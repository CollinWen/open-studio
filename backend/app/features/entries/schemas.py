"""
Entry API shapes: what the frontend sends to create or edit an entry,
and what it gets back. The embedding is never sent to the browser.
An entry's media may include a write-up (type html) only if the studio
stored it, so it was made safe on the way in (media/service.py).
"""

from datetime import datetime, timezone
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict

from app.integrations.media_storage import is_stored_writeup_url

Visibility = Literal["private", "unlisted", "public"]


def _assume_utc(value: datetime) -> datetime:
    """A plain date like "2024-05-01" has no timezone; treat it as UTC."""
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


UtcDatetime = Annotated[datetime, AfterValidator(_assume_utc)]


class MediaItem(BaseModel):
    """One picture, video or write-up in an entry.

    image: shown with <img>.  video: a video file.  embed: a player page in an
    iframe (YouTube, Drive video).  html: a write-up, shown in the site's own
    style. thumbnail_url is the still used as a cover.
    """

    type: Literal["image", "video", "embed", "html"]
    url: str
    thumbnail_url: str = ""
    caption: str = ""


def _only_stored_writeups(media: list[MediaItem] | None) -> list[MediaItem] | None:
    for item in media or []:
        if item.type == "html" and not is_stored_writeup_url(item.url):
            raise ValueError("A write-up must be stored by the studio first (attach_writeup, or upload the .html)")
    return media


SentMedia = Annotated[list[MediaItem], AfterValidator(_only_stored_writeups)]


class EntryCreate(BaseModel):
    """Agents' entries are always saved unlisted, whatever `visibility` says."""

    title: str
    description: str = ""
    kind: str = "note"
    source_name: str = ""
    source_url: str = ""
    media: SentMedia = []
    occurred_at: UtcDatetime | None = None
    visibility: Visibility = "private"
    board: str = "home"
    # Leave empty to have tags suggested automatically.
    tags: list[str] = []


class EntryUpdate(BaseModel):
    """Every field is optional: only the fields sent are changed."""

    title: str | None = None
    description: str | None = None
    kind: str | None = None
    source_name: str | None = None
    source_url: str | None = None
    media: SentMedia | None = None
    occurred_at: UtcDatetime | None = None
    visibility: Visibility | None = None
    tags: list[str] | None = None
    board: str | None = None


class EntryOut(BaseModel):
    # Built straight from a stored Entry (routes and the agent server's tools).
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    kind: str
    source_name: str
    source_url: str
    media: list[MediaItem]
    occurred_at: datetime
    created_at: datetime
    updated_at: datetime
    visibility: Visibility
    tags: list[str]
    added_by: str
    board: str


class EntryPage(BaseModel):
    """One page of entries, newest first. Pass next_cursor back to get the page after; null at the end."""

    entries: list[EntryOut]
    next_cursor: str | None
