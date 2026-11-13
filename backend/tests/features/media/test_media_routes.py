"""
Tests for POST /api/media: only the owner may upload; a file type the studio
doesn't keep is refused with a plain message; and an upload comes back as a
URL that serves exactly the bytes that were sent (media is never altered).
Uploads go to the test's throwaway data folder, never to R2.
"""

from dataclasses import replace

import pytest
from conftest import OWNER_HEADERS, SCOUT_HEADERS

from app.integrations import media_storage

# Not a real picture: the studio stores what it's given without opening it.
PICTURE = bytes(range(256)) * 4


@pytest.fixture(autouse=True)
def never_r2(monkeypatch):
    """Even with R2 settings in a developer's .env, these uploads stay on local disk."""
    monkeypatch.setattr(media_storage, "settings", replace(media_storage.settings, r2_account_id=""))


def _upload(client, name: str, headers=OWNER_HEADERS, content: bytes = PICTURE):
    return client.post("/api/media", files={"file": (name, content)}, headers=headers)


def test_only_the_owner_may_upload(client):
    assert _upload(client, "photo.jpg", headers={}).status_code == 401
    assert _upload(client, "photo.jpg", headers=SCOUT_HEADERS).status_code == 401


def test_a_file_type_the_studio_does_not_keep_is_refused(client):
    response = _upload(client, "notes.pdf")

    assert response.status_code == 400
    assert response.json()["detail"]


def test_an_upload_is_served_back_exactly_as_sent(client):
    response = _upload(client, "Crumb Shot.JPG")

    assert response.status_code == 200
    url = response.json()["url"]
    assert url.startswith("/media/") and url.endswith(".jpg")
    served = client.get(url)
    assert served.status_code == 200
    assert served.content == PICTURE


def test_two_uploads_with_the_same_name_keep_both(client):
    first = _upload(client, "same.png", content=b"first").json()["url"]
    second = _upload(client, "same.png", content=b"second").json()["url"]

    assert first != second
    assert client.get(first).content == b"first"
    assert client.get(second).content == b"second"


def test_an_uploaded_write_up_is_made_safe_and_says_what_was_removed(client):
    html = b'<p style="color:red">words</p><script>alert(1)</script>'

    response = _upload(client, "Findings.html", content=html)

    assert response.status_code == 200
    body = response.json()
    assert body["url"].endswith(".html")
    assert "<script>: 1" in body["removed"]
    assert client.get(body["url"]).text == "<p>words</p>"


def test_a_write_up_with_nothing_to_keep_is_refused(client):
    response = _upload(client, "empty.html", content=b"<script>alert(1)</script>")

    assert response.status_code == 400
    assert response.json()["detail"]
