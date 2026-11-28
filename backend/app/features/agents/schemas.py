"""
Agent API shapes: what the owner sends to add or change an agent, and what
anyone gets back. Agents have no token of their own; their tokens are runs
(runs/schemas.py).
"""

from datetime import datetime
from typing import Literal, get_args

from pydantic import BaseModel, Field

from app.features.runs.schemas import OutsideToolName

# Lowercase letters, digits and dashes, like a board's slug.
NAME_PATTERN = r"^[a-z0-9][a-z0-9-]{0,39}$"
# The skills the owner can pick for an agent: one folder each in skills/ (a test
# keeps them in step). open-studio and studio-collaborator aren't here: every
# agent loads those (runs/run_kit.py). Mirrored in frontend/src/types/agent.ts.
SkillName = Literal[
    "gathering-sources", "studying-sources", "brainstorming", "building", "studio-writeup", "linking-entries"
]
AGENT_SKILLS: tuple[str, ...] = get_args(SkillName)
MANIFEST_MAX_LENGTH = 8000


class AgentCreate(BaseModel):
    name: str = Field(pattern=NAME_PATTERN)
    description: str = ""
    # Its standing job, written into every run's prompt (agents/models.py).
    manifest: str = Field(default="", max_length=MANIFEST_MAX_LENGTH)
    # Boards it may add to from the start; changed later on each board.
    boards: list[str] = []
    # Outside tools its runs may be given.
    tools: list[OutsideToolName] = []
    # Skills it works with, by name.
    skills: list[SkillName] = []


class AgentUpdate(BaseModel):
    """Every field is optional: only the fields sent are changed."""

    description: str | None = None
    manifest: str | None = Field(default=None, max_length=MANIFEST_MAX_LENGTH)
    # The boards it's signed on to, all at once (each board keeps its own list).
    boards: list[str] | None = None
    active: bool | None = None
    tools: list[OutsideToolName] | None = None
    skills: list[SkillName] | None = None


class AgentOut(BaseModel):
    name: str
    description: str
    manifest: str
    active: bool
    status: str
    # Outside tools its runs may be given.
    tools: list[str]
    # Skills it works with, by name.
    skills: list[str]
    last_seen_at: datetime | None
    created_at: datetime
    # Boards it's signed on to (from each board's agents list).
    boards: list[str]

