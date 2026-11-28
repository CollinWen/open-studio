"""
Tests for agents: only the owner adds, changes, pauses and removes agents; a
new agent has no token of its own (the owner issues it one, as a run), and
none is ever listed; an agent's boards can be set in one change; a paused
agent's tokens are treated as a visitor's, and removing an agent takes it
off its boards and stops its tokens.
"""

import uuid

from conftest import AGENT_BOARD, OWNER_HEADERS, SCOUT_HEADERS, issue_token


def _add_agent(client, boards: list[str] | None = None) -> tuple[str, dict]:
    """A new agent, and a token issued for it on all its boards."""
    name = f"a-{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/api/agents", json={"name": name, "boards": boards or [AGENT_BOARD]}, headers=OWNER_HEADERS
    )
    assert response.status_code == 200, response.text
    assert "token" not in response.json()
    return name, issue_token(name)


def _entry(board: str = AGENT_BOARD) -> dict:
    return {"board": board, "title": f"t {uuid.uuid4().hex}", "description": "why"}


def test_the_test_agents_are_listed(client):
    names = {agent["name"] for agent in client.get("/api/agents").json()}
    assert {"scout", "archivist"} <= names


def test_only_the_owner_adds_agents(client):
    response = client.post("/api/agents", json={"name": "sneaky"}, headers=SCOUT_HEADERS)
    assert response.status_code == 401


def test_a_new_agent_writes_on_an_issued_token_and_no_token_is_listed(client):
    name, headers = _add_agent(client)
    added = client.post("/api/entries", json=_entry(), headers=headers)
    assert added.json()["added_by"] == f"agent:{name}"

    listed = client.get(f"/api/agents/{name}").json()
    assert listed["boards"] == [AGENT_BOARD]
    assert "token" not in listed and "token_hash" not in listed
    assert listed["last_seen_at"] is not None


def test_an_agents_boards_are_set_in_one_change(client):
    client.post("/api/boards", json={"slug": "second", "name": "Second"}, headers=OWNER_HEADERS)
    name, _ = _add_agent(client)
    changed = client.patch(f"/api/agents/{name}", json={"boards": ["second"]}, headers=OWNER_HEADERS)
    assert changed.json()["boards"] == ["second"]
    assert name not in client.get(f"/api/boards/{AGENT_BOARD}").json()["agents"]


def test_a_paused_agent_cannot_write(client):
    name, headers = _add_agent(client)
    client.patch(f"/api/agents/{name}", json={"active": False}, headers=OWNER_HEADERS)
    assert client.post("/api/entries", json=_entry(), headers=headers).status_code == 401


def test_removing_an_agent_takes_it_off_its_boards(client):
    name, headers = _add_agent(client)
    assert client.delete(f"/api/agents/{name}", headers=OWNER_HEADERS).status_code == 204
    assert client.get(f"/api/agents/{name}").status_code == 404
    assert name not in client.get(f"/api/boards/{AGENT_BOARD}").json()["agents"]
    assert client.post("/api/entries", json=_entry(), headers=headers).status_code == 401


def test_an_agents_skills_are_kept_and_named_in_its_runs(client):
    name = f"a-{uuid.uuid4().hex[:8]}"
    body = {"name": name, "boards": [AGENT_BOARD], "skills": ["gathering-sources", "linking-entries"]}
    assert client.post("/api/agents", json=body, headers=OWNER_HEADERS).json()["skills"] == body["skills"]
    assert client.post("/api/agents", json={"name": "x-bad", "skills": ["Not A Name"]}, headers=OWNER_HEADERS).status_code == 422
    kit = client.post("/api/runs", json={"agent": name, "boards": ["*"]}, headers=OWNER_HEADERS).json()
    assert "open-studio, studio-collaborator, gathering-sources, linking-entries" in kit["prompt"]


def test_an_agents_skills_must_be_in_the_agent_resources(client):
    name = f"a-{uuid.uuid4().hex[:8]}"
    refused = client.post("/api/agents", json={"name": name, "skills": ["building", "no-such-skill"]}, headers=OWNER_HEADERS)
    assert refused.status_code == 422
    assert "no-such-skill" in refused.json()["detail"] and "building" not in refused.json()["detail"]
    client.post("/api/agents", json={"name": name}, headers=OWNER_HEADERS)
    assert client.patch(f"/api/agents/{name}", json={"skills": ["no-such-skill"]}, headers=OWNER_HEADERS).status_code == 422
    assert client.patch(f"/api/agents/{name}", json={"skills": ["building"]}, headers=OWNER_HEADERS).json()["skills"] == ["building"]


def test_the_owner_exports_every_agent_as_yaml_without_tokens(client):
    name, _ = _add_agent(client)
    changes = {"description": 'says "hi"', "skills": ["building"], "addons": ["web"], "addon_instructions": {"web": "Cite pages."}}
    client.patch(f"/api/agents/{name}", json=changes, headers=OWNER_HEADERS)
    assert client.get("/api/agents/export").status_code == 401
    response = client.get("/api/agents/export", headers=OWNER_HEADERS)
    assert response.status_code == 200
    assert "agents.yaml" in response.headers["content-disposition"]
    text = response.text
    assert "version: 1" in text and "run." not in text
    block = text[text.index(f"  - name: {name}"):]
    assert block.splitlines()[1:7] == [
        '    description: "says \\"hi\\""',
        "    active: true",
        f'    boards: ["{AGENT_BOARD}"]',
        '    skills: ["building"]',
        '    addons: ["web"]',
        '    addon_instructions: {"web": "Cite pages."}',
    ]
