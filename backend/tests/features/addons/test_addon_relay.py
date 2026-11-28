"""
Tests for the add-on relay (an agent's side), with a stand-in for Composio:
a run lists the tools of its Composio add-ons, through one Composio session
made on first use (from the saved policy when there is one, each add-on's
account pinned), never Composio's own helper tools; it calls one in that
session; a tool of another toolkit, an add-on the run left out or the
agent lost, a token that isn't a run's, or the hourly limit all refuse
before anything is sent; Composio's own refusal reaches the agent in its
words; and the same works over MCP.
"""

import uuid
from dataclasses import replace

import pytest

from conftest import AGENT_BOARD, OWNER_HEADERS

from app.auth import agent_write_limit
from app.features.addons import relay
from app.integrations import composio_client

MCP_HEADERS = {"Accept": "application/json, text/event-stream", "MCP-Protocol-Version": "2025-06-18"}
TOOLS = [
    {"slug": "GMAIL_FETCH_EMAILS", "toolkit": {"slug": "gmail"}, "description": "Fetch recent emails", "input_parameters": {"properties": {"max": {}}}},
    {"slug": "GMAIL_CREATE_EMAIL_DRAFT", "toolkit": {"slug": "gmail"}, "description": "Draft an email", "input_parameters": {}},
    {"slug": "EXA_SEARCH", "toolkit": {"slug": "exa"}, "description": "Search the web", "input_parameters": {}},
    {"slug": "COMPOSIO_SEARCH_TOOLS", "toolkit": {"slug": "composio"}, "description": "Composio's own helper", "input_parameters": {}},
]


@pytest.fixture
def composio(monkeypatch):
    """A stand-in Composio: records sessions and calls, answers like the real one."""
    record = {"sessions": [], "calls": []}

    def create_session(user_id, toolkits, accounts, policy=""):
        record["sessions"].append({"user_id": user_id, "toolkits": toolkits, "accounts": accounts, "policy": policy})
        return f"sess_{len(record['sessions'])}"

    def run_in_session(session_id, tool, arguments):
        if tool == "GMAIL_SEND_EMAIL":
            raise composio_client.ComposioRefusedError("Composio refused it: [Session Restriction] not enabled")
        record["calls"].append({"session": session_id, "tool": tool, "arguments": arguments})
        return {"data": {"echo": arguments}, "error": None, "result_type": "completed"}

    monkeypatch.setattr(composio_client, "create_session", create_session)
    monkeypatch.setattr(composio_client, "list_session_tools", lambda session_id: TOOLS)
    monkeypatch.setattr(composio_client, "run_in_session", run_in_session)
    monkeypatch.setattr(composio_client, "get_connected_account", lambda account: {
        "id": account, "status": "ACTIVE", "user_id": "open-studio", "toolkit": {"slug": "gmail"}})
    relay.forget_session_tools()
    yield record
    relay.forget_session_tools()


def _setup(client, run_addons=None) -> tuple[dict, str, str, str]:
    """A mail add-on (connected) and a search add-on, an agent with both and web, and a run."""
    mail, search = f"mail-{uuid.uuid4().hex[:6]}", f"search-{uuid.uuid4().hex[:6]}"
    client.post("/api/addons", json={"name": mail, "kind": "composio", "service": "gmail"}, headers=OWNER_HEADERS)
    client.post("/api/addons", json={"name": search, "kind": "composio", "service": "exa"}, headers=OWNER_HEADERS)
    client.post(f"/api/addons/{mail}/connection", json={"connected_account_id": "ca_mail"}, headers=OWNER_HEADERS)
    agent = f"r-{uuid.uuid4().hex[:8]}"
    client.post("/api/agents", json={"name": agent, "boards": [AGENT_BOARD], "addons": ["web", mail, search]}, headers=OWNER_HEADERS)
    run = {"agent": agent, "boards": ["*"], **({"addons": run_addons(mail, search)} if run_addons else {})}
    kit = client.post("/api/runs", json=run, headers=OWNER_HEADERS).json()
    return {"Authorization": f"Bearer {kit['token']}"}, agent, mail, search


