"""
Tests for the owner's view of what the studio read from an entry: only the
owner gets it, it lists each part and the exact text that was embedded, and
"read again" (one entry, or all) queues a fresh reading.
"""

from sqlmodel import Session

from conftest import OWNER_HEADERS, SCOUT_HEADERS

from app.database import engine
from app.features.entries.models import Entry


def _entry_with_readings(client) -> str:
    entry_id = client.post("/api/entries", json={"title": "Reading: halibut", "visibility": "public", "tags": ["fish"],
                                 "media": [{"type": "image", "url": "/media/a.jpg"}]},
                           headers=OWNER_HEADERS).json()["id"]
    with Session(engine) as db:
        stored = db.get(Entry, entry_id)
        stored.readings = {"picture /media/a.jpg": "white fish on leeks"}
        db.add(stored)
        db.commit()
    return entry_id


def test_only_the_owner_sees_what_was_read(client):
    entry_id = _entry_with_readings(client)
    assert client.get(f"/api/entries/{entry_id}/reading").status_code == 401
    assert client.get(f"/api/entries/{entry_id}/reading", headers=SCOUT_HEADERS).status_code in (401, 403)
    assert "readings" not in client.get(f"/api/entries/{entry_id}").json()

    reading = client.get(f"/api/entries/{entry_id}/reading", headers=OWNER_HEADERS).json()
    assert reading["parts"] == [{"part": "picture", "address": "/media/a.jpg", "text": "white fish on leeks"}]
    assert "Picture: white fish on leeks" in reading["embedding_text"]
    assert reading["has_embedding"] is False and reading["waiting"] is False


def test_read_again_is_for_the_owner(client):
    entry_id = _entry_with_readings(client)
    assert client.post(f"/api/entries/{entry_id}/read-again").status_code == 401
    assert client.post(f"/api/entries/{entry_id}/read-again", headers=OWNER_HEADERS).status_code == 200
    assert client.post("/api/entries/read-all-again", headers=OWNER_HEADERS).json()["queued"] >= 1
    assert client.post("/api/entries/read-all-again").status_code == 401
