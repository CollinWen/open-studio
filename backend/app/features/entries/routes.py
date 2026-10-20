"""
Entry endpoints:

  GET    /api/entries         list entries (owner also sees private/unlisted)
                              ?updated_since=<date> keeps only entries added or edited after it
  GET    /api/entries/{id}    one entry
  POST   /api/entries         create (owner, or an agent: saved unlisted)
  PATCH  /api/entries/{id}    edit (owner, or an agent on agents' unpublished entries)
  DELETE /api/entries/{id}    delete (owner only)

POST /api/entries is also the capture endpoint: a phone shortcut can call it
directly with the owner token. Agents usually come in through agent_server/ (MCP)
instead, which uses the same service.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.auth.owner_auth import require_owner
from app.auth.viewer import Viewer, current_viewer, require_writer
from app.database import get_db
from app.features.entries import service
from app.features.entries.schemas import EntryCreate, EntryOut, EntryUpdate
from app.features.entries.visibility_rules import can_edit

router = APIRouter(prefix="/entries", tags=["entries"])


@router.get("", response_model=list[EntryOut])
def list_entries(
    updated_since: datetime | None = None,
    db: Session = Depends(get_db),
    viewer: Viewer = Depends(current_viewer),
):
    if updated_since is not None and updated_since.tzinfo is None:
        updated_since = updated_since.replace(tzinfo=timezone.utc)
    return service.list_entries(db, viewer, updated_since=updated_since)


@router.get("/{entry_id}", response_model=EntryOut)
def get_entry(entry_id: str, db: Session = Depends(get_db), viewer: Viewer = Depends(current_viewer)):
    entry = service.get_entry(db, entry_id, viewer)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@router.post("", response_model=EntryOut)
def create_entry(data: EntryCreate, db: Session = Depends(get_db), viewer: Viewer = Depends(require_writer)):
    try:
        return service.create_entry(db, data, viewer)
    except service.DuplicateLinkError as error:
        existing_id = error.existing.id if error.existing else None
        raise HTTPException(status_code=409, detail={"message": str(error), "existing_id": existing_id})


@router.patch("/{entry_id}", response_model=EntryOut)
def update_entry(
    entry_id: str,
    changes: EntryUpdate,
    db: Session = Depends(get_db),
    viewer: Viewer = Depends(require_writer),
):
    entry = service.get_entry(db, entry_id, viewer)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    if not can_edit(viewer, entry):
        raise HTTPException(status_code=403, detail="Agents can only edit agents' unpublished entries")
    try:
        return service.update_entry(db, entry, changes, viewer)
    except service.AgentCannotPublishError as error:
        raise HTTPException(status_code=403, detail=str(error))


@router.delete("/{entry_id}", status_code=204, dependencies=[Depends(require_owner)])
def delete_entry(entry_id: str, db: Session = Depends(get_db), viewer: Viewer = Depends(current_viewer)):
    entry = service.get_entry(db, entry_id, viewer)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    service.delete_entry(db, entry)
