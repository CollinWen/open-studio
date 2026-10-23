"""
Tag endpoints:

  GET /api/tags           every tag in use, with count, description and importance (?board= for one board)
  PUT /api/tags/{name}    set a tag's description and importance (owner only)
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.auth.owner_auth import require_owner
from app.auth.viewer import Viewer, current_viewer
from app.database import get_db
from app.features.tags import service
from app.features.tags.schemas import TagInfo, TagNotes

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagInfo])
def list_tags(board: str | None = None, db: Session = Depends(get_db), viewer: Viewer = Depends(current_viewer)):
    return service.list_tags(db, viewer, board=board)


@router.put("/{name}", response_model=TagNotes, dependencies=[Depends(require_owner)])
def save_tag_notes(name: str, notes: TagNotes, db: Session = Depends(get_db)):
    return service.save_tag_notes(db, name, notes)
