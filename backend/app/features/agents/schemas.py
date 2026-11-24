"""
Agent API shapes: what the owner sends to add or change an agent, and what
anyone gets back. Agents have no token of their own; their tokens are runs
(runs/schemas.py).
"""

from datetime import datetime

from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.features.runs.schemas import OutsideToolName

# Lowercase letters, digits and dashes, like a board's slug.
NAME_PATTERN = r"^[a-z0-9][a-z0-9-]{0,39}$"
# A skill's name: its folder in the agent resources, e.g. "gathering-sources".
SkillName = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9-]{0,59}$")]


class AgentCreate(BaseModel):
    name: str = Field(pattern=NAME_PATTERN)
    description: str = ""
    # Boards it may add to from the start; changed later on each board.
    boards: list[str] = []
    # Outside tools its runs may be given.
    tools: list[OutsideToolName] = []
    # Skills it works with, by name.
    skills: list[SkillName] = []


class AgentUpdate(BaseModel):
    """Every field is optional: only the fields sent are changed."""

    description: str | None = None
    # The boards it's signed on to, all at once (each board keeps its own list).
    boards: list[str] | None = None
    active: bool | None = None
    tools: list[OutsideToolName] | None = None
    skills: list[SkillName] | None = None


class AgentOut(BaseModel):
    name: str
    description: str
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

