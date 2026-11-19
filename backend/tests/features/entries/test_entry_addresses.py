"""
Tests that an entry's addresses are web addresses: its source link and each
media item's address and thumbnail must start with http:// or https:// (or
be a file the studio stored, /media/...), on create and on edit, for the
owner and agents alike. Anything else (javascript:, data:, a bare word) is
refused with a plain message, so it can never reach a page as a link.
"""

from conftest import AGENT_BOARD, OWNER_HEADERS, SCOUT_HEADERS

NOT_WEB_ADDRESSES = ["javascript:alert(1)", " JaVaScRiPt:alert(1)", "data:text/html,<script>x</script>", "vbscript:x", "notes"]


def _create(client, headers=OWNER_HEADERS, **fields):
    entry = {"title": "addresses", "board": AGENT_BOARD if headers is SCOUT_HEADERS else "home", **fields}
    return client.post("/api/entries", json=entry, headers=headers)


def test_web_addresses_and_stored_files_are_kept(client):
    response = _create(
        client,
        source_url="https://example.com/recipe",
        media=[
            {"type": "image", "url": "/media/abc123.jpg"},
            {"type": "embed", "url": "https://www.youtube-nocookie.com/embed/x", "thumbnail_url": "https://i.ytimg.com/x.jpg"},
            {"type": "video", "url": "http://example.com/clip.mp4", "thumbnail_url": ""},
        ],
    )
    assert response.status_code == 200, response.text
    assert response.json()["source_url"] == "https://example.com/recipe"
    assert _create(client, source_url="").status_code == 200


def test_a_source_link_that_is_not_a_web_address_is_refused(client):
    for headers in (OWNER_HEADERS, SCOUT_HEADERS):
        for address in NOT_WEB_ADDRESSES:
            response = _create(client, headers=headers, source_url=address)
            assert response.status_code == 422, (address, response.text)
            assert "http:// or https://" in response.text


def test_media_addresses_that_are_not_web_addresses_are_refused(client):
    for address in NOT_WEB_ADDRESSES:
        assert _create(client, media=[{"type": "embed", "url": address}]).status_code == 422, address
        image_with_bad_thumbnail = {"type": "image", "url": "/media/abc.jpg", "thumbnail_url": address}
        assert _create(client, media=[image_with_bad_thumbnail]).status_code == 422, address


def test_an_edit_is_held_to_the_same_rule(client):
    entry_id = _create(client, source_url="https://example.com").json()["id"]
    edit = client.patch(f"/api/entries/{entry_id}", json={"source_url": "javascript:alert(1)"}, headers=OWNER_HEADERS)
    assert edit.status_code == 422
    assert client.get(f"/api/entries/{entry_id}", headers=OWNER_HEADERS).json()["source_url"] == "https://example.com"


def test_addresses_are_kept_without_surrounding_spaces(client):
    response = _create(client, source_url="  https://example.com/recipe  ")
    assert response.status_code == 200
    assert response.json()["source_url"] == "https://example.com/recipe"
