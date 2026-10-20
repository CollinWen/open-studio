"""
Related endpoints:

  GET /api/entries/{id}/related    entries closest in meaning to this one
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.auth.viewer import Viewer, current_viewer
from app.database import get_db
from app.features.entries import service as entries_service
from app.features.entries.schemas import EntryOut
from app.features.related.service import find_related_entries

router = APIRouter(tags=["related"])


@router.get("/entries/{entry_id}/related", response_model=list[EntryOut])
def related_entries(entry_id: str, db: Session = Depends(get_db), viewer: Viewer = Depends(current_viewer)):
    entry = entries_service.get_entry(db, entry_id, viewer)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return find_related_entries(db, entry, viewer)
