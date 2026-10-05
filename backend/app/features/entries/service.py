"""
Entry service: the rules for listing, creating, editing and deleting entries,
including who can see what.

Visibility rules:
  public   - shown in the home grid and to everyone
  unlisted - hidden from the grid, but anyone with the direct link can open it
  private  - only the owner sees it

Other features (related, tags) read entries through this file, never
through the database directly.
"""

from datetime import datetime, timezone

from sqlmodel import Session, select

from app.features.entries.enrichment import enrich_entry
from app.features.entries.models import Entry
from app.features.entries.schemas import EntryCreate, EntryUpdate

# Edits to these fields change an entry's meaning, so its embedding is recomputed.
MEANING_FIELDS = {"title", "description", "kind", "source_name", "tags"}


def list_entries(db: Session, include_private: bool = False) -> list[Entry]:
    """Entries for browsing, newest first. Visitors get public ones only."""
    query = select(Entry).order_by(Entry.occurred_at.desc())
    if not include_private:
        query = query.where(Entry.visibility == "public")
    return list(db.exec(query))


def get_entry(db: Session, entry_id: str, viewer_is_owner: bool = False) -> Entry | None:
    """One entry by id, or None if it doesn't exist or this viewer can't see it."""
    entry = db.get(Entry, entry_id)
    if entry is None:
        return None
    if entry.visibility == "private" and not viewer_is_owner:
        return None
    return entry


def create_entry(db: Session, data: EntryCreate) -> Entry:
    entry = Entry(**data.model_dump(exclude_none=True))
    enrich_entry(entry, existing_tags=_all_tags(db))
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update_entry(db: Session, entry: Entry, changes: EntryUpdate) -> Entry:
    changed = {
        field: value
        for field, value in changes.model_dump(exclude_unset=True).items()
        if getattr(entry, field) != value
    }
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


def _all_tags(db: Session) -> list[str]:
    """Every tag already in use, so new suggestions reuse them instead of inventing near-duplicates."""
    tags = {tag for entry in db.exec(select(Entry)) for tag in entry.tags}
    return sorted(tags)
