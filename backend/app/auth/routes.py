"""
Auth endpoint:

  GET /api/auth/owner    204 when the request carries the owner's sign-in, 401 otherwise

Lets the studio check a password before keeping it, so a mistyped one is
caught at once instead of making every later save fail. It returns nothing:
who may do what is decided where each action lives (auth/owner_auth.py).
"""

from fastapi import APIRouter, Depends

from app.auth.owner_auth import require_owner

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/owner", status_code=204, dependencies=[Depends(require_owner)])
def check_owner_sign_in() -> None:
    return None
