"""
Tests for POST /api/capture/link: only the owner may read links, a link that
can't be read comes back as a plain message (422), and a readable one comes
back as a draft. The reader is replaced with a fixed result, so no network
calls, and nothing is ever saved.
"""

from conftest import OWNER_HEADERS, SCOUT_HEADERS

from app.features.capture import service
from app.integrations.link_readers.link_details import LinkDetails


def test_only_the_owner_may_capture(client):
    link = {"url": "https://example.com"}
    assert client.post("/api/capture/link", json=link).status_code == 401
    assert client.post("/api/capture/link", json=link, headers=SCOUT_HEADERS).status_code == 401


def test_a_link_that_cannot_be_read_says_why(client):
    response = client.post("/api/capture/link", json={"url": "example.com/no-scheme"}, headers=OWNER_HEADERS)

    assert response.status_code == 422
    assert response.json()["detail"] == "Links need to start with http:// or https://"


def test_a_readable_link_comes_back_as_a_draft_and_nothing_is_saved(client, monkeypatch):
    monkeypatch.setattr(service, "read_link", lambda url: LinkDetails(url=url, title="Captured page", platform="Example"))
    entries_before = len(client.get("/api/entries", headers=OWNER_HEADERS).json())

    response = client.post("/api/capture/link", json={"url": "https://example.com/page"}, headers=OWNER_HEADERS)

    assert response.status_code == 200
    assert response.json()["title"] == "Captured page"
    assert response.json()["source_name"] == "Example"
    assert len(client.get("/api/entries", headers=OWNER_HEADERS).json()) == entries_before
