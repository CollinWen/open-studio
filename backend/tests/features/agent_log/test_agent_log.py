"""
Tests for the agent log: an agent writes lines about boards it's on and
anyone can read them, newest first and narrowed by agent or board; agents
can't write about boards they're not on, visitors and the owner can't write
at all, and a line may name an entry. (Setting a status through the agent server
is tested in tests/agent_server/test_agent_tools.py.)
"""

import uuid

from conftest import AGENT_BOARD, ARCHIVIST_HEADERS, OWNER_HEADERS, SCOUT_HEADERS


def _write(client, headers, **line) -> dict:
    body = {"board": AGENT_BOARD, "type": "plan", "text": f"look into {uuid.uuid4().hex}", **line}
    return client.post("/api/agent-log", json=body, headers=headers)


def test_an_agent_writes_and_anyone_reads(client):
    first = _write(client, SCOUT_HEADERS).json()
    second = _write(client, ARCHIVIST_HEADERS, type="finding").json()

    newest = client.get("/api/agent-log").json()
    assert [line["id"] for line in newest[:2]] == [second["id"], first["id"]]
    only_scout = client.get("/api/agent-log?agent=scout").json()
    assert all(line["agent"] == "scout" for line in only_scout)
    assert client.get(f"/api/agent-log?board={AGENT_BOARD}").json()[0]["id"] == second["id"]


def test_only_agents_write_and_only_on_their_boards(client):
    slug = f"b-{uuid.uuid4().hex[:8]}"
    client.post("/api/boards", json={"slug": slug, "name": slug}, headers=OWNER_HEADERS)
    assert _write(client, SCOUT_HEADERS, board=slug).status_code == 403
    assert _write(client, {}).status_code == 403
    assert _write(client, OWNER_HEADERS).status_code == 403


def test_a_line_can_name_an_entry(client):
    entry = {"board": AGENT_BOARD, "title": f"t {uuid.uuid4().hex}", "description": "why"}
    entry_id = client.post("/api/entries", json=entry, headers=SCOUT_HEADERS).json()["id"]
    line = _write(client, SCOUT_HEADERS, type="finding", entry_id=entry_id).json()
    assert line["entry_title"] == entry["title"]
    assert _write(client, SCOUT_HEADERS, entry_id="missing").status_code == 403

