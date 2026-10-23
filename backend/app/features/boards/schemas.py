"""
Board API shapes: what the owner sends to make or change a board, and what
anyone gets back.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

# Lowercase letters, digits and dashes, so a slug always works in a link.
SLUG_PATTERN = r"^[a-z0-9][a-z0-9-]{0,39}$"


class BoardCreate(BaseModel):
    slug: str = Field(pattern=SLUG_PATTERN)
    name: str
    description: str = ""
    agents: list[str] = []


class BoardUpdate(BaseModel):
    """Every field is optional: only the fields sent are changed."""

    name: str | None = None
    description: str | None = None
    agents: list[str] | None = None


class BoardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    name: str
    description: str
    agents: list[str]
    created_at: datetime
