"""
Tests for the toolkit relay, with a stand-in for Composio (tests never call
it): the owner grants an agent a toolkit's tools, an account and pinned
arguments (tools must belong to their toolkit), and only the owner sees
grants; a run gets all its agent's toolkits unless it asks for fewer, and
never one the agent lacks; an agent on a run lists its toolkit tools (with
descriptions, schemas and pins) and calls them, which runs them on Composio
as the grant's account at the version it was shown; a tool not granted, a
toolkit the run left out, a pin broken, a grant taken back mid-run, a token
that isn't a run's, or the hourly limit all refuse before anything is sent;
Composio being off says so; the same works over MCP; and the owner can
browse a toolkit's catalog.
"""

import uuid
from dataclasses import replace

import pytest

from conftest import AGENT_BOARD, OWNER_HEADERS, SCOUT_HEADERS

from app.auth import agent_write_limit
from app.features.toolkits import service as toolkits_service
from app.integrations import composio_client

REAL_EXECUTE_TOOL = composio_client.execute_tool
MCP_HEADERS = {"Accept": "application/json, text/event-stream", "MCP-Protocol-Version": "2025-06-18"}
GITHUB = {
    "tools": ["GITHUB_GET_A_REPOSITORY", "GITHUB_CREATE_AN_ISSUE"],
    "connected_account": "ca_bot",
    "pins": {"owner": ["CollinWen"], "repo": ["open-studio"]},
}
EXA = {"tools": ["EXA_SEARCH"]}
DETAILS = {
    "GITHUB_GET_A_REPOSITORY": {"slug": "GITHUB_GET_A_REPOSITORY", "description": "Get a repository", "version": "20251101_00",
                                "input_parameters": {"properties": {"owner": {}, "repo": {}}}},
    "GITHUB_CREATE_AN_ISSUE": {"slug": "GITHUB_CREATE_AN_ISSUE", "description": "Open an issue", "version": "20251101_00",
                               "input_parameters": {"properties": {"owner": {}, "repo": {}, "title": {}}}},
    "EXA_SEARCH": {"slug": "EXA_SEARCH", "description": "Search the web", "version": "20251020_01",
                   "input_parameters": {"properties": {"query": {}}}},
}


@pytest.fixture
def composio(monkeypatch):
    """A stand-in Composio: records each call and answers like the real one."""
    calls = []

    def execute_tool(slug, arguments, user_id, connected_account_id="", version="latest"):
        calls.append({"slug": slug, "arguments": arguments, "user_id": user_id,
                      "connected_account_id": connected_account_id, "version": version})
        return {"successful": True, "data": {"echo": arguments}, "error": None}

    monkeypatch.setattr(composio_client, "is_configured", lambda: True)
    monkeypatch.setattr(composio_client, "execute_tool", execute_tool)
    monkeypatch.setattr(composio_client, "fetch_tool_details", lambda slugs: {s: DETAILS[s] for s in slugs if s in DETAILS})
    monkeypatch.setattr(composio_client, "list_toolkit_tools", lambda toolkit, query="": [
        {"slug": "GITHUB_GET_A_REPOSITORY", "name": "Get a repository", "description": "Get one", "tags": ["readOnlyHint"]},
    ])
    toolkits_service.forget_tool_details()
    yield calls
    toolkits_service.forget_tool_details()


def _agent(client, toolkits) -> str:
    name = f"k-{uuid.uuid4().hex[:8]}"
    body = {"name": name, "boards": [AGENT_BOARD], "toolkits": toolkits}
    response = client.post("/api/agents", json=body, headers=OWNER_HEADERS)
    assert response.status_code == 200, response.text
    return name


def _run(client, agent, **fields) -> dict:
    response = client.post("/api/runs", json={"agent": agent, "boards": ["*"], **fields}, headers=OWNER_HEADERS)
    assert response.status_code == 200, response.text
    kit = response.json()
    return {"Authorization": f"Bearer {kit['token']}"} | {"kit": kit}


def _headers(run: dict) -> dict:
    return {"Authorization": run["Authorization"]}


def _call(client, run, tool, arguments):
    return client.post(f"/api/toolkits/tools/{tool}", json={"arguments": arguments}, headers=_headers(run))


def test_grants_are_checked_and_only_the_owner_sees_them(client):
    name = _agent(client, {"github": GITHUB})
    owners_view = client.get(f"/api/agents/{name}", headers=OWNER_HEADERS).json()
    assert owners_view["toolkits"]["github"]["pins"] == GITHUB["pins"]
    assert client.get(f"/api/agents/{name}").json()["toolkits"] == {}
    assert all(agent["toolkits"] == {} for agent in client.get("/api/agents").json())

    stray = {"github": {"tools": ["EXA_SEARCH"]}}
    assert client.post("/api/agents", json={"name": f"k-{uuid.uuid4().hex[:8]}", "toolkits": stray}, headers=OWNER_HEADERS).status_code == 422
    for bad in ({"tools": []}, {"tools": ["github_lowercase"]}, {"tools": ["GITHUB_X"], "pins": {"repo": []}}):
        response = client.patch(f"/api/agents/{name}", json={"toolkits": {"github": bad}}, headers=OWNER_HEADERS)
        assert response.status_code == 422, bad


