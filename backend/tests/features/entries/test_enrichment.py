"""
Tests for enrichment: the embedding text puts the owner's words first, then
tags, then what was read from the source, each picture (with its caption)
and the write-up; the meaning fingerprint changes with any meaning field;
and nothing is worked out without OpenRouter. Never calls OpenRouter.
"""

from app.features.entries import enrichment
from app.features.entries.enrichment import build_embedding_text, enrich_entry, meaning_fingerprint
from app.features.entries.models import Entry


def test_the_embedding_text_reads_every_part_after_the_owners_words():
    entry = Entry(
        title="Halibut",
        description="why it's here",
        tags=["fish"],
        media=[{"type": "image", "url": "/media/a.jpg", "caption": "plated"}, {"type": "video", "url": "/media/v.mp4", "caption": "the steam"}],
        readings={"source https://x.com/p/1": "a post", "picture /media/a.jpg": "white fish on leeks"},
        writeup_text="Findings",
    )
    lines = build_embedding_text(entry).split("\n")
    assert lines == [
        "Halibut",
        "why it's here",
        "Kind: note",
        "Tags: fish",
        "From the source: a post",
        "Picture (plated): white fish on leeks",
        "Caption: the steam",
        "Write-up: Findings",
    ]


def test_the_fingerprint_changes_with_meaning_but_not_with_visibility():
    entry = Entry(title="Halibut", media=[])
    before = meaning_fingerprint(entry)
    entry.visibility = "public"
    assert meaning_fingerprint(entry) == before
    entry.media = [{"type": "image", "url": "/media/a.jpg"}]
    assert meaning_fingerprint(entry) != before


def test_nothing_is_worked_out_without_openrouter():
    assert enrich_entry(Entry(title="t"), existing_tags=[]) is None


def test_tags_and_the_embedding_come_from_every_part(monkeypatch):
    seen: dict = {}
    monkeypatch.setattr(enrichment.openrouter_http, "is_configured", lambda: True)
    monkeypatch.setattr(enrichment, "read_entry_parts", lambda entry, earlier: {"picture /media/a.jpg": "ginger and scallion"})
    monkeypatch.setattr(enrichment, "suggest_tags", lambda **prompt: seen.update(prompt) or ["fish"])
    monkeypatch.setattr(enrichment, "embed_text", lambda text: seen.update(embedded=text) or [1.0, 0.0])

    entry = Entry(title="Halibut", media=[{"type": "image", "url": "/media/a.jpg"}])
    result = enrich_entry(entry, existing_tags=[])

    assert result.tags == ["fish"] and result.embedding == [1.0, 0.0]
    assert "ginger and scallion" in seen["writeup_text"]
    assert "Tags: fish" in seen["embedded"] and "ginger and scallion" in seen["embedded"]
