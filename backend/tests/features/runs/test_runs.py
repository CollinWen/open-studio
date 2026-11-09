"""
Tests for runs: the owner starts a run and gets a kit (token, MCP address,
prompt, command); the run's token adds only to its own board, records the
run on what it adds, can't edit or link entries on other boards, and stops working when the run is finished or its agent
paused; a run can't be given outside tools the agent wasn't granted; an
agent can start runs only for itself, and a run token can't start more.
"""

import uuid

from conftest import AGENT_BOARD, OWNER_HEADERS, SCOUT_HEADERS


def _add_agent(client, tools: list[str] | None = None) -> tuple[str, dict]:
    name = f"r-{uuid.uuid4().hex[:8]}"
    body = {"name": name, "boards": [AGENT_BOARD, "second"], "tools": tools or []}
    response = client.post("/api/agents", json=body, headers=OWNER_HEADERS)
    assert response.status_code == 200, response.text
    return name, {"Authorization": f"Bearer {response.json()['token']}"}


def _start(client, agent: str, headers=OWNER_HEADERS, **fields):
    body = {"agent": agent, "kind": "study", "board": AGENT_BOARD, "brief": "look at this", **fields}
    return client.post("/api/runs", json=body, headers=headers)


def _bearer(kit: dict) -> dict:
    return {"Authorization": f"Bearer {kit['token']}"}


def _entry(board: str = AGENT_BOARD) -> dict:
    return {"board": board, "title": f"t {uuid.uuid4().hex}", "description": "why"}


def _second_board(client):
    client.post("/api/boards", json={"slug": "second", "name": "Second"}, headers=OWNER_HEADERS)


def test_the_owner_starts_a_run_and_gets_a_kit(client):
    _second_board(client)
    name, _ = _add_agent(client, tools=["web"])
    response = _start(client, name)
    assert response.status_code == 200, response.text
    kit = response.json()
    assert kit["token"].startswith("run.")
    assert kit["mcp_url"].endswith("/mcp")
    assert kit["run"]["scopes"] == [f"board:{AGENT_BOARD}", "web"]
    assert kit["run"]["state"] == "running"
    assert "look at this" in kit["prompt"]
    assert "WebFetch" in kit["allowed_tools"]
    assert kit["claude_command"].startswith("claude -p ")


def test_a_run_adds_only_to_its_board_and_is_recorded(client):
    _second_board(client)
    name, _ = _add_agent(client, tools=["web"])
    kit = _start(client, name).json()
    added = client.post("/api/entries", json=_entry(), headers=_bearer(kit))
    assert added.status_code == 200, added.text
    assert added.json()["added_by"] == f"agent:{name}"
    other_board = client.post("/api/entries", json=_entry("second"), headers=_bearer(kit))
    assert other_board.status_code == 403

    run = client.get(f"/api/runs/{kit['run']['id']}", headers=OWNER_HEADERS).json()
    assert run["added"] == [added.json()["id"]]


def test_finishing_a_run_ends_its_token(client):
    name, _ = _add_agent(client, tools=["web"])
    kit = _start(client, name).json()
    finished = client.post(f"/api/runs/{kit['run']['id']}/finish", json={"summary": "done"}, headers=_bearer(kit))
    assert finished.json()["state"] == "finished"
    assert finished.json()["summary"] == "done"
    assert client.post("/api/entries", json=_entry(), headers=_bearer(kit)).status_code == 401


def test_pausing_the_agent_stops_its_runs(client):
    name, _ = _add_agent(client, tools=["web"])
    kit = _start(client, name).json()
    client.patch(f"/api/agents/{name}", json={"active": False}, headers=OWNER_HEADERS)
    assert client.post("/api/entries", json=_entry(), headers=_bearer(kit)).status_code == 401


def test_a_run_gets_only_tools_the_agent_was_granted(client):
    name, _ = _add_agent(client, tools=["web"])
    refused = _start(client, name, kind="prototype")
    assert refused.status_code == 403
    assert "code" in refused.json()["detail"]
    narrowed = _start(client, name, kind="prototype", tools=["web"])
    assert narrowed.json()["run"]["tools"] == ["web"]


def test_a_run_cannot_last_longer_than_allowed(client):
    name, _ = _add_agent(client, tools=["web"])
    assert _start(client, name, hours=1000).status_code == 403


def test_an_agent_starts_runs_only_for_itself(client):
    name, headers = _add_agent(client, tools=["web"])
    assert _start(client, name, headers=headers).status_code == 200
    assert _start(client, "scout", headers=headers).status_code == 403
    assert _start(client, name, headers=SCOUT_HEADERS).status_code == 403


def test_a_run_token_cannot_start_more_runs(client):
    name, _ = _add_agent(client, tools=["web"])
    kit = _start(client, name).json()
    assert _start(client, name, headers=_bearer(kit)).status_code == 403


def test_a_run_cannot_start_from_a_private_entry(client):
    name, _ = _add_agent(client, tools=["web"])
    private = client.post("/api/entries", json={**_entry("home"), "visibility": "private"}, headers=OWNER_HEADERS)
    assert _start(client, name, entry_id=private.json()["id"]).status_code == 403


def test_only_the_owner_lists_runs_and_others_cannot_see_one(client):
    name, _ = _add_agent(client, tools=["web"])
    kit = _start(client, name).json()
    assert client.get("/api/runs").status_code == 401
    assert client.get(f"/api/runs/{kit['run']['id']}", headers=SCOUT_HEADERS).status_code == 404
    listed = client.get("/api/runs", params={"agent": name}, headers=OWNER_HEADERS).json()
    assert [run["id"] for run in listed] == [kit["run"]["id"]]



def _entries_on_two_boards(client) -> tuple[dict, dict, dict]:
    """A run on AGENT_BOARD, an agent entry on that board, and one on "second"."""
    _second_board(client)
    name, agent_headers = _add_agent(client, tools=["web"])
    mine = client.post("/api/entries", json=_entry(), headers=agent_headers).json()
    elsewhere = client.post("/api/entries", json=_entry("second"), headers=agent_headers).json()
    return _start(client, name).json(), mine, elsewhere


def test_a_run_cannot_edit_or_link_entries_on_other_boards(client):
    kit, mine, elsewhere = _entries_on_two_boards(client)
    edit = client.patch(f"/api/entries/{elsewhere['id']}", json={"title": "x"}, headers=_bearer(kit))
    assert edit.status_code == 403
    link = {"builds_on_id": mine["id"], "note": "n"}
    assert client.post(f"/api/entries/{elsewhere['id']}/builds-on", json=link, headers=_bearer(kit)).status_code == 403


def test_a_run_has_full_use_of_its_own_board(client):
    kit, mine, elsewhere = _entries_on_two_boards(client)
    assert client.patch(f"/api/entries/{mine['id']}", json={"title": "y"}, headers=_bearer(kit)).status_code == 200
    # Its entries may point at entries on other boards; only changing those is out of reach.
    back = {"builds_on_id": elsewhere["id"], "note": "n"}
    assert client.post(f"/api/entries/{mine['id']}/builds-on", json=back, headers=_bearer(kit)).status_code == 200
    assert client.get(f"/api/entries/{elsewhere['id']}", headers=_bearer(kit)).status_code == 200