def _call(client, headers, tool, arguments):
    return client.post(f"/api/addon-tools/{tool}", json={"arguments": arguments}, headers=headers)


def test_a_run_lists_and_calls_its_add_ons_tools_in_one_session(client, composio):
    headers, _, mail, search = _setup(client)
    listed = client.get("/api/addon-tools", headers=headers).json()
    assert [(tool["tool"], tool["addon"]) for tool in listed] == [
        ("GMAIL_FETCH_EMAILS", mail), ("GMAIL_CREATE_EMAIL_DRAFT", mail), ("EXA_SEARCH", search)]
    assert [tool["tool"] for tool in client.get("/api/addon-tools?q=draft", headers=headers).json()] == ["GMAIL_CREATE_EMAIL_DRAFT"]

    called = _call(client, headers, "EXA_SEARCH", {"query": "folding"})
    assert called.json() == {"tool": "EXA_SEARCH", "successful": True, "data": {"echo": {"query": "folding"}}, "error": None}
    assert composio["sessions"] == [{"user_id": "open-studio", "toolkits": ["gmail", "exa"], "accounts": {"gmail": "ca_mail"}, "policy": ""}]
    assert composio["calls"] == [{"session": "sess_1", "tool": "EXA_SEARCH", "arguments": {"query": "folding"}}]


def test_the_saved_policy_starts_the_session(client, composio, monkeypatch):
    monkeypatch.setattr(relay, "settings", replace(relay.settings, composio_policy="sc_safe"))
    headers, *_ = _setup(client)
    _call(client, headers, "GMAIL_FETCH_EMAILS", {})
    assert composio["sessions"][0]["policy"] == "sc_safe"


def test_calls_outside_the_runs_add_ons_are_refused_before_anything_is_sent(client, composio):
    headers, agent, mail, search = _setup(client, run_addons=lambda mail, search: [mail])
    assert _call(client, headers, "EXA_SEARCH", {}).status_code == 403
    assert _call(client, headers, "SLACK_SEND_MESSAGE", {}).status_code == 403
    assert _call(client, headers, "COMPOSIO_SEARCH_TOOLS", {}).status_code == 403
    assert _call(client, {"Authorization": OWNER_HEADERS["Authorization"]}, "GMAIL_FETCH_EMAILS", {}).status_code == 403
    assert [tool["addon"] for tool in client.get("/api/addon-tools", headers=headers).json()] == [mail, mail]
    client.patch(f"/api/agents/{agent}", json={"addons": ["web"]}, headers=OWNER_HEADERS)
    assert _call(client, headers, "GMAIL_FETCH_EMAILS", {}).status_code == 403
    assert composio["calls"] == []


def test_composios_refusal_and_the_hourly_limit(client, composio, monkeypatch):
    headers, *_ = _setup(client)
    refused = _call(client, headers, "GMAIL_SEND_EMAIL", {})
    assert refused.status_code == 403 and "Session Restriction" in refused.json()["detail"]
    agent_write_limit.forget_agent_writes()
    monkeypatch.setattr(agent_write_limit, "settings", replace(agent_write_limit.settings, agent_addon_calls_per_hour=2))
    assert [_call(client, headers, "EXA_SEARCH", {}).status_code for _ in range(3)] == [200, 200, 403]


def test_the_same_over_mcp(running_client, composio):
    headers, *_ = _setup(running_client)

    def tool(name, arguments):
        body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}}
        return running_client.post("/mcp", json=body, headers={**MCP_HEADERS, **headers}).json()["result"]

    listed = tool("list_addon_tools", {"query": "search"})
    assert [item["tool"] for item in listed["structuredContent"]["result"]] == ["EXA_SEARCH"]
    called = tool("call_addon_tool", {"tool": "EXA_SEARCH", "arguments": {"query": "q"}})
    assert not called["isError"] and called["structuredContent"]["successful"]
    assert tool("call_addon_tool", {"tool": "SLACK_SEND_MESSAGE"})["isError"]
