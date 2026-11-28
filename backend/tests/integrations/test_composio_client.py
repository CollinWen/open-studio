"""
Tests for the Composio client, against a stand-in transport (never the
network): a run's session is made from the saved policy when there is one,
else from its toolkits, with only app tools and each account pinned; a
session's tools are read page by page; a tool runs in its session; a
Connect Link comes from a small session of its own; Composio's refusals
keep its own words, and other errors or no key at all are ComposioErrors.
"""

import json
from dataclasses import replace

import httpx
import pytest

from app.integrations import composio_client

REAL_CLIENT = httpx.Client
SESSIONS = "/api/v3.1/tool_router/session"


@pytest.fixture
def composio(monkeypatch):
    """Route the client's requests to the stand-in, with a key and a made-up address."""
    seen: list[httpx.Request] = []
    replies: dict[str, list[httpx.Response]] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        waiting = replies.get(request.url.path)
        return waiting.pop(0) if waiting else httpx.Response(404, text="no such route")

    monkeypatch.setattr(composio_client, "settings", replace(
        composio_client.settings, composio_api_key="test-key", composio_base_url="https://composio.test"))
    monkeypatch.setattr(composio_client.httpx, "Client",
                        lambda **options: REAL_CLIENT(transport=httpx.MockTransport(handler), timeout=options.get("timeout")))
    return seen, replies


def _body(request: httpx.Request) -> dict:
    return json.loads(request.content)


def test_a_session_comes_from_the_policy_or_the_toolkits(composio):
    seen, replies = composio
    replies[SESSIONS] = [httpx.Response(200, json={"session_id": "s1"}), httpx.Response(200, json={"session_id": "s2"})]
    assert composio_client.create_session("open-studio", ["gmail", "exa"], {"gmail": "ca_mail"}) == "s1"
    assert composio_client.create_session("open-studio", ["gmail"], {}, policy="sc_safe") == "s2"
    plain, from_policy = _body(seen[0]), _body(seen[1])
    assert seen[0].headers["x-api-key"] == "test-key"
    assert plain["toolkits"] == {"enable": ["gmail", "exa"]} and plain["connected_accounts"] == {"gmail": ["ca_mail"]}
    assert plain["search"] == {"enable": False} and plain["manage_connections"] == {"enable": False}
    assert from_policy["experimental"] == {"session_config_id": "sc_safe"} and "toolkits" not in from_policy


def test_a_sessions_tools_are_read_page_by_page_and_run_there(composio):
    seen, replies = composio
    replies[f"{SESSIONS}/s1/tools"] = [
        httpx.Response(200, json={"items": [{"slug": "GMAIL_FETCH_EMAILS"}], "next_cursor": "page2"}),
        httpx.Response(200, json={"items": [{"slug": "EXA_SEARCH"}], "next_cursor": None}),
    ]
    replies[f"{SESSIONS}/s1/execute"] = [httpx.Response(200, json={"data": {"n": 1}, "error": None, "result_type": "completed"})]
    assert [tool["slug"] for tool in composio_client.list_session_tools("s1")] == ["GMAIL_FETCH_EMAILS", "EXA_SEARCH"]
    assert seen[1].url.params["cursor"] == "page2"
    assert composio_client.run_in_session("s1", "EXA_SEARCH", {"query": "q"})["data"] == {"n": 1}
    assert _body(seen[2]) == {"tool_slug": "EXA_SEARCH", "arguments": {"query": "q"}}


def test_a_connect_link_comes_from_a_small_session_of_its_own(composio):
    seen, replies = composio
    replies[SESSIONS] = [httpx.Response(200, json={"session_id": "s9"})]
    replies[f"{SESSIONS}/s9/link"] = [httpx.Response(200, json={"redirect_url": "https://connect.composio.test/x", "connected_account_id": "ca_new", "link_token": "t"})]
    url = composio_client.create_connect_link("open-studio", "gmail", "http://localhost:5173/studio/addons?addon=email")
    assert url == "https://connect.composio.test/x"
    assert _body(seen[0]) == {"user_id": "open-studio", "toolkits": {"enable": ["gmail"]}}
    assert _body(seen[1]) == {"toolkit": "gmail", "callback_url": "http://localhost:5173/studio/addons?addon=email"}


def test_refusals_keep_composios_words_and_other_failures_are_errors(composio, monkeypatch):
    seen, replies = composio
    blocked = {"error": {"message": "[Session Restriction] Tool 'GMAIL_SEND_EMAIL' is not enabled", "code": 4310}}
    replies[f"{SESSIONS}/s1/execute"] = [httpx.Response(400, json=blocked), httpx.Response(500, text="oops")]
    with pytest.raises(composio_client.ComposioRefusedError, match="Session Restriction"):
        composio_client.run_in_session("s1", "GMAIL_SEND_EMAIL", {})
    with pytest.raises(composio_client.ComposioError, match="500"):
        composio_client.run_in_session("s1", "GMAIL_SEND_EMAIL", {})
    monkeypatch.setattr(composio_client, "settings", replace(composio_client.settings, composio_api_key=""))
    with pytest.raises(composio_client.ComposioError, match="COMPOSIO_API_KEY"):
        composio_client.list_session_tools("s1")
