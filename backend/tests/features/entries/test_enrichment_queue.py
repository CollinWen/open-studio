"""
Tests for the enrichment queue: what was worked out is saved to the entry,
unless the entry changed meaning while it was being read (that edit queued
its own reading), and tags the owner set meanwhile are never replaced.
"""

from sqlmodel import Session

from app.database import engine
from app.features.entries import enrichment_queue
from app.features.entries.enrichment import Enrichment
from app.features.entries.models import Entry


def _stored(**fields) -> str:
    with Session(engine) as db:
        entry = Entry(title="Queue: halibut", **fields)
        db.add(entry)
        db.commit()
        return entry.id


def _read(entry_id: str) -> Entry:
    with Session(engine) as db:
        return db.get(Entry, entry_id)


def test_what_was_worked_out_is_saved(monkeypatch):
    result = Enrichment(readings={"picture /media/a.jpg": "fish"}, tags=["fish"], embedding=[0.5])
    monkeypatch.setattr(enrichment_queue, "enrich_entry", lambda entry, tags, again: result)
    entry_id = _stored()

    enrichment_queue.enrich_and_save(entry_id)

    entry = _read(entry_id)
    assert (entry.readings, entry.tags, entry.embedding) == (result.readings, ["fish"], [0.5])
    assert entry.embedding_model == enrichment_queue.settings.embedding_model


def test_a_reading_of_an_older_version_is_dropped(monkeypatch):
    entry_id = _stored()

    def edited_meanwhile(entry, tags, again):
        with Session(engine) as db:
            stored = db.get(Entry, entry_id)
            stored.title = "Queue: halibut, renamed"
            db.add(stored)
            db.commit()
        return Enrichment(readings={"source x": "old"}, tags=["fish"], embedding=[0.5])

    monkeypatch.setattr(enrichment_queue, "enrich_entry", edited_meanwhile)
    enrichment_queue.enrich_and_save(entry_id)

    entry = _read(entry_id)
    assert (entry.readings, entry.tags, entry.embedding) == ({}, [], None)


def test_tags_already_set_are_kept(monkeypatch):
    monkeypatch.setattr(enrichment_queue, "enrich_entry", lambda entry, tags, again: Enrichment({}, ["other"], [0.5]))
    entry_id = _stored(tags=["mine"])
    enrichment_queue.enrich_and_save(entry_id)
    assert _read(entry_id).tags == ["mine"]
