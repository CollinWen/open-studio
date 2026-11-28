"""
Composio client: Composio's REST API, with the studio's project key
(COMPOSIO_API_KEY, sent as x-api-key). It makes sessions (one per run, so
Composio applies the owner's policy to every call), lists and runs a
session's tools, asks for a Connect Link (Composio's own sign-in page for
a toolkit), reads a connected account, and lists a toolkit's tools.

Knows nothing about agents, runs or add-ons: features/addons/ decides what
may be called, and this key never leaves the backend. Running a tool is
never retried: it can change things (send an email), and a silent retry
could do it twice.
"""

import ssl
from typing import Any

import httpx
import truststore

from app.config import settings

TIMEOUT_SECONDS = 60
# Composio's largest page of tools, and the most pages read for one session.
PAGE_LIMIT = 500
MAX_PAGES = 4
SESSION_PATH = "/api/v3.1/tool_router/session"

# The operating system's certificates, as in openrouter_http.py.
_ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)


class ComposioError(Exception):
    """Composio isn't set up, couldn't be reached, or failed."""


class ComposioRefusedError(ComposioError):
    """Composio said no: a tool its policy blocks, or a request it won't take."""


def is_configured() -> bool:
    return bool(settings.composio_api_key)


def create_session(user_id: str, toolkits: list[str], accounts: dict[str, str], policy: str = "") -> str:
    """A session with only app tools, run directly (no search, sandbox or connecting). Its tools
    come from the saved policy `policy` ("sc_...") when given, else from `toolkits`; `accounts`
    pins the connected account each toolkit acts as."""
    body: dict[str, Any] = {
        "user_id": user_id,
        "manage_connections": {"enable": False},
        "workbench": {"enable": False},
        "search": {"enable": False},
        "execute": {"enable_multi_execute": False},
        "preload": {"tools": "all"},
    }
    if policy:
        body["experimental"] = {"session_config_id": policy}
    else:
        body["toolkits"] = {"enable": toolkits}
    if accounts:
        body["connected_accounts"] = {toolkit: [account] for toolkit, account in accounts.items()}
    return _request("POST", SESSION_PATH, json=body)["session_id"]


def list_session_tools(session_id: str) -> list[dict[str, Any]]:
    """The tools a session allows: slug, toolkit, description, input_parameters, tags."""
    tools: list[dict[str, Any]] = []
    params: dict[str, Any] = {"limit": PAGE_LIMIT}
    for _ in range(MAX_PAGES):
        reply = _request("GET", f"{SESSION_PATH}/{session_id}/tools", params=params)
        tools += reply.get("items", [])
        if not reply.get("next_cursor"):
            break
        params["cursor"] = reply["next_cursor"]
    return tools


def run_in_session(session_id: str, tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Run one tool. Composio's reply: {"data": {...}, "error": str | None, "result_type": ...}."""
    return _request("POST", f"{SESSION_PATH}/{session_id}/execute", json={"tool_slug": tool, "arguments": arguments})


def create_connect_link(user_id: str, toolkit: str, callback_url: str) -> str:
    """Composio's sign-in page for this toolkit; afterwards it sends the browser to callback_url
    with ?status=success&connected_account_id=ca_..."""
    session_id = _request("POST", SESSION_PATH, json={"user_id": user_id, "toolkits": {"enable": [toolkit]}})["session_id"]
    link = _request("POST", f"{SESSION_PATH}/{session_id}/link", json={"toolkit": toolkit, "callback_url": callback_url})
    return link["redirect_url"]


def get_connected_account(account_id: str) -> dict[str, Any]:
    """One connected account: id, status, user_id, toolkit {slug}."""
    return _request("GET", f"/api/v3.1/connected_accounts/{account_id}")


def list_toolkit_tools(toolkit: str, query: str = "") -> list[dict[str, Any]]:
    """Every tool of one toolkit (e.g. "gmail"), optionally narrowed by words."""
    params: dict[str, Any] = {"toolkit_slug": toolkit, "limit": 1000}
    if query:
        params["query"] = query
    return _request("GET", "/api/v3.1/tools", params=params).get("items", [])


def _request(method: str, path: str, **options: Any) -> dict[str, Any]:
    if not is_configured():
        raise ComposioError("Composio isn't set up: set COMPOSIO_API_KEY")
    url = f"{settings.composio_base_url.rstrip('/')}{path}"
    try:
        with httpx.Client(verify=_ssl_context, timeout=TIMEOUT_SECONDS) as http:
            response = http.request(method, url, headers={"x-api-key": settings.composio_api_key}, **options)
    except httpx.HTTPError as error:
        raise ComposioError(f"Couldn't reach Composio: {error}") from error
    if response.status_code in (400, 403, 422):
        raise ComposioRefusedError(f"Composio refused it: {_message(response)}")
    if response.status_code >= 400:
        raise ComposioError(f"Composio answered {response.status_code}: {_message(response)}")
    return response.json()


def _message(response: httpx.Response) -> str:
    """Composio's own explanation, e.g. "[Session Restriction] Tool ... is not enabled"."""
    try:
        error = response.json().get("error")
    except ValueError:
        return response.text[:300]
    if isinstance(error, dict) and error.get("message"):
        return str(error["message"])
    return str(error or response.text)[:300]
