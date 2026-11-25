"""
Toolkit tools: how an agent on a run uses the tools of outside services
(GitHub, Exa, ...) through the studio. list_toolkit_tools shows what its run
may call, with each tool's input and pinned arguments; call_toolkit_tool
runs one as the account the owner chose. The agent never holds a key.

Two relay tools rather than one MCP tool per Composio tool, so what an agent
sees is decided per run, on every call. The checks are in
toolkits/service.py. Registered by server.py.
"""

from typing import Any

from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from sqlmodel import Session

from app.agent_server.tool_viewer import viewer_for
from app.database import engine
from app.features.toolkits import service as toolkits_service
from app.features.toolkits.schemas import ToolkitCallResult, ToolkitTool


def register_toolkit_tools(server: MCPServer) -> None:
    @server.tool()
    def list_toolkit_tools(ctx: Context) -> list[ToolkitTool]:
        """The tools of outside services (GitHub, Exa, ...) your run may call through the studio,
        each with what it does, what it takes (a JSON schema) and its pinned arguments: those may
        only take the values listed ("x*": anything starting with x). Empty if your run has none."""
        viewer = viewer_for(ctx)
        with Session(engine) as db:
            try:
                return toolkits_service.list_run_tools(db, viewer)
            except toolkits_service.ToolkitRefusedError as error:
                raise ToolError(str(error))

    @server.tool()
    def call_toolkit_tool(tool: str, arguments: dict[str, Any], ctx: Context) -> ToolkitCallResult:
        """Run one of your toolkit tools (from list_toolkit_tools) with its arguments. It runs as the
        account the owner chose, so you need no keys. Keep pinned arguments to their values. Each
        call counts against your hourly limit; a tool that ran but failed says why in `error`."""
        viewer = viewer_for(ctx)
        with Session(engine) as db:
            try:
                return toolkits_service.call_run_tool(db, viewer, tool, arguments)
            except (toolkits_service.ToolkitRefusedError, toolkits_service.ToolkitUnavailableError) as error:
                raise ToolError(str(error))
