"""
Media service: stores write-ups, after making them safe.

A write-up is an entry's illustrated text: plain HTML (headings, paragraphs,
tables, layout, embedded pictures, drawings) that the site shows in its own
style. It is sanitized here (writeup_sanitizer.py), then stored as a file
(integrations/media_storage.py), and becomes one `html` item in the entry's
media list. Used by media/routes.py (the owner's upload) and
agent_server/write_tools.py (attach_writeup). entries/service.py reads the
words back (read_writeup_text) for tags, Related and search.
"""

import logging
from dataclasses import dataclass

from app.config import settings
from app.features.media.writeup_sanitizer import sanitize_writeup
from app.integrations.media_storage import is_stored_writeup_url, read_stored_writeup, save_writeup_file

log = logging.getLogger(__name__)


class EmptyWriteupError(ValueError):
    pass


class WriteupTooLargeError(ValueError):
    pass


@dataclass
class StoredWriteup:
    url: str
    removed: list[str]


def store_writeup(html: str) -> StoredWriteup:
    """Sanitize and store a write-up; says what was removed on the way in."""
    if len(html.encode("utf-8")) > settings.writeup_max_bytes:
        limit = settings.writeup_max_bytes // 1_000_000
        raise WriteupTooLargeError(f"A write-up can be at most {limit} MB, embedded pictures included")
    sanitized = sanitize_writeup(html)
    if not sanitized.html:
        raise EmptyWriteupError("Nothing in this write-up could be kept")
    return StoredWriteup(url=save_writeup_file(sanitized.html), removed=sanitized.removed)


def read_writeup_text(media: list[dict]) -> str:
    """The words in an entry's write-ups, one after another. A write-up that can't be
    read is skipped (the entry still saves; its words are picked up on the next media change)."""
    texts = []
    for item in media:
        url = item.get("url", "")
        if item.get("type") != "html" or not is_stored_writeup_url(url):
            continue
        try:
            texts.append(sanitize_writeup(read_stored_writeup(url)).text)
        except Exception:
            log.exception("Couldn't read the write-up at %s", url)
    return "\n".join(text for text in texts if text)
