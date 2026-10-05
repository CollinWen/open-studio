"""
Tag API shapes.
"""

from typing import Literal

from pydantic import BaseModel

# -1 hidden, 0 normal, 1 key. See models.py.
Importance = Literal[-1, 0, 1]


class TagInfo(BaseModel):
    name: str
    count: int  # how many visible entries have this tag
    description: str
    importance: Importance


class TagNotes(BaseModel):
    """What the owner can set on a tag."""

    description: str = ""
    importance: Importance = 0
