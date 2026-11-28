"""
Agent API shapes: what the owner sends to add or change an agent, and what
anyone gets back. Agents have no token of their own; their tokens are runs
(runs/schemas.py).
"""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.features.addons.schemas import AddonName

# Lowercase letters, digits and dashes, like a board's slug.
NAME_PATTERN = r"^[a-z0-9][a-z0-9-]{0,39}$"
# A skill's name: its folder in the agent resources, e.g. "gathering-sources"; it must be
# in the skill catalog (features/skills/) when saved.
SkillName = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9-]{0,59}$")]
# The owner's instructions for one add-on, in markdown.
Instructions = Annotated[str, StringConstraints(max_length=10_000)]
MANIFEST_MAX_LENGTH = 8000


class AgentCreate(BaseModel):
    name: str = Field(pattern=NAME_PATTERN)
    description: str = ""
    # Its standing job, written into every run's prompt (agents/models.py).
    manifest: str = Field(default="", max_length=MANIFEST_MAX_LENGTH)
    # Boards it may add to from the start; changed later on each board.
    boards: list[str] = []
    # Skills it works with, by name.
    skills: list[SkillName] = []
    # The add-ons it uses, by name, and the owner's instructions for any of them.
    addons: list[AddonName] = []
    addon_instructions: dict[AddonName, Instructions] = {}


class AgentUpdate(BaseModel):
    """Every field is optional: only the fields sent are changed."""

    description: str | None = None
    manifest: str | None = Field(default=None, max_length=MANIFEST_MAX_LENGTH)
    # The boards it's signed on to, all at once (each board keeps its own list).
    boards: list[str] | None = None
    active: bool | None = None
    skills: list[SkillName] | None = None
    # All its add-ons at once; instructions for add-ons it no longer has are dropped.
    addons: list[AddonName] | None = None
    addon_instructions: dict[AddonName, Instructions] | None = None


class AgentOut(BaseModel):
    name: str
    description: str
    manifest: str
    active: bool
    status: str
    # Skills it works with, by name.
    skills: list[str]
    # The add-ons it uses, by name.
    addons: list[str]
    # The owner's instructions for its add-ons. Only the owner sees them; everyone else gets {}.
    addon_instructions: dict[str, str]
    last_seen_at: datetime | None
    created_at: datetime
    # Boards it's signed on to (from each board's agents list).
    boards: list[str]

