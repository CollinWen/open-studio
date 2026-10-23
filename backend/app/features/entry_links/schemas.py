"""
Entry link API shapes: a new "builds on" link, a link as sent back, and a
chain (the entries around one entry and the links between them).
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.features.entries.schemas import EntryOut


class BuildsOnCreate(BaseModel):
    builds_on_id: str
    note: str = ""


class EntryLinkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    entry_id: str
    builds_on_id: str
    note: str
    added_by: str
    created_at: datetime


class Chain(BaseModel):
    """Everything an entry builds on (back to its roots) and everything built on it,
    a few steps each way. Draw it from `links`: each one points from entry_id back to builds_on_id."""

    entry_id: str
    entries: list[EntryOut]
    links: list[EntryLinkOut]
