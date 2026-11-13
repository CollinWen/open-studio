"""
Tests for the capture service: how what a link reader found becomes the
fields of a draft entry (title, kind, source, date, pictures). The reader is
replaced with a fixed result, so no network calls.
"""

from datetime import datetime, timezone

from app.features.capture import service
from app.integrations.link_readers.link_details import LinkDetails, LinkMedia


def captured_from(monkeypatch, details: LinkDetails):
    monkeypatch.setattr(service, "read_link", lambda url: details)
    return service.capture_link(details.url)


def test_a_reading_fills_every_field_of_the_draft(monkeypatch):
    published = datetime(2024, 3, 9, tzinfo=timezone.utc)
    draft = captured_from(
        monkeypatch,
        LinkDetails(
            url="https://www.youtube.com/watch?v=abc",
            title="Shaping a batard",
            description="Slowed down.",
            kind="video",
            author="Slow Craft",
            platform="YouTube",
            published_at=published,
            media=[LinkMedia(type="embed", url="https://www.youtube-nocookie.com/embed/abc", thumbnail_url="https://i.ytimg.com/abc.jpg")],
        ),
    )

    assert draft.source_url == "https://www.youtube.com/watch?v=abc"
    assert (draft.title, draft.description, draft.kind) == ("Shaping a batard", "Slowed down.", "video")
    assert draft.source_name == "Slow Craft, YouTube"
    assert draft.occurred_at == published
    assert [(item.type, item.url, item.thumbnail_url) for item in draft.media] == [
        ("embed", "https://www.youtube-nocookie.com/embed/abc", "https://i.ytimg.com/abc.jpg")
    ]


def test_source_name_says_each_name_once():
    assert service._source_name("Slow Craft", "YouTube") == "Slow Craft, YouTube"
    assert service._source_name("GitHub", "github") == "GitHub"
    assert service._source_name("", "Google Drive") == "Google Drive"
    assert service._source_name("Collin Wen", "") == "Collin Wen"
    assert service._source_name("", "") == ""


def test_a_bare_reading_still_makes_a_draft(monkeypatch):
    draft = captured_from(monkeypatch, LinkDetails(url="https://example.com/page"))

    assert (draft.title, draft.kind, draft.source_name) == ("", "link", "")
    assert draft.occurred_at is None
    assert draft.media == []
