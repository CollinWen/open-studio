"""
Media endpoints:

  POST /api/media    upload one image, video or write-up (owner only); returns its URL

The returned URL becomes one item in an entry's media list. Pictures and
videos are stored untouched (integrations/media_storage.py); a write-up
(.html) is made safe first, and the answer says what was removed
(media/service.py).
"""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.auth.owner_auth import require_owner
from app.features.media import service
from app.integrations.media_storage import WRITEUP_EXTENSION, save_media_file

router = APIRouter(prefix="/media", tags=["media"])


@router.post("", dependencies=[Depends(require_owner)])
async def upload_media(file: UploadFile) -> dict[str, str | list[str]]:
    name = file.filename or ""
    content = await file.read()
    try:
        if Path(name).suffix.lower() == WRITEUP_EXTENSION:
            stored = service.store_writeup(content.decode("utf-8", errors="replace"))
            return {"url": stored.url, "removed": stored.removed}
        return {"url": save_media_file(name, content)}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
