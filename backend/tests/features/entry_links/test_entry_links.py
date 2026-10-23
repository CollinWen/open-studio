"""
Tests for "builds on" links: a chain shows what an entry builds on and what
builds on it, loops and self-links are refused, visitors don't see unlisted
agent entries in a chain, agents can't link from the owner's entries, and
deleting an entry removes its links.
"""

from conftest import AGENT_BOARD, OWNER_HEADERS, SCOUT_HEADERS


def _entry(client, title: str, headers=OWNER_HEADERS, **fields) -> str:
    body = {"title": title, "tags": ["t"], "visibility": "public", **fields}
    response = client.post("/api/entries", json=body, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()["id"]


def _link(client, entry_id: str, builds_on_id: str, headers=OWNER_HEADERS):
    body = {"builds_on_id": builds_on_id, "note": "extends it"}
    return client.post(f"/api/entries/{entry_id}/builds-on", json=body, headers=headers)


def test_chain_runs_back_and_forward(client):
    root, middle, later = (_entry(client, title) for title in ("root", "middle", "later"))
    assert _link(client, middle, root).status_code == 200
    assert _link(client, later, middle).status_code == 200

    chain = client.get(f"/api/entries/{middle}/chain").json()
    assert {entry["id"] for entry in chain["entries"]} == {root, middle, later}
    assert {(link["entry_id"], link["builds_on_id"]) for link in chain["links"]} == {
        (middle, root),
        (later, middle),
    }


def test_loops_and_self_links_are_refused(client):
    first, second = _entry(client, "first"), _entry(client, "second")
    assert _link(client, second, first).status_code == 200
    assert _link(client, first, second).status_code == 403
    assert _link(client, first, first).status_code == 403
    assert _link(client, second, first).status_code == 403


def test_visitors_do_not_see_unlisted_agent_entries_in_a_chain(client):
    root = _entry(client, "root")
    agent_entry = _entry(client, "agent find", headers=SCOUT_HEADERS, board=AGENT_BOARD)
    assert _link(client, agent_entry, root, headers=SCOUT_HEADERS).status_code == 200

    visitor_ids = {entry["id"] for entry in client.get(f"/api/entries/{root}/chain").json()["entries"]}
    agent_ids = {
        entry["id"]
        for entry in client.get(f"/api/entries/{root}/chain", headers=SCOUT_HEADERS).json()["entries"]
    }
    assert agent_entry not in visitor_ids
    assert agent_entry in agent_ids


def test_agents_cannot_link_from_owner_entries(client):
    owner_entry, other = _entry(client, "mine"), _entry(client, "other")
    assert _link(client, owner_entry, other, headers=SCOUT_HEADERS).status_code == 403


def test_deleting_an_entry_removes_its_links(client):
    root, later = _entry(client, "root"), _entry(client, "later")
    _link(client, later, root)
    client.delete(f"/api/entries/{root}", headers=OWNER_HEADERS)
    assert client.get(f"/api/entries/{later}/chain").json()["links"] == []
