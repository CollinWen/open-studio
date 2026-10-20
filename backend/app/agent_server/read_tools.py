"""
Read tools: what an agent can look at through the MCP server. The studio's
interests (key tags and their descriptions), search by meaning, recent
changes, one entry, and the entries related to it.

Anyone may call these; an agent token also shows other agents' unlisted
entries (see entries/visibility_rules.py). Registered by server.py.
"""

from datetime import datetime, timezone

from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel
from sqlmodel import Session

from app.agent_server.tool_viewer import viewer_for
from app.database import engine
from app.features.entries import service as entries_service
from app.features.entries.schemas import EntryOut
from app.features.related.service import find_related_entries
from app.features.search.service import search_entries
from app.features.tags import service as tags_service
from app.features.tags.models import NORMAL
from app.features.tags.schemas import TagInfo

MOST_USED_TAG_COUNT = 30
MAX_LISTED_ENTRIES = 100


class StudioInterests(BaseModel):
    key_tags: list[TagInfo]
    most_used_tags: list[TagInfo]


def register_read_tools(server: MCPServer) -> None:
    @server.tool()
    def get_studio_interests(ctx: Context) -> StudioInterests:
        """What this studio cares about: the owner's key tags (with a description of each,
        when written) and the most used tags. Start here to choose what to look for."""
        with Session(engine) as db:
            tags = tags_service.list_tags(db, viewer_for(ctx))
        return StudioInterests(
            key_tags=[tag for tag in tags if tag.importance > NORMAL],
            most_used_tags=sorted(tags, key=lambda tag: -tag.count)[:MOST_USED_TAG_COUNT],
        )

    @server.tool()
    def search_studio(query: str, ctx: Context) -> list[EntryOut]:
        """Entries matching a query by meaning as well as words, best first.
        Search before adding something, so the studio doesn't get it twice."""
        with Session(engine) as db:
            return [EntryOut.model_validate(entry) for entry in search_entries(db, query, viewer_for(ctx))]

    @server.tool()
    def list_entries(ctx: Context, tag: str = "", updated_since: str = "", limit: int = 50) -> list[EntryOut]:
        """Entries newest first. tag: only entries with this tag. updated_since: an ISO date
        or time; only entries added or edited after it (to catch up on what others added)."""
        since = _parse_time(updated_since) if updated_since else None
        with Session(engine) as db:
            entries = entries_service.list_entries(db, viewer_for(ctx), updated_since=since)
        if tag:
            entries = [entry for entry in entries if tag in entry.tags]
        return [EntryOut.model_validate(entry) for entry in entries[: min(limit, MAX_LISTED_ENTRIES)]]

    @server.tool()
    def get_entry(entry_id: str, ctx: Context) -> EntryOut:
        """One entry by id."""
        with Session(engine) as db:
            return EntryOut.model_validate(_entry_or_error(db, entry_id, ctx))

    @server.tool()
    def find_related(entry_id: str, ctx: Context, limit: int = 6) -> list[EntryOut]:
        """The entries closest in meaning to this one: a way to wander and find gaps."""
        with Session(engine) as db:
            viewer = viewer_for(ctx)
            entry = _entry_or_error(db, entry_id, ctx)
            return [EntryOut.model_validate(other) for other in find_related_entries(db, entry, viewer, limit)]


def _entry_or_error(db: Session, entry_id: str, ctx: Context):
    entry = entries_service.get_entry(db, entry_id, viewer_for(ctx))
    if entry is None:
        raise ToolError(f"No entry {entry_id}")
    return entry


def _parse_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ToolError(f"updated_since should be an ISO date or time, got {value!r}") from error
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
