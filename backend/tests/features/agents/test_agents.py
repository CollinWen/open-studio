"""
Tests for agents: agents named in AGENT_TOKENS are in the studio on startup,
only the owner adds, pauses, re-keys and removes agents, a new agent's token
works at once and is never listed, a paused agent is treated as a visitor,
a new token replaces the old one, and removing an agent takes it off its boards.
"""

import uuid

from conftest import AGENT_BOARD, OWNER_HEADERS, SCOUT_HEADERS


def _add_agent(client, boards: list[str] | None = None) -> tuple[str, dict]:
    name = f"a-{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/api/agents", json={"name": name, "boards": boards or [AGENT_BOARD]}, headers=OWNER_HEADERS
    )
    assert response.status_code == 200, response.text
    return name, {"Authorization": f"Bearer {response.json()['token']}"}


def _entry(board: str = AGENT_BOARD) -> dict:
    return {"board": board, "title": f"t {uuid.uuid4().hex}", "description": "why"}


def test_agents_from_settings_are_listed(client):
    names = {agent["name"] for agent in client.get("/api/agents").json()}
    assert {"scout", "archivist"} <= names


def test_only_the_owner_adds_agents(client):
    response = client.post("/api/agents", json={"name": "sneaky"}, headers=SCOUT_HEADERS)
    assert response.status_code == 401


def test_a_new_agent_can_write_and_its_token_is_never_listed(client):
    name, headers = _add_agent(client)
    added = client.post("/api/entries", json=_entry(), headers=headers)
    assert added.json()["added_by"] == f"agent:{name}"

    listed = client.get(f"/api/agents/{name}").json()
    assert listed["boards"] == [AGENT_BOARD]
    assert "token" not in listed and "token_hash" not in listed
    assert listed["last_seen_at"] is not None


def test_a_paused_agent_cannot_write(client):
    name, headers = _add_agent(client)
    client.patch(f"/api/agents/{name}", json={"active": False}, headers=OWNER_HEADERS)
    assert client.post("/api/entries", json=_entry(), headers=headers).status_code == 401


def test_a_new_token_replaces_the_old_one(client):
    name, old_headers = _add_agent(client)
    token = client.post(f"/api/agents/{name}/token", headers=OWNER_HEADERS).json()["token"]
    assert client.post("/api/entries", json=_entry(), headers=old_headers).status_code == 401
    new_headers = {"Authorization": f"Bearer {token}"}
    assert client.post("/api/entries", json=_entry(), headers=new_headers).status_code == 200


def test_removing_an_agent_takes_it_off_its_boards(client):
    name, headers = _add_agent(client)
    assert client.delete(f"/api/agents/{name}", headers=OWNER_HEADERS).status_code == 204
    assert client.get(f"/api/agents/{name}").status_code == 404
    assert name not in client.get(f"/api/boards/{AGENT_BOARD}").json()["agents"]
    assert client.post("/api/entries", json=_entry(), headers=headers).status_code == 401
