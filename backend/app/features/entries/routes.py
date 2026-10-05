"""
Entry endpoints:

  GET    /api/entries         list entries (owner also sees private/unlisted)
  GET    /api/entries/{id}    one entry
  POST   /api/entries         create (owner only)
  PATCH  /api/entries/{id}    edit (owner only)
  DELETE /api/entries/{id}    delete (owner only)

POST /api/entries is also the capture endpoint: a phone shortcut can call it
directly with the owner token.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.auth.owner_auth import require_owner, viewer_is_owner
from app.database import get_db
from app.features.entries import service
from app.features.entries.schemas import EntryCreate, EntryOut, EntryUpdate

router = APIRouter(prefix="/entries", tags=["entries"])


@router.get("", response_model=list[EntryOut])
def list_entries(db: Session = Depends(get_db), is_owner: bool = Depends(viewer_is_owner)):
    return service.list_entries(db, include_private=is_owner)


@router.get("/{entry_id}", response_model=EntryOut)
def get_entry(entry_id: str, db: Session = Depends(get_db), is_owner: bool = Depends(viewer_is_owner)):
    entry = service.get_entry(db, entry_id, viewer_is_owner=is_owner)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@router.post("", response_model=EntryOut, dependencies=[Depends(require_owner)])
def create_entry(data: EntryCreate, db: Session = Depends(get_db)):
    return service.create_entry(db, data)


@router.patch("/{entry_id}", response_model=EntryOut, dependencies=[Depends(require_owner)])
def update_entry(entry_id: str, changes: EntryUpdate, db: Session = Depends(get_db)):
    entry = service.get_entry(db, entry_id, viewer_is_owner=True)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return service.update_entry(db, entry, changes)


@router.delete("/{entry_id}", status_code=204, dependencies=[Depends(require_owner)])
def delete_entry(entry_id: str, db: Session = Depends(get_db)):
    entry = service.get_entry(db, entry_id, viewer_is_owner=True)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    service.delete_entry(db, entry)
