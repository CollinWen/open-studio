"""
Run API shapes: what the owner sends to issue a token (start a run), what
anyone allowed gets back about one, the link to the harness's session an
agent leaves on its run, the kit (everything any harness needs to set an
agent to work, plus one line per harness that sets up a sandbox for it),
and that sandbox setup itself: the files a fresh sandbox writes and the
command that starts its harness.
A run token only goes over the wire once, in the kit.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

RunKindName = Literal["open", "study", "references", "prototype"]
# In a run's boards: every board its agent is signed on to, now or later.
ALL_BOARDS = "*"
OutsideToolName = Literal["web", "code", "github"]
# The harnesses a sandbox can be set up for (runs/sandbox_setup.py).
HarnessName = Literal["pi", "claude_code"]
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

    # Lines to paste into a shell where that harness is installed: they set up a sandbox
    # folder for the run (skills, studio connection, prompt) and run the whole task.
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
    # The shell script that sets up a sandbox for this run, fetched with the token;
    # add ?harness=claude_code for Claude Code (Pi otherwise).
    sandbox_url: str
    # By harness name ("pi", "claude_code"): lines that set up a sandbox and run the task.
    setups: dict[str, HarnessSetup]


class SandboxFile(BaseModel):
    # Where it goes, inside the run's folder.
    path: str
    # Its bytes, base64 encoded (a skill may hold pictures).
    content_base64: str


class SandboxSetup(BaseModel):
    """Everything a fresh sandbox needs to start one run in one harness. Holds no secret:
    the token is read from OPEN_STUDIO_TOKEN only when the harness starts."""

    run_id: str
    harness: HarnessName
    # The folder it all goes in, made where the setup runs.
    folder: str
    files: list[SandboxFile]
    # The skills written into it, by name.
    skills: list[str]
    # What the sandbox must already have: the harness's program and these environment variables.
    program: str
    env: list[str]
    # The shell command that starts the harness inside the folder.
    command: str
    # The harness's names for the tools the run may use.
    allowed_tools: list[str]
