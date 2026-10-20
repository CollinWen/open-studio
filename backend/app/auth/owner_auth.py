"""
Owner auth: decides whether a request comes from the site's owner.

This is a single-owner site. The owner proves who they are by sending the
OWNER_TOKEN from backend/.env as a Bearer token. Visitors never need to sign in.
Agents have their own tokens; see auth/viewer.py.
"""

import secrets

from fastapi import Header, HTTPException

from app.config import settings


def is_owner(authorization: str | None) -> bool:
    """True when the Authorization header carries the correct owner token."""
    if not settings.owner_token or not authorization:
        return False
    supplied = authorization.removeprefix("Bearer ").strip()
    return secrets.compare_digest(supplied, settings.owner_token)


def require_owner(authorization: str | None = Header(default=None)) -> None:
    """Route guard for write actions. Rejects anyone who isn't the owner."""
    if not is_owner(authorization):
        raise HTTPException(status_code=401, detail="Owner token required")

