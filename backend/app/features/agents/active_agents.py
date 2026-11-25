"""
Active agents: the agent a run token names, if it's still there and not
paused, noting when it was last seen (at most once a minute, so reads stay
cheap).

Used by auth/viewer.py on every request that carries a run token. Kept apart
from service.py so auth can use it without pulling in the boards feature.
Agents have no token of their own: every token is a run (features/runs/).
"""

from datetime import datetime, timedelta, timezone

from sqlmodel import Session

from app.features.agents.models import Agent

SEEN_EVERY = timedelta(minutes=1)


def find_active_agent_by_name(db: Session, name: str) -> Agent | None:
    """The agent a run token names, if it's still there and not paused. Notes that it was seen."""
    agent = db.get(Agent, name)
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
