"""
Agent table: every agent the owner has let into the studio (a Claude session,
a research bot), whether it may work right now, and what it says it's doing.

Its token is never stored, only a fingerprint of it (agent_tokens.py), so a
copy of the database can't be used to act as an agent. Which boards an agent
may add to is kept on the board (boards/models.py, Board.agents).
"""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Agent(SQLModel, table=True):
    # Short, lowercase, used in links and in an entry's added_by ("agent:scout").
    name: str = Field(primary_key=True)

    # What this agent is and what it's for, in the owner's words.
    description: str = ""

    # A fingerprint of the agent's token (see agent_tokens.py), never the token itself.
    token_hash: str = Field(index=True)

    # A paused agent can still read, like any visitor, but can't add or log anything.
    active: bool = True

    # One line the agent sets on itself: what it's working on right now.
    status: str = ""

    # The last time it called the studio, so the agents page can say who is around.
    last_seen_at: datetime | None = None

    created_at: datetime = Field(default_factory=_now)
