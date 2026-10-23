"""
Page cursor: the bookmark that says where the next page of entries starts,
so a long collection can be loaded a page at a time.

A cursor names the last entry of the page just sent (its date and id).
The next page starts right after it, so entries added in the meantime never
make a page repeat or skip one. Used by entries/service.py.
"""

import base64
from datetime import datetime


class BadCursorError(ValueError):
    """The cursor wasn't one this backend made."""


def make_cursor(occurred_at: datetime, entry_id: str) -> str:
    raw = f"{occurred_at.isoformat()}|{entry_id}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def read_cursor(cursor: str) -> tuple[datetime, str]:
    try:
        when, entry_id = base64.urlsafe_b64decode(cursor.encode()).decode().split("|", 1)
        return datetime.fromisoformat(when), entry_id
    except ValueError as error:
        raise BadCursorError("Not a valid page cursor") from error
