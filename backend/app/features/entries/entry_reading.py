"""
Entry reading: turns each part of an entry into words, so everything in it
(not only its title and description) shapes its tags, Related and search.
Each kind of part has its own way of being read:

  source link    the link's own words, through the link readers: a YouTube
                 video's title and description, an Instagram post's caption,
                 an X post's text, a web page's summary
  image          described by a model that can see (media/picture_reader.py)
  video, embed   their still (thumbnail) described the same way; a video file
                 with no still isn't read
  html           a write-up: its words are already kept as writeup_text

The result is the entry's readings: one short text per part, keyed by what
was read ("source <url>", "picture <url>"). A part already read is never read
again (pictures cost a call, and Instagram's picture addresses stop working
after a few weeks), unless the owner asks to read the entry again.

Used by enrichment.py. Readings are never shown to visitors.
"""

import logging

from app.config import settings
from app.features.entries.models import Entry
from app.features.media.picture_reader import read_picture
from app.integrations.link_readers.read_link import read_link

log = logging.getLogger(__name__)


def read_entry_parts(entry: Entry, earlier: dict[str, str]) -> dict[str, str]:
    """The readings for every part the entry has now, reusing `earlier` ones."""
    readings: dict[str, str] = {}
    if entry.source_url.strip():
        key = source_key(entry.source_url.strip())
        readings[key] = earlier.get(key) or _read_source(entry.source_url.strip())

    for item in entry.media[: settings.pictures_read_per_entry]:
        picture = picture_address(item)
        if not picture:
            continue
        key = picture_key(picture)
        readings[key] = earlier.get(key) or _read_picture(picture, item.get("caption", ""))

    # A part that couldn't be read is left out, so it's tried again next time.
    return {key: text for key, text in readings.items() if text}


def picture_address(item: dict) -> str:
    """The picture to read for a media item: an image itself, a video's or embed's still; "" for none."""
    if item.get("type") == "html":
        return ""
    return item.get("url", "") if item.get("type") == "image" else item.get("thumbnail_url", "")


def source_key(url: str) -> str:
    return f"source {url}"


def picture_key(url: str) -> str:
    return f"picture {url}"


def _read_source(url: str) -> str:
    try:
        details = read_link(url)
    except Exception:
        log.warning("Couldn't read the source link %s", url, exc_info=True)
        return ""
    parts = [
        f"{details.platform}: {details.title}" if details.platform else details.title,
        f"By {details.author}" if details.author else "",
        details.description[: settings.source_text_for_meaning],
    ]
    return "\n".join(part for part in parts if part.strip())


def _read_picture(url: str, caption: str) -> str:
    try:
        return read_picture(url, caption)
    except Exception:
        log.warning("Couldn't read the picture %s", url, exc_info=True)
        return ""
