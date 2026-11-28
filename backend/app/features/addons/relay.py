"""
Add-on relay: how an agent on a run uses its Composio add-ons without
holding any of their keys. Each run gets one Composio session, made the
first time it's needed, for the studio's Composio user: started from the
owner's saved policy in Composio (COMPOSIO_POLICY) when there is one, else
limited to the run's toolkits, with each add-on's account pinned. Composio
applies the owner's policy (risky tools, approvals) to every call.

Before that, the studio checks the tool belongs to one of the run's add-ons
(its token names them, and its agent still has them) and that the agent is
under its hourly limit. A refused call never leaves the studio.
Used by addons/routes.py and agent_server/addon_tools.py.
"""

import threading
import time
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.auth.agent_write_limit import record_agent_addon_call
from app.auth.viewer import Viewer
from app.config import settings
from app.features.addons import service as addons_service
from app.features.addons.models import Addon, ComposioSession
from app.features.addons.schemas import AddonCallResult, AddonTool
from app.features.agents import service as agents_service
from app.integrations import composio_client
from app.integrations.composio_client import ComposioError, ComposioRefusedError

# A session's tool list is read again after this long.
TOOLS_KEPT_SECONDS = 600
# Composio's own helper tools (search, connecting): never shown, never run here.
COMPOSIO_HELPERS = "COMPOSIO_"

_lock = threading.Lock()
_tools: dict[str, tuple[float, list[dict[str, Any]]]] = {}


class AddonRefusedError(Exception):
    """The call isn't allowed: by the studio before it's sent, or by Composio's policy."""


class AddonUnavailableError(Exception):
    """Composio isn't set up, couldn't be reached, or failed."""


def list_run_tools(db: Session, viewer: Viewer, query: str = "") -> list[AddonTool]:
    """The tools of the caller's run's Composio add-ons that Composio's policy allows.
    `query` keeps those whose name or description holds every word."""
    addons = _run_composio_addons(db, viewer)
    if not addons:
        return []
    by_toolkit = {addon.service: addon for addon in addons}
    words = query.lower().split()
    tools = []
    for tool in _session_tools(_session_for(db, viewer.run_id, addons)):
        addon = by_toolkit.get((tool.get("toolkit") or {}).get("slug", ""))
        text = f"{tool['slug']} {tool.get('description', '')}".lower()
        if addon is None or tool["slug"].startswith(COMPOSIO_HELPERS) or not all(word in text for word in words):
            continue
        tools.append(AddonTool(
            tool=tool["slug"],
            addon=addon.name,
            description=tool.get("description", ""),
            input_schema=tool.get("input_parameters") or {},
        ))
    return tools


def call_run_tool(db: Session, viewer: Viewer, tool: str, arguments: dict[str, Any]) -> AddonCallResult:
    """Check the call, then run it in the run's Composio session."""
    addons = _run_composio_addons(db, viewer)
    if tool.startswith(COMPOSIO_HELPERS) or not any(tool.startswith(f"{addon.service.upper()}_") for addon in addons):
        raise AddonRefusedError(f"{tool} isn't a tool of this run's add-ons (list_addon_tools shows them)")
    if not record_agent_addon_call(viewer.agent_name):
        raise AddonRefusedError("Hourly add-on call limit reached for this agent")
    session_id = _session_for(db, viewer.run_id, addons)
    try:
        reply = composio_client.run_in_session(session_id, tool, arguments)
    except ComposioRefusedError as error:
        raise AddonRefusedError(str(error)) from error
    except ComposioError as error:
        raise AddonUnavailableError(str(error)) from error
    error = reply.get("error")
    return AddonCallResult(
        tool=tool, successful=not error and reply.get("result_type", "completed") == "completed", data=reply.get("data"), error=error
    )


def _run_composio_addons(db: Session, viewer: Viewer) -> list[Addon]:
    """The run's Composio add-ons: named in its token, still the agent's, still defined."""
    if not viewer.is_run:
        raise AddonRefusedError("Add-on tools need a live run token (the one from your run's kit)")
    agent = agents_service.get_agent(db, viewer.agent_name)
    names = [name for name in (agent.addons if agent else []) if viewer.run_allows_addon(name)]
    return [addon for addon in addons_service.find_addons(db, names) if addon.kind == "composio"]


def _session_for(db: Session, run_id: str, addons: list[Addon]) -> str:
    """The run's Composio session, made now if it has none yet."""
    saved = db.get(ComposioSession, run_id)
    if saved is not None:
        return saved.session_id
    accounts = {addon.service: addon.account for addon in addons if addon.account}
    try:
        session_id = composio_client.create_session(
            settings.composio_user_id, [addon.service for addon in addons], accounts, settings.composio_policy
        )
    except ComposioError as error:
        raise AddonUnavailableError(str(error)) from error
    db.add(ComposioSession(run_id=run_id, session_id=session_id))
    try:
        db.commit()
    except IntegrityError:
        # Another call made it first: use that one.
        db.rollback()
        return db.get(ComposioSession, run_id).session_id
    return session_id


def _session_tools(session_id: str) -> list[dict[str, Any]]:
    now = time.monotonic()
    with _lock:
        kept = _tools.get(session_id)
    if kept and now - kept[0] < TOOLS_KEPT_SECONDS:
        return kept[1]
    try:
        tools = composio_client.list_session_tools(session_id)
    except ComposioError as error:
        raise AddonUnavailableError(str(error)) from error
    with _lock:
        _tools[session_id] = (now, tools)
    return tools


def forget_session_tools() -> None:
    """Ask Composio afresh next time (tests)."""
    with _lock:
        _tools.clear()
