"""
Tests for the Composio client, against a stand-in transport (never the
network): running a tool posts its arguments, the user, the account and the
version to Composio's execute endpoint with the project key; tool details
come back by slug; an error reply or no key at all is a ComposioError.
"""

import json
from dataclasses import replace

import httpx
import pytest

from app.integrations import composio_client

REAL_CLIENT = httpx.Client


@pytest.fixture
def composio(monkeypatch):
    """Route the client's requests to `handler`, with a key and a made-up address."""
    seen: list[httpx.Request] = []
    replies: dict[str, httpx.Response] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return replies.get(request.url.path, httpx.Response(404, text="no such route"))

    monkeypatch.setattr(composio_client, "settings", replace(
        composio_client.settings, composio_api_key="test-key", composio_base_url="https://composio.test"))
    monkeypatch.setattr(composio_client.httpx, "Client",
                        lambda **options: REAL_CLIENT(transport=httpx.MockTransport(handler), timeout=options.get("timeout")))
    return seen, replies


def test_running_a_tool_sends_the_account_the_version_and_the_key(composio):
    seen, replies = composio
    replies["/api/v3.1/tools/execute/GITHUB_CREATE_AN_ISSUE"] = httpx.Response(
        200, json={"successful": True, "data": {"number": 7}, "error": None, "log_id": "log_1"})
    reply = composio_client.execute_tool("GITHUB_CREATE_AN_ISSUE", {"title": "t"}, "open-studio", "ca_bot", "20251101_00")
    assert reply["data"] == {"number": 7}
    request = seen[0]
    assert request.method == "POST" and request.headers["x-api-key"] == "test-key"
    assert json.loads(request.content) == {
        "user_id": "open-studio", "arguments": {"title": "t"}, "version": "20251101_00", "connected_account_id": "ca_bot"}


def test_no_account_leaves_it_to_composio(composio):
    seen, replies = composio
    replies["/api/v3.1/tools/execute/EXA_SEARCH"] = httpx.Response(200, json={"successful": True, "data": {}})
    composio_client.execute_tool("EXA_SEARCH", {"query": "q"}, "open-studio")
    assert "connected_account_id" not in json.loads(seen[0].content)


def test_tool_details_come_back_by_slug(composio):
    seen, replies = composio
    replies["/api/v3.1/tools"] = httpx.Response(200, json={"items": [
        {"slug": "EXA_SEARCH", "description": "Search", "version": "20251020_01", "input_parameters": {"properties": {}}}]})
    details = composio_client.fetch_tool_details(["EXA_SEARCH", "EXA_ANSWER"])
    assert set(details) == {"EXA_SEARCH"} and details["EXA_SEARCH"]["version"] == "20251020_01"
    assert seen[0].url.params["tool_slugs"] == "EXA_SEARCH,EXA_ANSWER"


def test_an_error_reply_or_no_key_is_a_composio_error(composio, monkeypatch):
    seen, replies = composio
    replies["/api/v3.1/tools/execute/EXA_SEARCH"] = httpx.Response(401, text="bad key")
    with pytest.raises(composio_client.ComposioError, match="401"):
        composio_client.execute_tool("EXA_SEARCH", {}, "open-studio")
    monkeypatch.setattr(composio_client, "settings", replace(composio_client.settings, composio_api_key=""))
    with pytest.raises(composio_client.ComposioError, match="COMPOSIO_API_KEY"):
        composio_client.execute_tool("EXA_SEARCH", {}, "open-studio")
