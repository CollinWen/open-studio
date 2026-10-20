"""
Tests for the agent server (MCP at /mcp): the tools are listed, an agent can
add an entry and find it again, the same link is refused the second time,
visitors can read but not write, and agents can't edit the owner's entries.
"""

import uuid

from conftest import OWNER_HEADERS, SCOUT_HEADERS

MCP_HEADERS = {"Accept": "application/json, text/event-stream", "MCP-Protocol-Version": "2025-06-18"}


def _call(client, method: str, params: dict | None = None, headers: dict | None = None) -> dict:
    body = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
    response = client.post("/mcp", json=body, headers={**MCP_HEADERS, **(headers or {})})
    assert response.status_code == 200, response.text
    return response.json()["result"]


def _tool(client, name: str, arguments: dict, headers: dict | None = None) -> dict:
    return _call(client, "tools/call", {"name": name, "arguments": arguments}, headers)


def test_tools_are_listed(running_client):
    names = {tool["name"] for tool in _call(running_client, "tools/list")["tools"]}
    assert {"get_studio_interests", "search_studio", "add_entry", "update_entry"} <= names


def test_agent_adds_an_entry_and_finds_it(running_client):
    title = f"paper {uuid.uuid4().hex}"
    added = _tool(running_client, "add_entry", {"title": title, "description": "why", "tags": ["t"]}, SCOUT_HEADERS)
    assert not added["isError"]
    assert added["structuredContent"]["added_by"] == "agent:scout"
    assert added["structuredContent"]["visibility"] == "unlisted"

    found = _tool(running_client, "search_studio", {"query": title}, SCOUT_HEADERS)
    assert [entry["title"] for entry in found["structuredContent"]["result"]] == [title]


def test_the_same_link_is_refused(running_client):
    arguments = {"title": "x", "description": "y", "source_url": f"https://example.com/{uuid.uuid4().hex}"}
    assert not _tool(running_client, "add_entry", arguments, SCOUT_HEADERS)["isError"]
    again = _tool(running_client, "add_entry", arguments, SCOUT_HEADERS)
    assert again["isError"]
    assert "Already in the studio" in again["content"][0]["text"]


def test_visitors_can_read_but_not_write(running_client):
    assert not _tool(running_client, "get_studio_interests", {})["isError"]
    assert _tool(running_client, "add_entry", {"title": "x", "description": "y"})["isError"]


def test_agents_cannot_edit_owner_entries(running_client):
    owner_entry = running_client.post(
        "/api/entries", json={"title": "mine", "visibility": "public", "tags": ["t"]}, headers=OWNER_HEADERS
    ).json()
    edit = _tool(running_client, "update_entry", {"entry_id": owner_entry["id"], "title": "x"}, SCOUT_HEADERS)
    assert edit["isError"]
