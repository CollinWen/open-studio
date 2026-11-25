"""
Run API shapes: what the owner sends to issue a token (start a run), what
anyone allowed gets back about one, the link to the harness's session an
agent leaves on its run, and the kit: everything any harness needs to set an
agent to work, plus optional ready-made setups for particular harnesses.
A run token only goes over the wire once, in the kit.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

RunKindName = Literal["open", "study", "references", "prototype"]
# In a run's boards: every board its agent is signed on to, now or later.
ALL_BOARDS = "*"
OutsideToolName = Literal["web", "code", "github"]
SESSION_URL_MAX_LENGTH = 500


class RunCreate(BaseModel):
    agent: str
    # "open" (no set task) unless it's one of the task kinds.
    kind: RunKindName = "open"
    # The boards it may add to and log on: slugs, or ["*"] for all its agent's boards.
    boards: list[str] = Field(min_length=1)
    brief: str = ""
    entry_id: str | None = None
    # Leave out for the kind's usual tools (an open run: all its agent was granted);
    # a narrower list gives fewer.
    tools: list[OutsideToolName] | None = None
    # How long its token works; the default and the most allowed are in config.py.
    minutes: int | None = Field(default=None, ge=1)


class RunFinish(BaseModel):
    summary: str = ""


class RunSession(BaseModel):
    """Where the harness keeps its own record of the run, e.g. a claude.ai/code session."""

    url: str = Field(max_length=SESSION_URL_MAX_LENGTH)

    @field_validator("url")
    @classmethod
    def _web_address(cls, value: str) -> str:
        value = value.strip()
        if not value.startswith(("https://", "http://")):
            raise ValueError("A session link must start with https:// or http://")
        return value


class RunOut(BaseModel):
    id: str
    agent: str
    kind: str
    # Slugs, or ["*"]: every board its agent is signed on to.
    boards: list[str]
    brief: str
    entry_id: str | None
    tools: list[str]
    started_by: str
    created_at: datetime
    expires_at: datetime
    finished_at: datetime | None
    # Where to watch the agent work, in its harness; empty until the agent sets it.
    session_url: str
    summary: str
    state: Literal["running", "finished", "expired"]
    # What it may do, as written in its token.
    scopes: list[str]
    # Entries it added.
    added: list[str]


class HarnessSetup(BaseModel):
    """A ready way to run the kit in one particular harness."""

    # A command that runs the whole task, start to finish.
    command: str
    # That harness's names for the tools the run may use.
    allowed_tools: list[str]


class RunKit(BaseModel):
    """Returned once, when a run starts. Everything outside `setups` works with any
    harness: send `token` as `Authorization: Bearer <token>` to `mcp_url` (MCP) or
    `api_url` (plain HTTP), give the model `prompt`, and allow only the run's tools."""

    run: RunOut
    token: str
    mcp_url: str
    api_url: str
    # The run's instructions: the task kind, the owner's brief, its limits.
    prompt: str
    # Optional, by harness name ("claude_code"): ready-made commands. Never needed.
    setups: dict[str, HarnessSetup]
