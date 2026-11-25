"""
Toolkit relay: lets an agent on a run use the tools of outside services
(GitHub, Exa, ...) without holding any of their keys. The agent asks the
studio, the studio checks the call, then runs it on Composio with the
studio's key, as the account the owner chose for that agent. Every call is
checked, in order:
  - the token is a live run's, and its scopes name the toolkit
  - the agent is granted that tool now (a change on the agents page applies at once)
  - every pinned argument holds (pinned_arguments.py)
  - the agent is under its hourly toolkit calls (AGENT_TOOLKIT_CALLS_PER_HOUR)
Anything refused never leaves the studio.

Tools' details from Composio (description, input schema, version) are kept
for an hour, and a call runs the version its agent was shown.
Used by toolkits/routes.py and agent_server/toolkit_tools.py. Composio itself
is in integrations/composio_client.py.
"""

import threading
import time
from typing import Any

from sqlmodel import Session

from app.auth.agent_write_limit import record_agent_toolkit_call
from app.auth.viewer import Viewer
from app.config import settings
from app.features.agents import service as agents_service
from app.features.agents.models import Agent
from app.features.toolkits.pinned_arguments import PinnedArgumentError, check_pinned_arguments
from app.features.toolkits.schemas import CatalogTool, ToolkitCallResult, ToolkitGrant, ToolkitTool
from app.integrations import composio_client
from app.integrations.composio_client import ComposioError

DETAILS_KEPT_SECONDS = 3600

_details_lock = threading.Lock()
_details: dict[str, tuple[float, dict[str, Any]]] = {}


class ToolkitRefusedError(Exception):
    """The call isn't allowed; nothing was sent."""


class ToolkitUnavailableError(Exception):
    """Composio isn't set up, or couldn't run the tool."""


def list_run_tools(db: Session, viewer: Viewer) -> list[ToolkitTool]:
    """The toolkit tools the caller's run may call, with what each takes and its pins."""
    granted = _granted_tools(viewer, _agent_of(db, viewer))
    details = _tool_details([tool for _, tool, _ in granted])
    return [
        ToolkitTool(
            tool=tool,
            toolkit=toolkit,
            description=details.get(tool, {}).get("description", ""),
            input_schema=details.get(tool, {}).get("input_parameters") or {},
            pins=grant.pins,
        )
        for toolkit, tool, grant in granted
    ]


def call_run_tool(db: Session, viewer: Viewer, tool: str, arguments: dict[str, Any]) -> ToolkitCallResult:
    """Check the call, then run it on Composio as the grant's account."""
    granted = _granted_tools(viewer, _agent_of(db, viewer))
    grant = next((grant for _, name, grant in granted if name == tool), None)
    if grant is None:
        raise ToolkitRefusedError(f"{tool} isn't one of this run's toolkit tools (list_toolkit_tools shows them)")
    detail = _tool_details([tool]).get(tool, {})
    try:
        check_pinned_arguments(grant.pins, arguments, detail.get("input_parameters"))
    except PinnedArgumentError as error:
        raise ToolkitRefusedError(str(error)) from error
    if not record_agent_toolkit_call(viewer.agent_name):
        raise ToolkitRefusedError("Hourly toolkit call limit reached for this agent")
    try:
        reply = composio_client.execute_tool(
            tool, arguments, settings.composio_user_id, grant.connected_account, detail.get("version") or "latest"
        )
    except ComposioError as error:
        raise ToolkitUnavailableError(str(error)) from error
    return ToolkitCallResult(
        tool=tool, successful=bool(reply.get("successful")), data=reply.get("data"), error=reply.get("error")
    )


def list_catalog(toolkit: str, query: str = "") -> list[CatalogTool]:
    """Every tool of a toolkit on Composio, for the owner picking an agent's tools."""
    try:
        items = composio_client.list_toolkit_tools(toolkit, query)
    except ComposioError as error:
        raise ToolkitUnavailableError(str(error)) from error
    return [
        CatalogTool(
            tool=item["slug"],
            name=item.get("name", ""),
            description=item.get("description", ""),
            tags=item.get("tags") or [],
        )
        for item in items
    ]


def _agent_of(db: Session, viewer: Viewer) -> Agent:
    if not viewer.is_run:
        raise ToolkitRefusedError("Toolkit tools need a live run token (the one from your run's kit)")
    agent = agents_service.get_agent(db, viewer.agent_name)
    if agent is None:
        raise ToolkitRefusedError(f"No agent {viewer.agent_name}")
    return agent


def _granted_tools(viewer: Viewer, agent: Agent) -> list[tuple[str, str, ToolkitGrant]]:
    """(toolkit, tool, grant) for every tool the agent is granted in a toolkit its run may use."""
    granted = []
    for toolkit, saved in (agent.toolkits or {}).items():
        if viewer.run_allows_toolkit(toolkit):
            grant = ToolkitGrant.model_validate(saved)
            granted += [(toolkit, tool, grant) for tool in grant.tools]
    return granted


def _tool_details(tools: list[str]) -> dict[str, dict[str, Any]]:
    """What Composio says about each tool, from the last hour's answers where it can. Tools it
    can't describe now (not set up, unreachable) are left out, and calls still work."""
    now = time.monotonic()
    with _details_lock:
        known = {tool: detail for tool, (at, detail) in _details.items() if tool in tools and now - at < DETAILS_KEPT_SECONDS}
    missing = [tool for tool in tools if tool not in known]
    if missing and composio_client.is_configured():
        try:
            fetched = composio_client.fetch_tool_details(missing)
        except ComposioError:
            fetched = {}
        with _details_lock:
            for tool, detail in fetched.items():
                _details[tool] = (now, detail)
        known.update(fetched)
    return known


def forget_tool_details() -> None:
    """Ask Composio afresh next time (tests)."""
    with _details_lock:
        _details.clear()
