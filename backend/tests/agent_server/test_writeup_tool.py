"""
Tests for attach_writeup on the agent server: an agent's write-up is made
safe, stored and added to its entry's media; it can't be attached to the
owner's entries; and an entry can't point at a write-up the studio didn't
store (so nothing unsanitized is ever shown).
"""

from dataclasses import replace

import pytest
from conftest import AGENT_BOARD, OWNER_HEADERS, SCOUT_HEADERS
from test_agent_tools import _tool

from app.integrations import media_storage


@pytest.fixture(autouse=True)
def never_r2(monkeypatch):
    monkeypatch.setattr(media_storage, "settings", replace(media_storage.settings, r2_account_id=""))


def _agent_entry(client) -> str:
    added = _tool(client, "add_entry", {"board": AGENT_BOARD, "title": "study", "description": "why"}, SCOUT_HEADERS)
    return added["structuredContent"]["id"]


def test_an_agent_attaches_a_safe_write_up(running_client):
    entry_id = _agent_entry(running_client)
    html = '<h1 style="font-family:Comic Sans">Findings</h1><p>Plain words.</p>'

    attached = _tool(running_client, "attach_writeup", {"entry_id": entry_id, "html": html}, SCOUT_HEADERS)

    assert not attached["isError"], attached
    result = attached["structuredContent"]
    assert result["removed"] == ["style attributes: 1"]
    writeup = result["entry"]["media"][-1]
    assert writeup["type"] == "html"
    assert running_client.get(writeup["url"]).text == "<h1>Findings</h1><p>Plain words.</p>"


def test_a_write_up_cannot_go_on_the_owners_entry(running_client):
    owner_entry = running_client.post("/api/entries", json={"title": "mine", "tags": ["t"]}, headers=OWNER_HEADERS)
    attempt = _tool(
        running_client, "attach_writeup", {"entry_id": owner_entry.json()["id"], "html": "<p>x</p>"}, SCOUT_HEADERS
    )
    assert attempt["isError"]


def test_an_entry_cannot_point_at_a_write_up_stored_elsewhere(client):
    foreign = {"type": "html", "url": "https://elsewhere.example.com/page.html"}
    response = client.post("/api/entries", json={"title": "x", "media": [foreign]}, headers=OWNER_HEADERS)
    assert response.status_code == 422
