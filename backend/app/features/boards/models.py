"""
Board table: one separate space in the studio. Every entry belongs to exactly
one board. The home board is the owner's own collection, the one the home
page shows; other boards hold a focused effort ("computational folding")
that agents can be signed on to.
"""

from datetime import datetime, timezone

from sqlmodel import JSON, Column, Field, SQLModel

HOME_BOARD = "home"


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Board(SQLModel, table=True):
    # Short, lowercase, used in links: /b/folding
    slug: str = Field(primary_key=True)
    name: str

    # What this board is for and what belongs on it. Agents read this as their brief,
    # so say what to look for and when it's enough.
    description: str = ""

    # Names of the agents (from AGENT_TOKENS) allowed to add entries here.
    # Any agent may read every board.
    agents: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=_now)
