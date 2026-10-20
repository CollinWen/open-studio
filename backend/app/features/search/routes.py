"""
Search endpoints:

  GET /api/search?q=...    entries matching the query, best match first
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.auth.viewer import Viewer, current_viewer
from app.database import get_db
from app.features.entries.schemas import EntryOut
from app.features.search.service import search_entries

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=list[EntryOut])
def search(q: str = "", db: Session = Depends(get_db), viewer: Viewer = Depends(current_viewer)):
    return search_entries(db, q, viewer)
