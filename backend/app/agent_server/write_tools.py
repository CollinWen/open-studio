"""
Write tools: how an agent adds to the studio through the MCP server.

Needs an owner or agent token. An agent's entries are saved unlisted and
signed with its name, a link already in the studio isn't added again, and
agents may only edit agents' entries the owner hasn't published yet; all of
that is decided in entries/service.py and entries/visibility_rules.py.
Registered by server.py.
"""

from datetime import date

from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from sqlmodel import Session

from app.agent_server.tool_viewer import writer_for
from app.database import engine
from app.features.entries import service as entries_service
from app.features.entries.schemas import EntryCreate, EntryOut, EntryUpdate, MediaItem
from app.features.entries.visibility_rules import can_edit


def register_write_tools(server: MCPServer) -> None:
    @server.tool()
    def add_entry(
        title: str,
        description: str,
        ctx: Context,
        source_url: str = "",
        source_name: str = "",
        kind: str = "link",
        tags: list[str] | None = None,
        occurred_at: date | None = None,
        media: list[MediaItem] | None = None,
    ) -> EntryOut:
        """Add one thing to the studio.

        description: why it's here, in a few plain sentences: what it is and why it
        matters to the studio's interests. This is the most important field.
        kind: link, note, book, paper, video, project, ...   source_name: who made it.
        tags: short lowercase labels; leave empty to have them suggested.
        occurred_at: when it was made or published.  media: pictures or videos to show.
        Fails if the link is already in the studio; the error names the existing entry."""
        viewer = writer_for(ctx)
        data = EntryCreate(
            title=title,
            description=description,
            kind=kind,
            source_name=source_name,
            source_url=source_url,
            tags=tags or [],
            occurred_at=occurred_at,
            media=media or [],
        )
        with Session(engine) as db:
            try:
                return EntryOut.model_validate(entries_service.create_entry(db, data, viewer))
            except entries_service.DuplicateLinkError as error:
                where = f": entry {error.existing.id}" if error.existing else ""
                raise ToolError(f"Already in the studio{where}") from error

    @server.tool()
    def update_entry(
        entry_id: str,
        ctx: Context,
        title: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        media: list[MediaItem] | None = None,
    ) -> EntryOut:
        """Improve an entry an agent added: a better description, tags or pictures.
        Only the fields given are changed. Entries the owner added or published can't be edited."""
        viewer = writer_for(ctx)
        given = {"title": title, "description": description, "tags": tags, "media": media}
        changes = EntryUpdate.model_validate({field: value for field, value in given.items() if value is not None})
        with Session(engine) as db:
            entry = entries_service.get_entry(db, entry_id, viewer)
            if entry is None:
                raise ToolError(f"No entry {entry_id}")
            if not can_edit(viewer, entry):
                raise ToolError("Agents can only edit agents' entries the owner hasn't published")
            return EntryOut.model_validate(entries_service.update_entry(db, entry, changes, viewer))
