"""
Entry service: the rules for listing, creating, editing and deleting entries,
for each kind of viewer (visitor, agent, owner).

Who can see and edit what lives in entries/visibility_rules.py. Every entry is
on one board; an agent may only add to (or move entries onto) boards it is
signed on to (boards/service.py). Entries added by an agent are recorded with
its name and start unlisted. An agent can't add a second entry for a link
that is already in the studio; it gets the existing one back instead.

Long collections can be read a page at a time (list_entry_page). Other
features (related, search, tags, entry_links, agent_server) read entries
through this file, never through the database directly.
"""

from datetime import datetime, timezone

from sqlalchemy import and_, or_
from sqlmodel import Session, select

from app.auth.viewer import Viewer
from app.features.boards import service as boards_service
from app.features.entries.enrichment import enrich_entry
from app.features.entries.models import Entry
from app.features.entries.page_cursor import make_cursor, read_cursor
from app.features.entries.schemas import EntryCreate, EntryUpdate
from app.features.entries.visibility_rules import AGENT_ENTRY_VISIBILITY, can_open, listing_condition

# Edits to these fields change an entry's meaning, so its embedding is recomputed.
MEANING_FIELDS = {"title", "description", "kind", "source_name", "tags"}
MAX_PAGE_SIZE = 200


class DuplicateLinkError(Exception):
    """An agent tried to add a link that's already an entry. `existing` is None if the agent can't open it."""

    def __init__(self, existing: Entry | None):
        super().__init__("An entry for this link already exists")
        self.existing = existing


class AgentCannotPublishError(Exception):
    """An agent tried to change an entry's visibility; only the owner publishes."""


class UnknownBoardError(Exception):
    """There's no board with that slug."""


class BoardNotAllowedError(Exception):
    """This viewer may not add to that board."""


def list_entries(
    db: Session, viewer: Viewer, board: str | None = None, updated_since: datetime | None = None
) -> list[Entry]:
    """Entries for browsing, newest first. `board` keeps one board (all boards when None);
    `updated_since` keeps only entries added or edited after it."""
    query = select(Entry).where(listing_condition(viewer)).order_by(Entry.occurred_at.desc())
    if board is not None:
        query = query.where(Entry.board == board)
    if updated_since is not None:
        query = query.where(Entry.updated_at > updated_since)
    return list(db.exec(query))


def list_entry_page(
    db: Session, viewer: Viewer, board: str | None, limit: int, cursor: str | None = None
) -> tuple[list[Entry], str | None]:
    """One page of entries, newest first, and the cursor for the next page (None at the end).
    Raises page_cursor.BadCursorError for a cursor this backend didn't make."""
    limit = max(1, min(limit, MAX_PAGE_SIZE))
    query = select(Entry).where(listing_condition(viewer)).order_by(Entry.occurred_at.desc(), Entry.id.desc())
    if board is not None:
        query = query.where(Entry.board == board)
    if cursor:
        last_date, last_id = read_cursor(cursor)
        query = query.where(
            or_(Entry.occurred_at < last_date, and_(Entry.occurred_at == last_date, Entry.id < last_id))
        )
    # One extra row says whether another page follows.
    rows = list(db.exec(query.limit(limit + 1)))
    page = rows[:limit]
    next_cursor = make_cursor(page[-1].occurred_at, page[-1].id) if len(rows) > limit else None
    return page, next_cursor


def get_entry(db: Session, entry_id: str, viewer: Viewer) -> Entry | None:
    """One entry by id, or None if it doesn't exist or this viewer can't see it."""
    entry = db.get(Entry, entry_id)
    if entry is None or not can_open(viewer, entry):
        return None
    return entry


def create_entry(db: Session, data: EntryCreate, viewer: Viewer) -> Entry:
    _check_can_add_to_board(db, viewer, data.board)
    entry = Entry(**data.model_dump(exclude_none=True), added_by=viewer.added_by)
    if viewer.is_agent:
        entry.visibility = AGENT_ENTRY_VISIBILITY
        existing = _find_by_source_url(db, entry.source_url)
        if existing is not None:
            raise DuplicateLinkError(existing if can_open(viewer, existing) else None)
    enrich_entry(entry, existing_tags=_all_tags(db))
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update_entry(db: Session, entry: Entry, changes: EntryUpdate, viewer: Viewer) -> Entry:
    """Change the fields sent. Callers check visibility_rules.can_edit first."""
    changed = {
        field: value
        for field, value in changes.model_dump(exclude_unset=True).items()
        if getattr(entry, field) != value
    }
    if viewer.is_agent and "visibility" in changed:
        raise AgentCannotPublishError("Only the owner can change an entry's visibility")
    if "board" in changed:
        _check_can_add_to_board(db, viewer, changed["board"])
    for field, value in changed.items():
        setattr(entry, field, value)
    entry.updated_at = datetime.now(timezone.utc)

    if MEANING_FIELDS & changed.keys():
        enrich_entry(entry, existing_tags=_all_tags(db))

    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def delete_entry(db: Session, entry: Entry) -> None:
    db.delete(entry)
    db.commit()


def _check_can_add_to_board(db: Session, viewer: Viewer, slug: str) -> None:
    board = boards_service.get_board(db, slug)
    if board is None:
        raise UnknownBoardError(f"No board {slug}")
    if not boards_service.can_add_to_board(viewer, board):
        raise BoardNotAllowedError(f"This agent isn't signed on to the {slug} board")


def _find_by_source_url(db: Session, source_url: str) -> Entry | None:
    if not source_url.strip():
        return None
    return db.exec(select(Entry).where(Entry.source_url == source_url.strip())).first()


def _all_tags(db: Session) -> list[str]:
    """Every tag already in use, so new suggestions reuse them instead of inventing near-duplicates."""
    tags = {tag for entry in db.exec(select(Entry)) for tag in entry.tags}
    return sorted(tags)
