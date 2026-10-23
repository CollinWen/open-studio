"""
Entry link service: adding and removing "builds on" links, and finding the
chain around an entry.

A link can't point an entry at itself, be added twice, or close a loop
(A builds on B builds on A), so chains always run one way, from roots to
later work. Who may add a link: the owner, or an agent on an entry it may
edit (visibility_rules.can_edit), pointing at any entry it can see.
Entries are read through entries/service.py.
"""

from sqlmodel import Session, or_, select

from app.auth.viewer import Viewer
from app.features.entries import service as entries_service
from app.features.entries.models import Entry
from app.features.entries.visibility_rules import can_edit, can_list
from app.features.entry_links.models import EntryLink

# How many steps a chain reaches back to roots, and forward to later work.
CHAIN_STEPS = 4
MAX_CHAIN_ENTRIES = 80


class LinkNotAllowedError(Exception):
    """This link can't be made: self-link, duplicate, loop, or not this viewer's to make."""


def add_builds_on(db: Session, viewer: Viewer, entry: Entry, builds_on: Entry, note: str) -> EntryLink:
    if not can_edit(viewer, entry):
        raise LinkNotAllowedError("Agents can only link from agents' unpublished entries")
    if entry.id == builds_on.id:
        raise LinkNotAllowedError("An entry can't build on itself")
    if _find_link(db, entry.id, builds_on.id) is not None:
        raise LinkNotAllowedError("That link is already there")
    if entry.id in _reachable(db, builds_on.id, direction="back", steps=None):
        raise LinkNotAllowedError("That would make a loop: the other entry already builds on this one")
    link = EntryLink(
        entry_id=entry.id, builds_on_id=builds_on.id, note=note.strip(), added_by=viewer.added_by
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def get_link(db: Session, link_id: str) -> EntryLink | None:
    return db.get(EntryLink, link_id)


def remove_link(db: Session, viewer: Viewer, link: EntryLink) -> None:
    entry = entries_service.get_entry(db, link.entry_id, viewer)
    if entry is None or not can_edit(viewer, entry):
        raise LinkNotAllowedError("Agents can only remove links from agents' unpublished entries")
    db.delete(link)
    db.commit()


def find_chain(db: Session, viewer: Viewer, entry: Entry) -> tuple[list[Entry], list[EntryLink]]:
    """The entries a few steps back and forward from this one that this viewer can see, and their links."""
    ids = (
        {entry.id}
        | _reachable(db, entry.id, direction="back", steps=CHAIN_STEPS)
        | _reachable(db, entry.id, direction="forward", steps=CHAIN_STEPS)
    )
    entries = [entry] + [
        other
        for other_id in ids - {entry.id}
        if (other := entries_service.get_entry(db, other_id, viewer)) is not None and can_list(viewer, other)
    ]
    entries = entries[:MAX_CHAIN_ENTRIES]
    shown = {other.id for other in entries}
    links = [
        link for link in _links_touching(db, shown) if link.entry_id in shown and link.builds_on_id in shown
    ]
    return entries, links


def _reachable(db: Session, start_id: str, direction: str, steps: int | None) -> set[str]:
    """Ids reached from start by following links back (to what it builds on) or forward. steps=None: no limit."""
    found: set[str] = set()
    frontier = {start_id}
    step = 0
    while frontier and (steps is None or step < steps):
        if direction == "back":
            query = select(EntryLink.builds_on_id).where(EntryLink.entry_id.in_(frontier))
        else:
            query = select(EntryLink.entry_id).where(EntryLink.builds_on_id.in_(frontier))
        frontier = set(db.exec(query)) - found - {start_id}
        found |= frontier
        step += 1
    return found


def _links_touching(db: Session, ids: set[str]) -> list[EntryLink]:
    query = select(EntryLink).where(or_(EntryLink.entry_id.in_(ids), EntryLink.builds_on_id.in_(ids)))
    return list(db.exec(query.order_by(EntryLink.created_at)))


def _find_link(db: Session, entry_id: str, builds_on_id: str) -> EntryLink | None:
    query = select(EntryLink).where(EntryLink.entry_id == entry_id, EntryLink.builds_on_id == builds_on_id)
    return db.exec(query).first()
