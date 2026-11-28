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

# In a run's boards: every board its agent is signed on to, now or later.
ALL_BOARDS = "*"
# The harnesses a sandbox can be set up for (runs/sandbox_setup.py).
HarnessName = Literal["pi", "claude_code"]
SESSION_URL_MAX_LENGTH = 500


class RunCreate(BaseModel):
    agent: str
    # The boards it may add to and log on: slugs, or ["*"] for all its agent's boards.
    boards: list[str] = Field(min_length=1)
    # Leave out for all its agent's add-ons; a narrower list gives fewer.
    addons: list[str] | None = None
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
    # Slugs, or ["*"]: every board its agent is signed on to.
    boards: list[str]
    # The add-ons it may use, by name.
    addons: list[str]
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

    # One line to paste into a shell where that harness is installed: it sets up a sandbox
    # folder for the run (prompt, AGENTS.md, skills, studio connection) and starts the agent.
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
    # Who the agent is (its manifest), how to reach the studio, the run's limits.
    prompt: str
    # The shell script that sets up a sandbox for the run whose token fetches it;
    # add ?harness=claude_code for Claude Code (Pi otherwise).
    sandbox_url: str
    # By harness name ("pi", "claude_code"): one line that sets up a sandbox and starts the agent.
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
    # What the setup sets for the harness besides the token: where the studio is, and the run.
    exports: dict[str, str]
    # The shell command that starts the harness inside the folder.
    command: str
    # The harness's names for the tools the run may use.
    allowed_tools: list[str]
