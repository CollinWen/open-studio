"""
Tests for an entry's write-up text: when an entry gets a write-up, its words
are read back and kept with the entry (never sent to the browser), so word
search finds them and the embedding and tag suggestions read them; when the
write-up is removed, its words go too.
"""

from dataclasses import replace

import pytest
from conftest import OWNER_HEADERS

from app.features.entries.enrichment import build_embedding_text
from app.features.entries.models import Entry
from app.integrations import media_storage

WRITEUP = b"<h1>Findings</h1><p>The levain doubled in quinquennial time.</p><style>p { color: red }</style>"


@pytest.fixture(autouse=True)
def never_r2(monkeypatch):
    monkeypatch.setattr(media_storage, "settings", replace(media_storage.settings, r2_account_id=""))


def _writeup_item(client) -> dict:
    url = client.post("/api/media", files={"file": ("w.html", WRITEUP)}, headers=OWNER_HEADERS).json()["url"]
    return {"type": "html", "url": url}


def _search(client, words: str) -> list[str]:
    return [entry["id"] for entry in client.get("/api/search", params={"q": words}, headers=OWNER_HEADERS).json()]


def test_word_search_finds_what_only_the_write_up_says(client):
    entry = client.post(
        "/api/entries",
        json={"title": "bake", "tags": ["t"], "media": [_writeup_item(client)]},
        headers=OWNER_HEADERS,
    ).json()

    assert "writeup_text" not in entry
    assert entry["id"] in _search(client, "quinquennial")


def test_removing_the_write_up_removes_its_words(client):
    entry = client.post("/api/entries", json={"title": "bake", "tags": ["t"]}, headers=OWNER_HEADERS).json()
    client.patch(f"/api/entries/{entry['id']}", json={"media": [_writeup_item(client)]}, headers=OWNER_HEADERS)
    assert entry["id"] in _search(client, "quinquennial")

    client.patch(f"/api/entries/{entry['id']}", json={"media": []}, headers=OWNER_HEADERS)
    assert entry["id"] not in _search(client, "quinquennial")


def test_the_embedding_reads_the_write_up_after_the_description():
    entry = Entry(title="bake", description="why", writeup_text="Findings The levain doubled.")
    text = build_embedding_text(entry)
    assert text.index("why") < text.index("Write-up: Findings The levain doubled.")
