"""
Owner auth: decides whether a request comes from the site's owner.

This is a single-owner site. The owner proves who they are by sending the
OWNER_TOKEN from backend/.env (the admin password) as a Bearer token.
Visitors never need to sign in. Agents have their own tokens; see auth/viewer.py.

Every part of the backend asks is_owner, so this is the one place to change
to sign in with Google instead: have is_owner also accept a Firebase ID token
for the owner's Google account (checked against Google's public keys, e.g.
with the firebase-admin package), and keep the password for scripts, deploys
and the iOS app. The browser side is frontend/src/api/ownerSignIn.ts.
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

