"""
Run table: one session of one agent, which is one token: what it was asked
to do (an open session, or a task: study a source, gather references, start
a project), what it may do, and how it ended. Every token an agent works
with is a run; only the owner issues them.

The run's token is never stored; it is signed (auth/run_tokens.py) and
carries the same scopes as `boards` and `addons` here. This row is the record:
who started it, the brief, where to watch the agent work (its harness's own
session link, set by the agent; owner-only), and the summary it leaves when
it finishes.
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

    # One of task_kinds.TASK_KINDS: open (no set task), study, references, prototype.
    kind: str
    # The boards it may add to and log on: slugs, or ["*"] for every board its agent is
    # signed on to. Either way, each call is also checked against the agent's boards then.
    boards: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    # The owner's note: what to do, in their words (may hold a link).
    brief: str = ""
    # Where to start, e.g. the entry holding the link to study.
    entry_id: str | None = Field(default=None, foreign_key="entry.id", ondelete="SET NULL")
    # The add-ons it may use (features/addons/), by name: its agent's, or fewer.
    addons: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    # "owner" or "agent:<name>": who started it.
    started_by: str
    created_at: datetime = Field(default_factory=_now, index=True)
    expires_at: datetime
    # Set when the agent (or the owner) finishes it; its token stops working then.
    finished_at: datetime | None = None
    # A link to the harness's own record of this run (e.g. a claude.ai/code session),
    # so the owner can watch how the agent works. Set by the agent; may stay empty.
    session_url: str = ""
    # What the agent says it did, left when it finishes.
    summary: str = ""
