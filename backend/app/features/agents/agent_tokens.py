"""
Agent tokens: making a new token, and finding which agent a token belongs to.

Only a fingerprint (SHA-256) of each token is stored, so the token itself is
shown to the owner once, when it's made, and never again. Finding an agent
also notes when it was last seen (at most once a minute, so reads stay cheap).

Used by auth/viewer.py on every request and by agents/service.py. Kept apart
from service.py so auth can use it without pulling in the boards feature.
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app.features.agents.models import Agent

TOKEN_BYTES = 32
SEEN_EVERY = timedelta(minutes=1)


def make_token() -> str:
    return secrets.token_urlsafe(TOKEN_BYTES)


def fingerprint(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def find_active_agent(db: Session, token: str) -> Agent | None:
    """The active agent this token belongs to, or None. Notes that it was seen."""
    agent = db.exec(select(Agent).where(Agent.token_hash == fingerprint(token))).first()
    if agent is None or not agent.active:
        return None
    _note_seen(db, agent)
    return agent


def _note_seen(db: Session, agent: Agent) -> None:
    now = datetime.now(timezone.utc)
    last = agent.last_seen_at
    if last is not None and last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)  # SQLite gives times back without a zone
    if last is None or now - last >= SEEN_EVERY:
        agent.last_seen_at = now
        db.add(agent)
        db.commit()
