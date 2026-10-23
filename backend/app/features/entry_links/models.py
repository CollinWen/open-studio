"""
Entry link table: one "builds on" connection. The entry builds on an earlier
one (extends it, answers it, was made because of it), with a short note
saying how. Links chain entries into lines and trees you can walk back to
where an idea started, or forward to what came of it.

Deleting either entry deletes the link (the database does this, see database.py).
"""

import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def _now() -> datetime:
    return datetime.now(timezone.utc)


class EntryLink(SQLModel, table=True):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, primary_key=True)

    # The later entry, and the one it builds on.
    entry_id: str = Field(foreign_key="entry.id", ondelete="CASCADE", index=True)
    builds_on_id: str = Field(foreign_key="entry.id", ondelete="CASCADE", index=True)

    # How it builds on it, in a few words: "extends the crease pattern from".
    note: str = ""

    # "owner", or "agent:<name>", like an entry's added_by.
    added_by: str = "owner"
    created_at: datetime = Field(default_factory=_now)
