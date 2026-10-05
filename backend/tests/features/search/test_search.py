"""
Tests for search without embeddings (tests never call OpenRouter): plain
text matches across title, description and tags; private entries stay hidden.
"""

from conftest import OWNER_HEADERS


def test_text_search_finds_matches_and_respects_visibility(client):
    client.post("/api/entries", json={"title": "Rye loaf", "description": "dense and sour", "visibility": "public", "tags": ["baking"]}, headers=OWNER_HEADERS)
    client.post("/api/entries", json={"title": "Secret loaf", "visibility": "private", "tags": ["baking"]}, headers=OWNER_HEADERS)

    titles = [entry["title"] for entry in client.get("/api/search", params={"q": "BAKING"}).json()]
    assert "Rye loaf" in titles
    assert "Secret loaf" not in titles
    assert client.get("/api/search", params={"q": "sour"}).json()[0]["title"] == "Rye loaf"
    assert client.get("/api/search", params={"q": "   "}).json() == []
