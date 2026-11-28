"""
Add-on tools: how an agent on a run uses its add-ons that run through the
studio (email, search and the like, on Composio). list_addon_tools shows
what its run may call and what each takes; call_addon_tool runs one as the
account the owner connected. The agent never holds a key. Its AGENTS.md
says which add-ons it has and how the owner wants them used.

Two relay tools rather than one MCP tool per Composio tool, so what an
agent sees is decided per run, on every call. The checks are in
addons/relay.py. Registered by server.py.
"""

from typing import Any

from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from sqlmodel import Session

from app.agent_server.tool_viewer import viewer_for
from app.database import engine
from app.features.addons import relay
from app.features.addons.schemas import AddonCallResult, AddonTool


def register_addon_tools(server: MCPServer) -> None:
    @server.tool()
    def list_addon_tools(ctx: Context, query: str = "") -> list[AddonTool]:
        """The tools of your add-ons that run through the studio (email, search and the like; your
        AGENTS.md says which add-ons you have and how the owner wants them used), each with what it
        does and what it takes, as a JSON schema. `query` keeps those matching every word. Empty if
        your run has none."""
        viewer = viewer_for(ctx)
        with Session(engine) as db:
            try:
                return relay.list_run_tools(db, viewer, query)
            except (relay.AddonRefusedError, relay.AddonUnavailableError) as error:
                raise ToolError(str(error))

    @server.tool()
    def call_addon_tool(tool: str, ctx: Context, arguments: dict[str, Any] | None = None) -> AddonCallResult:
        """Run one of your add-on tools (from list_addon_tools) with its arguments. It runs as the
        account the owner connected, so you need no keys, and Composio refuses anything the owner's
        policy blocks. Each call counts against your hourly limit; a tool that ran but failed says
        why in `error`."""
        viewer = viewer_for(ctx)
        with Session(engine) as db:
            try:
                return relay.call_run_tool(db, viewer, tool, arguments or {})
            except (relay.AddonRefusedError, relay.AddonUnavailableError) as error:
                raise ToolError(str(error))
