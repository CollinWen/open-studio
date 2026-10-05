"""
Capture endpoints:

  POST /api/capture/link    read a link (YouTube, Google Drive, GitHub, any page)
                            and return a prefilled entry draft (owner only)

Nothing is saved here. The draft goes back to the studio form; saving it
uses POST /api/entries as usual.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.auth.owner_auth import require_owner
from app.features.capture.schemas import CapturedLink, LinkToRead
from app.features.capture.service import capture_link
from app.integrations.link_readers.link_details import LinkReadError

router = APIRouter(prefix="/capture", tags=["capture"])


@router.post("/link", response_model=CapturedLink, dependencies=[Depends(require_owner)])
def read_link(body: LinkToRead):
    try:
        return capture_link(body.url)
    except LinkReadError as error:
        raise HTTPException(status_code=422, detail=str(error))
