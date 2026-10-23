"""
Entry link endpoints:

  GET    /api/entries/{id}/chain        what this entry builds on and what builds on it
  POST   /api/entries/{id}/builds-on    say this entry builds on another {builds_on_id, note}
                                        (owner, or an agent on agents' unpublished entries)
  DELETE /api/entry-links/{link_id}     remove a link (same rule)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.auth.viewer import Viewer, current_viewer, require_writer
from app.database import get_db
from app.features.entries import service as entries_service
from app.features.entry_links import service
from app.features.entry_links.schemas import BuildsOnCreate, Chain, EntryLinkOut

router = APIRouter(tags=["entry links"])


@router.get("/entries/{entry_id}/chain", response_model=Chain)
def get_chain(entry_id: str, db: Session = Depends(get_db), viewer: Viewer = Depends(current_viewer)):
    entry = entries_service.get_entry(db, entry_id, viewer)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    entries, links = service.find_chain(db, viewer, entry)
    return Chain(entry_id=entry.id, entries=entries, links=links)


@router.post("/entries/{entry_id}/builds-on", response_model=EntryLinkOut)
def add_builds_on(
    entry_id: str,
    body: BuildsOnCreate,
    db: Session = Depends(get_db),
    viewer: Viewer = Depends(require_writer),
):
    entry = entries_service.get_entry(db, entry_id, viewer)
    builds_on = entries_service.get_entry(db, body.builds_on_id, viewer)
    if entry is None or builds_on is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    try:
        return service.add_builds_on(db, viewer, entry, builds_on, body.note)
    except service.LinkNotAllowedError as error:
        raise HTTPException(status_code=403, detail=str(error))


@router.delete("/entry-links/{link_id}", status_code=204)
def remove_link(link_id: str, db: Session = Depends(get_db), viewer: Viewer = Depends(require_writer)):
    link = service.get_link(db, link_id)
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    try:
        service.remove_link(db, viewer, link)
    except service.LinkNotAllowedError as error:
        raise HTTPException(status_code=403, detail=str(error))
