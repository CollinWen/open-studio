"""
Composio client: runs one tool of an outside service (GitHub, Exa, ...) as
one of the studio's connected accounts, and reads tools' details (what each
does, its input schema, its current version), over Composio's REST API with
the studio's project key (COMPOSIO_API_KEY, sent as x-api-key).

Knows nothing about agents or runs: features/toolkits/service.py decides
what may be called, and this key never leaves the backend. Calls are never
retried: running a tool can change things (open an issue), and a silent
retry could do it twice.
"""

import ssl
from typing import Any

import httpx
import truststore

from app.config import settings

TIMEOUT_SECONDS = 60
# The most tools one listing asks for (Composio's own maximum is 1000).
LIST_LIMIT = 1000

# The operating system's certificates, as in openrouter_http.py.
_ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)


class ComposioError(Exception):
    """Composio isn't set up, couldn't be reached, or refused the request."""


def is_configured() -> bool:
    return bool(settings.composio_api_key)


def execute_tool(
    slug: str, arguments: dict[str, Any], user_id: str, connected_account_id: str = "", version: str = "latest"
) -> dict[str, Any]:
    """Run one tool. Composio's reply: {"successful": bool, "data": {...}, "error": str | None}."""
    body: dict[str, Any] = {"user_id": user_id, "arguments": arguments, "version": version}
    if connected_account_id:
        body["connected_account_id"] = connected_account_id
    return _request("POST", f"/api/v3.1/tools/execute/{slug}", json=body)


def fetch_tool_details(slugs: list[str]) -> dict[str, dict[str, Any]]:
    """Each tool's details by slug: name, description, input_parameters (a JSON schema), version."""
    if not slugs:
        return {}
    reply = _request("GET", "/api/v3.1/tools", params={"tool_slugs": ",".join(slugs), "limit": LIST_LIMIT})
    return {item["slug"]: item for item in reply.get("items", [])}


def list_toolkit_tools(toolkit: str, query: str = "") -> list[dict[str, Any]]:
    """Every tool of one toolkit (e.g. "github"), optionally narrowed by words."""
    params: dict[str, Any] = {"toolkit_slug": toolkit, "limit": LIST_LIMIT}
    if query:
        params["query"] = query
    return _request("GET", "/api/v3.1/tools", params=params).get("items", [])


def _request(method: str, path: str, **options: Any) -> dict[str, Any]:
    if not is_configured():
        raise ComposioError("Toolkits are off: set COMPOSIO_API_KEY")
    url = f"{settings.composio_base_url.rstrip('/')}{path}"
    try:
        with httpx.Client(verify=_ssl_context, timeout=TIMEOUT_SECONDS) as http:
            response = http.request(method, url, headers={"x-api-key": settings.composio_api_key}, **options)
    except httpx.HTTPError as error:
        raise ComposioError(f"Couldn't reach Composio: {error}") from error
    if response.status_code >= 400:
        raise ComposioError(f"Composio answered {response.status_code}: {response.text[:300]}")
    return response.json()
