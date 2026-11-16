"""
Tests for search without embeddings (tests never call OpenRouter): plain
text matches across title, description and tags; private entries stay hidden.
"""

import uuid

from conftest import OWNER_HEADERS


def test_text_search_finds_matches_and_respects_visibility(client):
    client.post("/api/entries", json={"title": "Rye loaf", "description": "dense and sour", "visibility": "public", "tags": ["baking"]}, headers=OWNER_HEADERS)
    client.post("/api/entries", json={"title": "Secret loaf", "visibility": "private", "tags": ["baking"]}, headers=OWNER_HEADERS)

    titles = [entry["title"] for entry in client.get("/api/search", params={"q": "BAKING"}).json()]
    assert "Rye loaf" in titles
    assert "Secret loaf" not in titles
    assert client.get("/api/search", params={"q": "sour"}).json()[0]["title"] == "Rye loaf"
    assert client.get("/api/search", params={"q": "   "}).json() == []


def test_every_entry_with_the_words_is_found_however_many(client):
    word = f"w{uuid.uuid4().hex[:10]}"
    for number in range(30):
        entry = {"title": f"{word} loaf {number}", "visibility": "public", "tags": ["baking"]}
        client.post("/api/entries", json=entry, headers=OWNER_HEADERS)

    assert len(client.get("/api/search", params={"q": word}).json()) == 30
