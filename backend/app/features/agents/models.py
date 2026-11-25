"""
Agent table: every agent the owner has let into the studio (a Claude session,
a research bot, any harness), whether it may work right now, and what it says
it's doing.

An agent has no token of its own: it works on run tokens the owner issues,
one per session (features/runs/). Which boards an agent
may add to is kept on the board (boards/models.py, Board.agents); which
outside tools its runs may use (web, code, github), its skills and its
toolkits (the outside services it may use through the studio) are kept here.
"""

from datetime import datetime, timezone

from sqlmodel import JSON, Column, Field, SQLModel


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Agent(SQLModel, table=True):
    # Short, lowercase, used in links and in an entry's added_by ("agent:scout").
    name: str = Field(primary_key=True)

    # What this agent is and what it's for, in the owner's words.
    description: str = ""

    # Outside tools its runs may be given (runs/task_kinds.py: web, code, github).
    # The owner grants these; a run gets at most these.
    tools: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    # The skills it works with, by name (folders in the agent resources, e.g.
    # "gathering-sources"); every run's prompt tells it to load them.
    skills: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Toolkits it may use through the studio (features/toolkits/), by toolkit name: each a
    # toolkits/schemas.py ToolkitGrant (its tools, the account it acts as, pinned arguments).
    toolkits: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # A paused agent can still read, like any visitor, but can't add or log anything.
    active: bool = True

    # One line the agent sets on itself: what it's working on right now.
    status: str = ""

    # The last time it called the studio, so the agents page can say who is around.
    last_seen_at: datetime | None = None

    created_at: datetime = Field(default_factory=_now)
