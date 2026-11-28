"""
Add-on tables: every capability the studio can give its agents, defined
once, and the Composio session each run uses for its Composio add-ons.

An add-on has a name agents are given it by, where it comes from (the
sandbox's own web, code or git; or a Composio toolkit, which the studio
runs for the agent), the account it acts as, and its guide: what it is,
what it's for and how it works, which goes into each run's AGENTS.md.
Which agents use an add-on is kept on the agent (agents/models.py,
Agent.addons), with any instructions meant for that agent alone.
"""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Addon(SQLModel, table=True):
    # Short, lowercase, how agents are given it ("email", "web-search").
    name: str = Field(primary_key=True)
    # "sandbox": one of the sandbox's own tools, which its harness allows or not
    #   (service: web, code or github);
    # "composio": a Composio toolkit the studio runs for the agent (service: its slug, e.g. gmail).
    kind: str
    service: str
    # For a Composio add-on: the connected account it acts as ("ca_..."); empty until connected.
    account: str = ""
    # What it is, what it's for and how it works, in markdown, for the agent to read.
    guide: str = ""
    created_at: datetime = Field(default_factory=_now)


class ComposioSession(SQLModel, table=True):
    """The Composio session a run's Composio add-ons go through, made on first use."""

    run_id: str = Field(primary_key=True)
    session_id: str
    created_at: datetime = Field(default_factory=_now)
