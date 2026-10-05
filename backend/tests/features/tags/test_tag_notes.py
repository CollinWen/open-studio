"""
Tests for tag notes: the owner can describe a tag and set its importance;
key tags come first, and hidden tags are left out for visitors.
"""

from conftest import OWNER_HEADERS


def _create(client, title: str, tags: list[str]) -> None:
    client.post("/api/entries", json={"title": title, "visibility": "public", "tags": tags}, headers=OWNER_HEADERS)


def test_tag_notes_order_and_hiding(client):
    _create(client, "a", ["common", "special", "noise"])
    _create(client, "b", ["common", "noise"])

    assert client.put("/api/tags/special", json={"description": "x"}).status_code == 401
    client.put("/api/tags/special", json={"description": "Why this matters.", "importance": 1}, headers=OWNER_HEADERS)
    client.put("/api/tags/noise", json={"importance": -1}, headers=OWNER_HEADERS)

    visitor_tags = [tag["name"] for tag in client.get("/api/tags").json()]
    assert visitor_tags[0] == "special"
    assert "noise" not in visitor_tags
    assert "noise" in [tag["name"] for tag in client.get("/api/tags", headers=OWNER_HEADERS).json()]

    special = next(tag for tag in client.get("/api/tags").json() if tag["name"] == "special")
    assert special["description"] == "Why this matters."
