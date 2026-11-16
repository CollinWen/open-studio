"""
Tests for reading an entry's parts: the source link through the link readers,
each picture (an image itself, a video's or embed's still) described, the
write-up left to writeup_text; parts already read are reused, and a part that
couldn't be read is left out so it's tried again.
"""

import pytest

from app.features.entries import entry_reading
from app.features.entries.models import Entry
from app.integrations.link_readers.link_details import LinkDetails


@pytest.fixture
def reads(monkeypatch) -> list[str]:
    calls: list[str] = []

    def fake_picture(url, caption=""):
        calls.append(url)
        return "" if "broken" in url else f"seen {url}"

    def fake_link(url):
        calls.append(url)
        return LinkDetails(url=url, title="Halibut en papillote", author="A cook", platform="YouTube",
                           description="Steam the halibut with ginger and scallion.")

    monkeypatch.setattr(entry_reading, "read_picture", fake_picture)
    monkeypatch.setattr(entry_reading, "read_link", fake_link)
    return calls


def _entry(**fields) -> Entry:
    return Entry(title="t", **fields)


def test_each_kind_of_part_is_read_its_own_way(reads):
    entry = _entry(
        source_url="https://youtu.be/abc",
        media=[
            {"type": "image", "url": "/media/a.jpg"},
            {"type": "embed", "url": "https://www.youtube.com/embed/abc", "thumbnail_url": "https://i.ytimg.com/abc.jpg"},
            {"type": "video", "url": "/media/clip.mp4"},
            {"type": "html", "url": "/media/w.html"},
        ],
    )
    readings = entry_reading.read_entry_parts(entry, earlier={})
    assert readings == {
        "source https://youtu.be/abc": "YouTube: Halibut en papillote\nBy A cook\nSteam the halibut with ginger and scallion.",
        "picture /media/a.jpg": "seen /media/a.jpg",
        "picture https://i.ytimg.com/abc.jpg": "seen https://i.ytimg.com/abc.jpg",
    }


def test_parts_already_read_are_reused(reads):
    entry = _entry(media=[{"type": "image", "url": "/media/a.jpg"}, {"type": "image", "url": "/media/b.jpg"}])
    readings = entry_reading.read_entry_parts(entry, earlier={"picture /media/a.jpg": "read before", "picture /media/gone.jpg": "x"})
    assert readings == {"picture /media/a.jpg": "read before", "picture /media/b.jpg": "seen /media/b.jpg"}
    assert reads == ["/media/b.jpg"]


def test_a_part_that_couldnt_be_read_is_left_out(reads):
    entry = _entry(media=[{"type": "image", "url": "/media/broken.jpg"}])
    assert entry_reading.read_entry_parts(entry, earlier={}) == {}
