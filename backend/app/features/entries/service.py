"""
Entry service: the rules for listing, creating, editing and deleting entries,
for each kind of viewer (visitor, agent, owner).

Who can see and edit what lives in entries/visibility_rules.py. Entries added
by an agent are recorded with its name and start unlisted. An agent can't add
a second entry for a link that is already in the studio; it gets the existing
one back instead, so many agents researching the same thing don't pile up copies.

Other features (related, search, tags, agent_server) read entries through this
file, never through the database directly.
"""

from datetime import datetime, timezone

from sqlmodel import Session, select

from app.auth.viewer import Viewer
from app.features.entries.enrichment import enrich_entry
from app.features.entries.models import Entry
from app.features.entries.schemas import EntryCreate, EntryUpdate
from app.features.entries.visibility_rules import AGENT_ENTRY_VISIBILITY, can_open, listing_condition

# Edits to these fields change an entry's meaning, so its embedding is recomputed.
MEANING_FIELDS = {"title", "description", "kind", "source_name", "tags"}


class DuplicateLinkError(Exception):
    """An agent tried to add a link that's already an entry. `existing` is None if the agent can't open it."""

    def __init__(self, existing: Entry | None):
        super().__init__("An entry for this link already exists")
        self.existing = existing


class AgentCannotPublishError(Exception):
    """An agent tried to change an entry's visibility; only the owner publishes."""


def list_entries(db: Session, viewer: Viewer, updated_since: datetime | None = None) -> list[Entry]:
    """Entries for browsing, newest first. `updated_since` keeps only entries added or edited after it."""
    query = select(Entry).where(listing_condition(viewer)).order_by(Entry.occurred_at.desc())
    if updated_since is not None:
        query = query.where(Entry.updated_at > updated_since)
    return list(db.exec(query))


def get_entry(db: Session, entry_id: str, viewer: Viewer) -> Entry | None:
    """One entry by id, or None if it doesn't exist or this viewer can't see it."""
    entry = db.get(Entry, entry_id)
    if entry is None or not can_open(viewer, entry):
        return None
    return entry


def create_entry(db: Session, data: EntryCreate, viewer: Viewer) -> Entry:
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


def _find_by_source_url(db: Session, source_url: str) -> Entry | None:
    if not source_url.strip():
        return None
    return db.exec(select(Entry).where(Entry.source_url == source_url.strip())).first()


def _all_tags(db: Session) -> list[str]:
    """Every tag already in use, so new suggestions reuse them instead of inventing near-duplicates."""
    tags = {tag for entry in db.exec(select(Entry)) for tag in entry.tags}
    return sorted(tags)
