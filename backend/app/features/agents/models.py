"""
Agent table: every agent the owner has let into the studio (a Claude session,
a research bot, any harness), whether it may work right now, and what it says
it's doing.

An agent has no token of its own: it works on run tokens the owner issues,
one per session (features/runs/). Which boards an agent
may add to is kept on the board (boards/models.py, Board.agents); which
outside tools its runs may use (web, code, github), its skills and its
manifest (its standing job) are kept here.
"""

from datetime import datetime, timezone

from sqlmodel import JSON, Column, Field, SQLModel


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Agent(SQLModel, table=True):
    # Short, lowercase, used in links and in an entry's added_by ("agent:scout").
    name: str = Field(primary_key=True)

    # One line on what it's for, in the owner's words, for the agent lists.
    description: str = ""

    # Its standing job, in the owner's words, written into every run's prompt:
    # its objective, what it focuses on (and doesn't), which tools it uses for
    # what, and what it hands back. Explains its work; grants nothing (boards and
    # tools do). What to do in one session is told to it by its harness instead.
    manifest: str = ""

    # Outside tools its runs may be given (runs/outside_tools.py: web, code, github).
    # The owner grants these; a run gets at most these.
    tools: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    # The skills it works with, by name (folders in skills/, picked from
    # agents/schemas.py's AGENT_SKILLS); every run's prompt tells it to load them.
    skills: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    # A paused agent can still read, like any visitor, but can't add or log anything.
    active: bool = True

    # One line the agent sets on itself: what it's working on right now.
    status: str = ""

    # The last time it called the studio, so the agents page can say who is around.
    last_seen_at: datetime | None = None

    created_at: datetime = Field(default_factory=_now)
