"""
Tests for reading entries a page at a time: pages follow each other newest
first without repeats or gaps, the last page has no cursor, entries added
while paging don't shift later pages, and a made-up cursor is refused.
"""

import uuid

from conftest import OWNER_HEADERS

PAGE_SIZE = 3


def _board_with_entries(client, count: int) -> str:
    slug = f"p-{uuid.uuid4().hex[:8]}"
    client.post("/api/boards", json={"slug": slug, "name": slug}, headers=OWNER_HEADERS)
    for day in range(1, count + 1):
        body = {"title": f"day {day}", "board": slug, "occurred_at": f"2024-01-{day:02d}", "tags": ["t"]}
        client.post("/api/entries", json={**body, "visibility": "public"}, headers=OWNER_HEADERS)
    return slug


def _read_all_pages(client, slug: str) -> list[str]:
    titles, cursor = [], None
    while True:
        params = {"board": slug, "limit": PAGE_SIZE, **({"cursor": cursor} if cursor else {})}
        page = client.get("/api/entries/page", params=params).json()
        titles += [entry["title"] for entry in page["entries"]]
        cursor = page["next_cursor"]
        if cursor is None:
            return titles


def test_pages_cover_everything_newest_first(client):
    slug = _board_with_entries(client, 7)
    assert _read_all_pages(client, slug) == [f"day {day}" for day in range(7, 0, -1)]


def test_an_entry_added_while_paging_does_not_shift_later_pages(client):
    slug = _board_with_entries(client, 6)
    first = client.get("/api/entries/page", params={"board": slug, "limit": PAGE_SIZE}).json()
    newest = {
        "title": "newer",
        "board": slug,
        "occurred_at": "2024-02-01",
        "visibility": "public",
        "tags": ["t"],
    }
    client.post("/api/entries", json=newest, headers=OWNER_HEADERS)
    params = {"board": slug, "limit": PAGE_SIZE, "cursor": first["next_cursor"]}
    second = client.get("/api/entries/page", params=params).json()
    assert [entry["title"] for entry in second["entries"]] == ["day 3", "day 2", "day 1"]


def test_made_up_cursor_is_refused(client):
    assert client.get("/api/entries/page", params={"cursor": "not-a-cursor"}).status_code == 422
