"""
Run API shapes: what's sent to start a run, what anyone allowed gets back
about one, and the kit: everything a harness needs to set an agent to work.
A run token only goes over the wire once, in the kit.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

RunKindName = Literal["study", "references", "prototype"]
OutsideToolName = Literal["web", "code", "github"]


class RunCreate(BaseModel):
    agent: str
    kind: RunKindName
    board: str
    brief: str = ""
    entry_id: str | None = None
    # Leave out for the kind's usual tools; a narrower list gives fewer.
    tools: list[OutsideToolName] | None = None
    # How long its token works; the default and the most allowed are in config.py.
    hours: int | None = Field(default=None, ge=1)


class RunFinish(BaseModel):
    summary: str = ""


class RunOut(BaseModel):
    id: str
    agent: str
    kind: str
    board: str
    brief: str
    entry_id: str | None
    tools: list[str]
    started_by: str
    created_at: datetime
    expires_at: datetime
    finished_at: datetime | None
    summary: str
    state: Literal["running", "finished", "expired"]
    # What it may do, as written in its token.
    scopes: list[str]
    # Entries it added.
    added: list[str]


class RunKit(BaseModel):
    """Returned once, when a run starts: hand it to Claude Code, a box, or any MCP client."""

    run: RunOut
    token: str
    mcp_url: str
    # The run's instructions: the task kind, the owner's brief, its limits.
    prompt: str
    # Claude Code tools to allow (MCP tools, plus the outside tools it was given).
    allowed_tools: list[str]
    # A ready command that runs the whole thing in Claude Code, start to finish.
    claude_command: str
