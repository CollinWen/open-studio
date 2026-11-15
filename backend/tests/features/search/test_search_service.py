"""
Tests for search/service.py's ranking, with entries and the query's
embedding made up (tests never call OpenRouter): entries that contain the
words come first and are all kept; entries found by meaning alone fill up to
RESULT_LIMIT and no further.
"""

from app.auth.viewer import Viewer
from app.features.entries.models import Entry
from app.features.search import service

NEAR = [1.0, 0.0]


def _entry(title: str, embedding: list[float]) -> Entry:
    return Entry(title=title, embedding=embedding, tags=[])


def _search(monkeypatch, entries: list[Entry], query: str) -> list[str]:
    monkeypatch.setattr(service.entries_service, "list_entries", lambda db, viewer, board=None: entries)
    monkeypatch.setattr(service, "_embed_query", lambda text: NEAR)
    return [entry.title for entry in service.search_entries(None, query, Viewer(role="visitor"))]


def test_meaning_only_matches_fill_up_to_the_limit_after_the_words(monkeypatch):
    with_words = [_entry(f"sourdough {n}", [0.0, 1.0]) for n in range(5)]
    by_meaning = [_entry(f"levain {n}", NEAR) for n in range(40)]

    found = _search(monkeypatch, by_meaning + with_words, "sourdough")

    assert found[:5] == [f"sourdough {n}" for n in range(5)]
    assert len(found) == service.RESULT_LIMIT


def test_word_matches_are_never_cut_even_past_the_limit(monkeypatch):
    with_words = [_entry(f"sourdough {n}", NEAR) for n in range(service.RESULT_LIMIT + 6)]
    by_meaning = [_entry(f"levain {n}", NEAR) for n in range(10)]

    found = _search(monkeypatch, with_words + by_meaning, "sourdough")

    assert len(found) == service.RESULT_LIMIT + 6
    assert all(title.startswith("sourdough") for title in found)


def test_unrelated_entries_are_left_out(monkeypatch):
    far = _entry("kiln notes", [0.0, 1.0])

    assert _search(monkeypatch, [far], "sourdough") == []
