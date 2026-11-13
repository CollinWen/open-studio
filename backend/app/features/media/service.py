"""
Media service: stores write-ups, after making them safe.

A write-up is an entry's illustrated text: plain HTML (headings, paragraphs,
tables, embedded pictures, simple drawings) that the site shows in its own
style. It is sanitized here (writeup_sanitizer.py), then stored as a file
(integrations/media_storage.py), and becomes one `html` item in the entry's
media list. Used by media/routes.py (the owner's upload) and
agent_server/write_tools.py (attach_writeup).
"""

from dataclasses import dataclass

from app.config import settings
from app.features.media.writeup_sanitizer import sanitize_writeup
from app.integrations.media_storage import save_writeup_file


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
    safe_html, removed = sanitize_writeup(html)
    if not safe_html:
        raise EmptyWriteupError("Nothing in this write-up could be kept")
    return StoredWriteup(url=save_writeup_file(safe_html), removed=removed)
