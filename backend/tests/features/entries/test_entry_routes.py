"""
Tests for the entry endpoints: who can see what (public in the list, unlisted
by direct link, private for the owner only), owner-only writes, dates, and the file size kept on uploaded media.
"""

from conftest import OWNER_HEADERS


def _create(client, title: str, visibility: str) -> str:
    response = client.post(
        "/api/entries",
        json={"title": title, "visibility": visibility, "tags": ["test"]},
        headers=OWNER_HEADERS,
    )
    assert response.status_code == 200
    return response.json()["id"]


def test_visitors_cannot_create_entries(client):
    assert client.post("/api/entries", json={"title": "nope"}).status_code == 401


def test_visibility_rules(client):
    public_id = _create(client, "public piece", "public")
    unlisted_id = _create(client, "unlisted piece", "unlisted")
    private_id = _create(client, "private piece", "private")

    visitor_ids = {entry["id"] for entry in client.get("/api/entries").json()}
    assert public_id in visitor_ids
    assert unlisted_id not in visitor_ids
    assert private_id not in visitor_ids

    assert client.get(f"/api/entries/{unlisted_id}").status_code == 200
    assert client.get(f"/api/entries/{private_id}").status_code == 404
    assert client.get(f"/api/entries/{private_id}", headers=OWNER_HEADERS).status_code == 200


def test_plain_date_is_accepted_for_occurred_at(client):
    response = client.post(
        "/api/entries",
        json={"title": "backfilled", "occurred_at": "2024-05-01", "tags": ["test"]},
        headers=OWNER_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()["occurred_at"].startswith("2024-05-01")


def test_media_keeps_its_file_size(client):
    media = [
        {"type": "image", "url": "/media/a.jpg", "size_bytes": 840_000},
        {"type": "embed", "url": "https://www.youtube.com/embed/x"},
    ]
    response = client.post(
        "/api/entries", json={"title": "sized", "media": media, "tags": ["test"]}, headers=OWNER_HEADERS
    )
    assert response.status_code == 200
    saved = client.get(f"/api/entries/{response.json()['id']}", headers=OWNER_HEADERS).json()["media"]
    assert [item["size_bytes"] for item in saved] == [840_000, 0]


def test_media_size_cannot_be_negative(client):
    media = [{"type": "image", "url": "/media/a.jpg", "size_bytes": -1}]
    response = client.post("/api/entries", json={"title": "bad", "media": media}, headers=OWNER_HEADERS)
    assert response.status_code == 422