def test_a_run_gets_its_agents_toolkits_unless_it_asks_for_fewer(client):
    name = _agent(client, {"github": GITHUB, "exa": EXA})
    every = _run(client, name)["kit"]["run"]
    assert every["toolkits"] == ["github", "exa"]
    assert {"toolkit:github", "toolkit:exa"} <= set(every["scopes"])
    assert "list_toolkit_tools" in _run(client, name)["kit"]["prompt"]

    fewer = _run(client, name, toolkits=["exa"])["kit"]["run"]
    assert fewer["toolkits"] == ["exa"] and "toolkit:github" not in fewer["scopes"]
    refused = client.post("/api/runs", json={"agent": name, "boards": ["*"], "toolkits": ["notion"]}, headers=OWNER_HEADERS)
    assert refused.status_code == 403 and "notion" in refused.json()["detail"]


def test_an_agent_lists_and_calls_its_toolkit_tools(client, composio):
    run = _run(client, _agent(client, {"github": GITHUB, "exa": EXA}))
    listed = client.get("/api/toolkits/tools", headers=_headers(run)).json()
    assert [tool["tool"] for tool in listed] == ["GITHUB_GET_A_REPOSITORY", "GITHUB_CREATE_AN_ISSUE", "EXA_SEARCH"]
    assert listed[1]["description"] == "Open an issue" and listed[1]["pins"] == GITHUB["pins"]
    assert "title" in listed[1]["input_schema"]["properties"]

    arguments = {"owner": "CollinWen", "repo": "open-studio", "title": "From an agent"}
    called = _call(client, run, "GITHUB_CREATE_AN_ISSUE", arguments)
    assert called.status_code == 200, called.text
    assert called.json() == {"tool": "GITHUB_CREATE_AN_ISSUE", "successful": True, "data": {"echo": arguments}, "error": None}
    assert composio == [{"slug": "GITHUB_CREATE_AN_ISSUE", "arguments": arguments, "user_id": "open-studio",
                         "connected_account_id": "ca_bot", "version": "20251101_00"}]


def test_calls_outside_the_grant_are_refused_before_anything_is_sent(client, composio):
    name = _agent(client, {"github": GITHUB, "exa": EXA})
    run = _run(client, name, toolkits=["github"])
    good = {"owner": "CollinWen", "repo": "open-studio"}

    assert _call(client, run, "GITHUB_DELETE_A_REPOSITORY", good).status_code == 403
    assert _call(client, run, "EXA_SEARCH", {"query": "folding"}).status_code == 403
    broken_pin = _call(client, run, "GITHUB_GET_A_REPOSITORY", {"owner": "CollinWen", "repo": "private-notes"})
    assert broken_pin.status_code == 403 and "open-studio" in broken_pin.json()["detail"]
    assert _call(client, run, "GITHUB_GET_A_REPOSITORY", {"owner": "CollinWen"}).status_code == 403
    assert _call(client, {"Authorization": OWNER_HEADERS["Authorization"]}, "GITHUB_GET_A_REPOSITORY", good).status_code == 403
    assert client.post("/api/toolkits/tools/GITHUB_GET_A_REPOSITORY", json={"arguments": good}).status_code == 403
    assert composio == []

    # Taking the tool back on the agents page reaches the live run at once.
    client.patch(f"/api/agents/{name}", json={"toolkits": {"github": {**GITHUB, "tools": ["GITHUB_CREATE_AN_ISSUE"]}}}, headers=OWNER_HEADERS)
    assert _call(client, run, "GITHUB_GET_A_REPOSITORY", good).status_code == 403
    assert composio == []


def test_the_hourly_limit_and_composio_being_off(client, composio, monkeypatch):
    run = _run(client, _agent(client, {"exa": EXA}))
    monkeypatch.setattr(agent_write_limit, "settings", replace(agent_write_limit.settings, agent_toolkit_calls_per_hour=2))
    assert [_call(client, run, "EXA_SEARCH", {"query": "q"}).status_code for _ in range(3)] == [200, 200, 403]

    # With no key, the real client refuses, and the agent is told why.
    agent_write_limit.forget_agent_writes()
    monkeypatch.setattr(composio_client, "is_configured", lambda: False)
    monkeypatch.setattr(composio_client, "execute_tool", REAL_EXECUTE_TOOL)
    off = _call(client, run, "EXA_SEARCH", {"query": "q"})
    assert off.status_code == 503 and "COMPOSIO_API_KEY" in off.json()["detail"]


def test_the_same_over_mcp(running_client, composio):
    run = _run(running_client, _agent(running_client, {"exa": EXA}))

    def tool(name, arguments, headers):
        body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}}
        return running_client.post("/mcp", json=body, headers={**MCP_HEADERS, **headers}).json()["result"]

    listed = tool("list_toolkit_tools", {}, _headers(run))
    assert [item["tool"] for item in listed["structuredContent"]["result"]] == ["EXA_SEARCH"]
    called = tool("call_toolkit_tool", {"tool": "EXA_SEARCH", "arguments": {"query": "folding"}}, _headers(run))
    assert not called["isError"] and called["structuredContent"]["successful"]
    refused = tool("call_toolkit_tool", {"tool": "GITHUB_GET_A_REPOSITORY", "arguments": {}}, _headers(run))
    assert refused["isError"]
    assert tool("list_toolkit_tools", {}, SCOUT_HEADERS)["structuredContent"]["result"] == []


def test_the_owner_browses_a_toolkits_catalog(client, composio):
    assert client.get("/api/toolkits/github/catalog").status_code == 401
    catalog = client.get("/api/toolkits/github/catalog", headers=OWNER_HEADERS).json()
    assert catalog == [{"tool": "GITHUB_GET_A_REPOSITORY", "name": "Get a repository", "description": "Get one", "tags": ["readOnlyHint"]}]
    assert client.get("/api/toolkits/Not-A-Toolkit/catalog", headers=OWNER_HEADERS).status_code == 422
