"""
Tag table: the owner's notes about a tag. Not every tag needs a row; tags
live on entries, and a row here only adds a description and an importance.
"""

from sqlmodel import Field, SQLModel

# Importance levels. Key tags are listed first and in black; hidden ones are
# left out of the tag line on the home page (they still show on entries).
HIDDEN = -1
NORMAL = 0
KEY = 1


class Tag(SQLModel, table=True):
    name: str = Field(primary_key=True)
    # Shown in place of the intro line when this tag is selected on the home page.
    description: str = ""
    importance: int = NORMAL
