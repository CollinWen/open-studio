"""
Run table: one task given to one agent (study a source, gather references,
start a project), what it may do, and how it ended.

The run's token is never stored; it is signed (auth/run_tokens.py) and
carries the same scopes as `tools` and `board` here. This row is the record:
who started it, the brief, and the summary the agent leaves when it finishes.
Entries and agent log lines made during a run carry its id (run_id).
"""

import uuid
from datetime import datetime, timezone

from sqlmodel import JSON, Column, Field, SQLModel


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


class Run(SQLModel, table=True):
    id: str = Field(default_factory=_new_id, primary_key=True)
    agent: str = Field(index=True)

    # One of task_kinds.TASK_KINDS: study, references, prototype.
    kind: str
    # The one board it may add to and log on.
    board: str
    # The owner's note: what to do, in their words (may hold a link).
    brief: str = ""
    # Where to start, e.g. the entry holding the link to study.
    entry_id: str | None = Field(default=None, foreign_key="entry.id", ondelete="SET NULL")
    # Outside tools it may use (task_kinds.OUTSIDE_TOOLS).
    tools: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    # "owner" or "agent:<name>": who started it.
    started_by: str
    created_at: datetime = Field(default_factory=_now, index=True)
    expires_at: datetime
    # Set when the agent (or the owner) finishes it; its token stops working then.
    finished_at: datetime | None = None
    # What the agent says it did, left when it finishes.
    summary: str = ""
