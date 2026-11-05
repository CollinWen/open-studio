"""
Tests for Related without embeddings (tests never call OpenRouter), so
entries are matched by shared tags: closest first, only on the entry's own
board, and never showing a visitor something they couldn't open.
"""

from conftest import AGENT_BOARD, OWNER_HEADERS


def add_entry(client, title, tags, visibility="public", board="home"):
    entry = {"title": title, "tags": tags, "visibility": visibility, "board": board}
    return client.post("/api/entries", json=entry, headers=OWNER_HEADERS).json()["id"]


def related_titles(client, entry_id, headers=None):
    return [entry["title"] for entry in client.get(f"/api/entries/{entry_id}/related", headers=headers).json()]


def test_related_ranks_by_shared_tags_and_skips_strangers(client):
    loaf = add_entry(client, "Related: loaf", ["rel-crumb", "rel-crust", "rel-oven"])
    add_entry(client, "Related: two shared", ["rel-crumb", "rel-crust"])
    add_entry(client, "Related: one shared", ["rel-oven"])
    add_entry(client, "Related: nothing shared", ["rel-glaze"])

    assert related_titles(client, loaf) == ["Related: two shared", "Related: one shared"]


def test_related_stays_on_the_entrys_own_board(client):
    loaf = add_entry(client, "Board: loaf", ["rel-board-tag"])
    add_entry(client, "Board: same board", ["rel-board-tag"])
    add_entry(client, "Board: other board", ["rel-board-tag"], board=AGENT_BOARD)

    assert related_titles(client, loaf) == ["Board: same board"]


def test_related_hides_what_a_visitor_cannot_see(client):
    loaf = add_entry(client, "Hidden: loaf", ["rel-hidden-tag"])
    add_entry(client, "Hidden: public", ["rel-hidden-tag"])
    add_entry(client, "Hidden: private", ["rel-hidden-tag"], visibility="private")
    add_entry(client, "Hidden: unlisted", ["rel-hidden-tag"], visibility="unlisted")

    assert related_titles(client, loaf) == ["Hidden: public"]
    assert set(related_titles(client, loaf, OWNER_HEADERS)) == {"Hidden: public", "Hidden: private", "Hidden: unlisted"}
