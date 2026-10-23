"""
Tests for agents adding and editing entries: their entries arrive unlisted and
signed with their name, other agents can list them but visitors can't, agents
can't publish or touch the owner's entries, the same link isn't added twice,
and the hourly write limit holds.
"""

import uuid

from conftest import AGENT_BOARD, ARCHIVIST_HEADERS, OWNER_HEADERS, SCOUT_HEADERS


def _agent_create(client, headers, **fields) -> dict:
    body = {
        "title": "found it",
        "tags": ["test"],
        "board": AGENT_BOARD,
        "source_url": f"https://example.com/{uuid.uuid4().hex}",
    }
    response = client.post("/api/entries", json={**body, **fields}, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def _listed_ids(client, headers=None) -> set[str]:
    return {entry["id"] for entry in client.get("/api/entries", headers=headers or {}).json()}


def test_agent_entries_arrive_unlisted_and_signed(client):
    entry = _agent_create(client, SCOUT_HEADERS, visibility="public")
    assert entry["visibility"] == "unlisted"
    assert entry["added_by"] == "agent:scout"


def test_agents_see_each_others_entries_but_visitors_do_not(client):
    entry_id = _agent_create(client, SCOUT_HEADERS)["id"]
    assert entry_id in _listed_ids(client, ARCHIVIST_HEADERS)
    assert entry_id not in _listed_ids(client)
    assert client.get(f"/api/entries/{entry_id}").status_code == 200


def test_agents_do_not_list_the_owners_unlisted_or_private_entries(client):
    owner_ids = {
        client.post(
            "/api/entries", json={"title": v, "visibility": v, "tags": ["t"]}, headers=OWNER_HEADERS
        ).json()["id"]
        for v in ("unlisted", "private")
    }
    assert not owner_ids & _listed_ids(client, SCOUT_HEADERS)


def test_agents_edit_agent_entries_but_cannot_publish(client):
    entry_id = _agent_create(client, SCOUT_HEADERS)["id"]
    edited = client.patch(f"/api/entries/{entry_id}", json={"description": "more"}, headers=ARCHIVIST_HEADERS)
    assert edited.status_code == 200
    published = client.patch(f"/api/entries/{entry_id}", json={"visibility": "public"}, headers=SCOUT_HEADERS)
    assert published.status_code == 403


def test_agents_cannot_edit_or_delete_owner_entries(client):
    owner_id = client.post(
        "/api/entries",
        json={"title": "mine", "visibility": "public", "tags": ["test"]},
        headers=OWNER_HEADERS,
    ).json()["id"]
    assert (
        client.patch(f"/api/entries/{owner_id}", json={"title": "x"}, headers=SCOUT_HEADERS).status_code
        == 403
    )
    assert client.delete(f"/api/entries/{owner_id}", headers=SCOUT_HEADERS).status_code == 401


def test_once_published_an_agent_entry_belongs_to_the_owner(client):
    entry_id = _agent_create(client, SCOUT_HEADERS)["id"]
    client.patch(f"/api/entries/{entry_id}", json={"visibility": "public"}, headers=OWNER_HEADERS)
    assert (
        client.patch(f"/api/entries/{entry_id}", json={"title": "x"}, headers=SCOUT_HEADERS).status_code
        == 403
    )


def test_the_same_link_is_not_added_twice(client):
    first = _agent_create(client, SCOUT_HEADERS)
    again = client.post(
        "/api/entries",
        json={"title": "again", "board": AGENT_BOARD, "source_url": first["source_url"]},
        headers=ARCHIVIST_HEADERS,
    )
    assert again.status_code == 409
    assert again.json()["detail"]["existing_id"] == first["id"]


def test_duplicate_of_a_private_entry_does_not_reveal_it(client):
    url = f"https://example.com/{uuid.uuid4().hex}"
    client.post(
        "/api/entries", json={"title": "secret", "source_url": url, "tags": ["t"]}, headers=OWNER_HEADERS
    )
    again = client.post(
        "/api/entries", json={"title": "x", "board": AGENT_BOARD, "source_url": url}, headers=SCOUT_HEADERS
    )
    assert again.status_code == 409
    assert again.json()["detail"]["existing_id"] is None


def test_hourly_write_limit(client):
    for _ in range(5):
        _agent_create(client, SCOUT_HEADERS)
    assert (
        client.post(
            "/api/entries", json={"title": "one too many", "board": AGENT_BOARD}, headers=SCOUT_HEADERS
        ).status_code
        == 429
    )
    _agent_create(client, ARCHIVIST_HEADERS)


def test_unknown_tokens_cannot_write(client):
    headers = {"Authorization": "Bearer not-a-token"}
    assert client.post("/api/entries", json={"title": "nope"}, headers=headers).status_code == 401


def test_updated_since_lists_only_recent_changes(client):
    before = client.get("/api/entries", headers=OWNER_HEADERS).json()
    newest_change = max(entry["updated_at"] for entry in before)
    entry_id = _agent_create(client, SCOUT_HEADERS)["id"]
    recent = client.get("/api/entries", params={"updated_since": newest_change}, headers=SCOUT_HEADERS).json()
    assert [entry["id"] for entry in recent] == [entry_id]
