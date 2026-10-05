"""
Capture API shapes: the link the owner pastes, and the prefilled draft
that comes back for them to check, annotate and save.
"""

from datetime import datetime

from pydantic import BaseModel

from app.features.entries.schemas import MediaItem


class LinkToRead(BaseModel):
    url: str


class CapturedLink(BaseModel):
    """Suggested values for a new entry. Nothing is saved until the owner saves the entry."""

    source_url: str
    title: str
    description: str
    kind: str
    source_name: str
    occurred_at: datetime | None
    media: list[MediaItem]
