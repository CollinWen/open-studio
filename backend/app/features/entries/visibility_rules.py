"""
Visibility rules: which entries each kind of viewer (visitor, agent, owner)
may list, open and edit.

  owner    - lists, opens and edits everything
  visitor  - lists public entries; opens public and unlisted ones by link
  agent    - like a visitor, and also lists other agents' unlisted entries,
             so agents can build on each other's work. It may edit agents'
             entries until the owner publishes them; after that they are the owner's.

Entries an agent adds always start unlisted: on the site only by direct link,
never in the grid, until the owner makes them public.
Used by entries/service.py.
"""

from sqlalchemy import ColumnElement, and_, or_, true

from app.auth.viewer import OWNER, Viewer
from app.features.entries.models import Entry

AGENT_ENTRY_VISIBILITY = "unlisted"


def listing_condition(viewer: Viewer) -> ColumnElement[bool]:
    """The database condition for entries this viewer sees when browsing or searching."""
    if viewer.is_owner:
        return true()
    if viewer.is_agent:
        return or_(
            Entry.visibility == "public",
            and_(Entry.visibility == "unlisted", Entry.added_by != OWNER),
        )
    return Entry.visibility == "public"


def can_list(viewer: Viewer, entry: Entry) -> bool:
    """The same rule as listing_condition, for one entry already loaded (e.g. one step of a chain)."""
    if viewer.is_owner or entry.visibility == "public":
        return True
    return viewer.is_agent and entry.visibility == "unlisted" and entry.added_by != OWNER


def can_open(viewer: Viewer, entry: Entry) -> bool:
    """Whether this viewer may open the entry by its id."""
    return viewer.is_owner or entry.visibility != "private"


def can_edit(viewer: Viewer, entry: Entry) -> bool:
    if viewer.is_owner:
        return True
    return viewer.is_agent and entry.added_by != OWNER and entry.visibility == AGENT_ENTRY_VISIBILITY
