"""
Tag endpoints:

  GET /api/tags           every tag in use, with count, description and importance
  PUT /api/tags/{name}    set a tag's description and importance (owner only)
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.auth.owner_auth import require_owner, viewer_is_owner
from app.database import get_db
from app.features.tags import service
from app.features.tags.schemas import TagInfo, TagNotes

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagInfo])
def list_tags(db: Session = Depends(get_db), is_owner: bool = Depends(viewer_is_owner)):
    return service.list_tags(db, include_private=is_owner)


@router.put("/{name}", response_model=TagNotes, dependencies=[Depends(require_owner)])
def save_tag_notes(name: str, notes: TagNotes, db: Session = Depends(get_db)):
    return service.save_tag_notes(db, name, notes)
