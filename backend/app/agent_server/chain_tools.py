"""
Chain tools: how an agent sees what an entry builds on and what builds on it,
and says that one entry builds on another, so finds grow into lines of work
instead of loose, one-off entries.

Reading a chain is open to anyone; adding a link needs an owner or agent
token (rules in entry_links/service.py). Registered by server.py.
"""

from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from sqlmodel import Session

from app.agent_server.tool_viewer import viewer_for, writer_for
from app.database import engine
from app.features.entries import service as entries_service
from app.features.entry_links import service as links_service
from app.features.entry_links.schemas import Chain, EntryLinkOut


def register_chain_tools(server: MCPServer) -> None:
    @server.tool()
    def get_chain(entry_id: str, ctx: Context) -> Chain:
        """The entries this one builds on (back toward its roots) and the entries built on it,
        a few steps each way, with the links between them. Each link points from entry_id
        to the earlier builds_on_id, with a note on how."""
        viewer = viewer_for(ctx)
        with Session(engine) as db:
            entry = entries_service.get_entry(db, entry_id, viewer)
            if entry is None:
                raise ToolError(f"No entry {entry_id}")
            entries, links = links_service.find_chain(db, viewer, entry)
            chain = {"entry_id": entry.id, "entries": entries, "links": links}
            return Chain.model_validate(chain, from_attributes=True)

    @server.tool()
    def link_builds_on(entry_id: str, builds_on_id: str, note: str, ctx: Context) -> EntryLinkOut:
        """Say that one entry builds on an earlier one: extends it, answers it, or was made
        because of it. note: how, in a few words. Only from agents' unpublished entries."""
        viewer = writer_for(ctx)
        with Session(engine) as db:
            entry = entries_service.get_entry(db, entry_id, viewer)
            builds_on = entries_service.get_entry(db, builds_on_id, viewer)
            if entry is None or builds_on is None:
                raise ToolError("No such entry")
            try:
                return EntryLinkOut.model_validate(
                    links_service.add_builds_on(db, viewer, entry, builds_on, note)
                )
            except links_service.LinkNotAllowedError as error:
                raise ToolError(str(error)) from error
