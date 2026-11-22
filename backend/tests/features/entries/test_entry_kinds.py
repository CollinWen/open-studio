"""
Tests that an entry's kind is kept plain: "Photo", " photo " and "PHOTO"
are all saved as "photo", on create and on edit, by the owner and agents
alike, and a blank kind is a note. Also that the migration step brings
kinds saved before this rule in line.
"""

from sqlalchemy import create_engine, text

from app import database_migrations
from conftest import AGENT_BOARD, OWNER_HEADERS, SCOUT_HEADERS


def _create(client, headers=OWNER_HEADERS, **fields):
    entry = {"title": "kinds", "board": AGENT_BOARD if headers is SCOUT_HEADERS else "home", **fields}
    response = client.post("/api/entries", json=entry, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def test_a_kind_is_saved_lowercase_with_single_spaces(client):
    for headers in (OWNER_HEADERS, SCOUT_HEADERS):
        assert _create(client, headers=headers, kind="Photo")["kind"] == "photo"
        assert _create(client, headers=headers, kind="  Field   NOTES ")["kind"] == "field notes"


def test_a_blank_kind_is_a_note(client):
    assert _create(client, kind="   ")["kind"] == "note"
    assert _create(client)["kind"] == "note"


def test_an_edited_kind_is_kept_plain_and_an_unsent_kind_is_left_alone(client):
    entry = _create(client, kind="book")
    edited = client.patch(f"/api/entries/{entry['id']}", json={"kind": "Video "}, headers=OWNER_HEADERS)
    assert edited.json()["kind"] == "video"
    untouched = client.patch(f"/api/entries/{entry['id']}", json={"title": "renamed"}, headers=OWNER_HEADERS)
    assert untouched.json()["kind"] == "video"


def test_the_migration_step_makes_older_kinds_plain(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'old.db'}")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE entry (id VARCHAR PRIMARY KEY, kind VARCHAR)"))
        connection.execute(text("INSERT INTO entry VALUES ('a', 'Photo'), ('b', ' photo '), ('c', ''), ('d', 'note')"))
        step = next(s for s in database_migrations.MIGRATIONS if s.startswith("UPDATE entry SET kind"))
        connection.execute(text(step))
        kinds = dict(connection.execute(text("SELECT id, kind FROM entry")).all())
    assert kinds == {"a": "photo", "b": "photo", "c": "note", "d": "note"}
