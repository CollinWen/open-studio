"""
Entry API shapes: what the frontend sends to create or edit an entry,
and what it gets back. The embedding is never sent to the browser.
"""

from datetime import datetime, timezone
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel

Visibility = Literal["private", "unlisted", "public"]


def _assume_utc(value: datetime) -> datetime:
    """A plain date like "2024-05-01" has no timezone; treat it as UTC."""
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


UtcDatetime = Annotated[datetime, AfterValidator(_assume_utc)]


class MediaItem(BaseModel):
    """One picture or video in an entry.

    image: shown with <img>.  video: a video file.  embed: a player page in an
    iframe (YouTube, Drive video). thumbnail_url is the still used as a cover.
    """

    type: Literal["image", "video", "embed"]
    url: str
    thumbnail_url: str = ""
    caption: str = ""


class EntryCreate(BaseModel):
    title: str
    description: str = ""
    kind: str = "note"
    source_name: str = ""
    source_url: str = ""
    media: list[MediaItem] = []
    occurred_at: UtcDatetime | None = None
    visibility: Visibility = "private"
    # Leave empty to have tags suggested automatically.
    tags: list[str] = []


class EntryUpdate(BaseModel):
    """Every field is optional: only the fields sent are changed."""

    title: str | None = None
    description: str | None = None
    kind: str | None = None
    source_name: str | None = None
    source_url: str | None = None
    media: list[MediaItem] | None = None
    occurred_at: UtcDatetime | None = None
    visibility: Visibility | None = None
    tags: list[str] | None = None


class EntryOut(BaseModel):
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
