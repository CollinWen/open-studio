"""
Agent log API shapes: what an agent writes, and what anyone reads back.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

LineType = Literal["plan", "thought", "finding", "question", "status"]
TEXT_MAX_LENGTH = 2000


class LogLineCreate(BaseModel):
    board: str | None = None
    type: LineType
    text: str = Field(min_length=1, max_length=TEXT_MAX_LENGTH)
    entry_id: str | None = None


class LogLineOut(BaseModel):
    id: str
    agent: str
    board: str | None
    type: str
    text: str
    entry_id: str | None
    # The entry's title when the reader may see it, so the line can link to it by name.
    entry_title: str | None
    created_at: datetime
