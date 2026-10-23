"""
Tests for boards: the home board always exists and is listed first, only the
owner makes boards, entries land on the home board unless told otherwise,
listings filter by board, and agents only add to boards they're signed on to.
"""

import uuid

from conftest import AGENT_BOARD, OWNER_HEADERS, SCOUT_HEADERS


def _new_board(client, agents: list[str] | None = None) -> str:
    slug = f"b-{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/api/boards", json={"slug": slug, "name": slug, "agents": agents or []}, headers=OWNER_HEADERS
    )
    assert response.status_code == 200, response.text
    return slug


def test_home_board_is_listed_first(client):
    assert client.get("/api/boards").json()[0]["slug"] == "home"


def test_only_the_owner_makes_boards(client):
    board = {"slug": "nope", "name": "nope"}
    assert client.post("/api/boards", json=board, headers=SCOUT_HEADERS).status_code == 401


def test_slugs_must_work_in_a_link(client):
    board = {"slug": "Not A Slug", "name": "x"}
    assert client.post("/api/boards", json=board, headers=OWNER_HEADERS).status_code == 422


def test_entries_land_on_home_unless_told(client):
    entry = client.post("/api/entries", json={"title": "x", "tags": ["t"]}, headers=OWNER_HEADERS).json()
    assert entry["board"] == "home"


def test_listings_filter_by_board(client):
    slug = _new_board(client)
    body = {"title": "on the board", "board": slug, "visibility": "public", "tags": ["t"]}
    entry_id = client.post("/api/entries", json=body, headers=OWNER_HEADERS).json()["id"]
    assert [entry["id"] for entry in client.get("/api/entries", params={"board": slug}).json()] == [entry_id]
    home_ids = {entry["id"] for entry in client.get("/api/entries", params={"board": "home"}).json()}
    assert entry_id not in home_ids


def test_agents_add_only_to_their_boards(client):
    elsewhere = _new_board(client, agents=["archivist"])
    refused = client.post("/api/entries", json={"title": "x", "board": elsewhere}, headers=SCOUT_HEADERS)
    assert refused.status_code == 403
    assert (
        client.post("/api/entries", json={"title": "x", "board": "home"}, headers=SCOUT_HEADERS).status_code
        == 403
    )
    allowed = client.post("/api/entries", json={"title": "x", "board": AGENT_BOARD}, headers=SCOUT_HEADERS)
    assert allowed.status_code == 200


def test_agents_cannot_move_entries_off_their_boards(client):
    entry = client.post(
        "/api/entries", json={"title": "x", "board": AGENT_BOARD}, headers=SCOUT_HEADERS
    ).json()
    moved = client.patch(f"/api/entries/{entry['id']}", json={"board": "home"}, headers=SCOUT_HEADERS)
    assert moved.status_code == 403


def test_unknown_board_is_refused(client):
    response = client.post("/api/entries", json={"title": "x", "board": "nowhere"}, headers=OWNER_HEADERS)
    assert response.status_code == 422
