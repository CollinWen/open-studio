"""
Agent API shapes: what the owner sends to add or change an agent, and what
anyone gets back. A token only ever goes over the wire once, in AgentWithToken.
"""

from datetime import datetime

from pydantic import BaseModel, Field

# Lowercase letters, digits and dashes, like a board's slug.
NAME_PATTERN = r"^[a-z0-9][a-z0-9-]{0,39}$"


class AgentCreate(BaseModel):
    name: str = Field(pattern=NAME_PATTERN)
    description: str = ""
    # Boards it may add to from the start; changed later on each board.
    boards: list[str] = []


class AgentUpdate(BaseModel):
    """Every field is optional: only the fields sent are changed."""

    description: str | None = None
    active: bool | None = None


class AgentOut(BaseModel):
    name: str
    description: str
    active: bool
    status: str
    last_seen_at: datetime | None
    created_at: datetime
    # Boards it's signed on to (from each board's agents list).
    boards: list[str]


class AgentWithToken(BaseModel):
    """Returned when an agent is added or given a new token: the only time the token is shown."""

    agent: AgentOut
    token: str
