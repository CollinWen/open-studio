"""
Media endpoints:

  POST /api/media    upload one image or video (owner only); returns its URL

The returned URL becomes one item in an entry's media list. Storage details live in
integrations/media_storage.py.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.auth.owner_auth import require_owner
from app.integrations.media_storage import save_media_file

router = APIRouter(prefix="/media", tags=["media"])


@router.post("", dependencies=[Depends(require_owner)])
async def upload_media(file: UploadFile) -> dict[str, str]:
    try:
        url = save_media_file(file.filename or "", await file.read())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return {"url": url}
