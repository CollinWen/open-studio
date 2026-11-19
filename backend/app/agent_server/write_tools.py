"""
Write tools: how an agent adds entries to the studio through the MCP server.

Needs an owner or agent token. An agent adds only to boards it's signed on
to; its entries are saved unlisted and signed with its name, a link already
in the studio isn't added again, and agents may only edit agents' entries the
owner hasn't published yet. All of that is decided in entries/service.py and
entries/visibility_rules.py. A write-up (an entry's illustrated text, in
HTML) is attached with attach_writeup, which makes it safe and stores it
(media/service.py). Linking entries later is in chain_tools.py.
Registered by server.py.
"""

from datetime import date

from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel
from sqlmodel import Session

from app.agent_server.tool_viewer import writer_for
from app.database import engine
from app.features.entries import service as entries_service
from app.features.entries.schemas import EntryCreate, EntryOut, EntryUpdate, MediaItem
from app.features.entries.visibility_rules import can_edit
from app.features.entry_links import service as links_service
from app.features.entry_links.schemas import BuildsOnCreate
from app.features.media import service as media_service

BOARD_ERRORS = (entries_service.UnknownBoardError, entries_service.BoardNotAllowedError)


class WriteupAttached(BaseModel):
    entry: EntryOut
    # What the studio removed from the HTML (styles, scripts, outside pictures...).
    removed: list[str]


def register_write_tools(server: MCPServer) -> None:
    @server.tool()
    def add_entry(
        board: str,
        title: str,
        description: str,
        ctx: Context,
        source_url: str = "",
        source_name: str = "",
        kind: str = "link",
        tags: list[str] | None = None,
        occurred_at: date | None = None,
        media: list[MediaItem] | None = None,
        builds_on: list[BuildsOnCreate] | None = None,
    ) -> EntryOut:
        """Add one thing to a board you're signed on to (see list_boards).

        description: why it's here, in a few plain sentences: what it is and why it fits
        the board's brief. This is the most important field.
        kind: link, note, book, paper, video, project, ...   source_name: who made it.
        tags: short lowercase labels; leave empty to have them suggested.
        occurred_at: when it was made or published.  media: pictures or videos to show
        (for a write-up, add the entry first, then use attach_writeup).
        builds_on: earlier entries this one extends or answers, each {builds_on_id, note}.
        Prefer adding to a chain over adding a loose entry.
        Fails if the link is already in the studio; the error names the existing entry."""
        viewer = writer_for(ctx)
        data = EntryCreate(
            board=board,
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
            # Look up what it builds on first, so a bad id doesn't leave a half-made entry.
            earlier = [
                (_entry_or_error(db, link.builds_on_id, viewer), link.note) for link in builds_on or []
            ]
            try:
                entry = entries_service.create_entry(db, data, viewer)
            except entries_service.DuplicateLinkError as error:
                where = f": entry {error.existing.id}" if error.existing else ""
                raise ToolError(f"Already in the studio{where}") from error
            except BOARD_ERRORS as error:
                raise ToolError(str(error)) from error
            for earlier_entry, note in earlier:
                links_service.add_builds_on(db, viewer, entry, earlier_entry, note)
            return EntryOut.model_validate(entry)

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
        changes = EntryUpdate.model_validate(
            {field: value for field, value in given.items() if value is not None}
        )
        with Session(engine) as db:
            entry = _entry_or_error(db, entry_id, viewer)
            if not can_edit(viewer, entry):
                raise ToolError("Agents can only edit agents' entries the owner hasn't published")
            return EntryOut.model_validate(entries_service.update_entry(db, entry, changes, viewer))

    @server.tool()
    def attach_writeup(entry_id: str, html: str, ctx: Context, caption: str = "") -> WriteupAttached:
        """Add a write-up to an entry an agent added: an illustrated page of HTML, for
        when a description isn't enough (a study's findings, what a commit changed, a diagram).
        You decide what's on the page and how it's arranged; the studio decides how it looks.
        Kept: any structure (headings, lists, tables, figures, code, details); layout CSS in
        style="" or <style> (display, grid/flex, gap, widths, alignment, order; var(--line)
        and var(--gutter) keep you on the studio's grid); inline <svg> drawings with arrowheads
        (marker), hatching (pattern) and reused shapes (defs, use), filled with currentColor
        or none, lighter with class "soft" or "faint"; pictures as data: URLs; links out;
        links to other entries as href="/entry/<id>" (link what the page mentions to the
        studio's entries on it: see the linking-entries skill).
        Removed: fonts, sizes, colors, backgrounds, borders, margins and padding (the studio
        sets them), and everything that runs or loads (scripts, forms, iframes, outside files).
        Nothing can be interactive. The answer lists what was removed; see the studio-writeup
        skill for the full rules."""
        viewer = writer_for(ctx)
        with Session(engine) as db:
            entry = _entry_or_error(db, entry_id, viewer)
            if not can_edit(viewer, entry):
                raise ToolError("Agents can only edit agents' entries the owner hasn't published")
            try:
                stored = media_service.store_writeup(html)
            except ValueError as error:
                raise ToolError(str(error)) from error
            writeup = MediaItem(type="html", url=stored.url, caption=caption)
            changes = EntryUpdate(media=[*map(MediaItem.model_validate, entry.media), writeup])
            updated = entries_service.update_entry(db, entry, changes, viewer)
            return WriteupAttached(entry=EntryOut.model_validate(updated), removed=stored.removed)


def _entry_or_error(db: Session, entry_id: str, viewer):
    entry = entries_service.get_entry(db, entry_id, viewer)
    if entry is None:
        raise ToolError(f"No entry {entry_id}")
    return entry
