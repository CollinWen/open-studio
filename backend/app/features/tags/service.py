"""
Tag service: every tag in use, how many visible entries have it, and the
owner's description and importance for it.

Ordered key tags first, then by how often they're used. Hidden tags are
left out for visitors and agents (the owner still sees them, to un-hide them).
"""

from collections import Counter

from sqlmodel import Session, select

from app.auth.viewer import Viewer
from app.features.entries import service as entries_service
from app.features.tags.models import HIDDEN, NORMAL, Tag
from app.features.tags.schemas import TagInfo, TagNotes


def list_tags(db: Session, viewer: Viewer) -> list[TagInfo]:
    counts = Counter(
        tag
        for entry in entries_service.list_entries(db, viewer)
        for tag in entry.tags
    )
    notes = {tag.name: tag for tag in db.exec(select(Tag))}

    tags = [
        TagInfo(
            name=name,
            count=count,
            description=notes[name].description if name in notes else "",
            importance=notes[name].importance if name in notes else NORMAL,
        )
        for name, count in counts.items()
    ]
    if not viewer.is_owner:
        tags = [tag for tag in tags if tag.importance != HIDDEN]
    return sorted(tags, key=lambda tag: (-tag.importance, -tag.count, tag.name))


def save_tag_notes(db: Session, name: str, notes: TagNotes) -> Tag:
    """Create or update the description and importance for one tag."""
    tag = db.get(Tag, name) or Tag(name=name)
    tag.description = notes.description
    tag.importance = notes.importance
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag
