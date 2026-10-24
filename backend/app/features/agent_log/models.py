"""
Agent log table: one line an agent wrote about its work, so anyone can see
what every agent is planning, thinking, finding and asking, as it goes.

A line is about one board (or none, for a status that isn't tied to one) and
may point at the entry it's about. Lines are kept when their agent is
removed, signed with its name, like the entries it added.
"""

import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

# What a line is, in the order an agent's work tends to go.
LINE_TYPES = ("plan", "thought", "finding", "question", "status")


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AgentLogLine(SQLModel, table=True):
    __tablename__ = "agent_log_line"

    id: str = Field(default_factory=lambda: uuid.uuid4().hex, primary_key=True)
    agent: str = Field(index=True)
    board: str | None = Field(default=None, index=True)
    type: str
    text: str
    entry_id: str | None = Field(default=None, foreign_key="entry.id", ondelete="SET NULL")
    created_at: datetime = Field(default_factory=_now, index=True)
