"""
Entry table: how one thing in the collection is stored in the database.

An entry is the core unit of the site: a project, a sketch, a book, a link,
a recipe. Tags and the embedding are filled in automatically by enrichment.py.
"""

import uuid
from datetime import datetime, timezone

from sqlmodel import JSON, Column, Field, SQLModel


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Entry(SQLModel, table=True):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, primary_key=True)

    # What it is, in my words. `description` is "why it's here", the most important field.
    title: str
    description: str = ""
    kind: str = "note"  # medium: note, link, book, artwork, sketch, project, recipe, video, ...

    # Where it came from, for things made by someone else.
    source_name: str = ""
    source_url: str = ""

    # Pictures and videos, in display order. The first one is the cover in the grid.
    # Each item: {type: image | video | embed, url, thumbnail_url, caption}. See schemas.MediaItem.
    # Uploaded files are stored untouched (full resolution); linked ones (YouTube, Drive) are not copied.
    media: list[dict] = Field(default_factory=list, sa_column=Column(JSON))

    # When it happened (can be in the past, for backfilling), and system timestamps.
    occurred_at: datetime = Field(default_factory=_now)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)

    # private: only me. unlisted: anyone with the link. public: in the grid.
    visibility: str = "private"

    # Short, plain labels. Suggested by an LLM, editable afterwards.
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Meaning-as-numbers, used to find "Related" entries. Empty until computed.
    embedding: list[float] | None = Field(default=None, sa_column=Column(JSON))
    embedding_model: str = ""
