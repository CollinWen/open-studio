"""
Agent server: the studio as an MCP server at /mcp, so any agent (a Claude
terminal, a research bot) can read the studio and add to it with tools
instead of raw HTTP calls.

  claude mcp add --transport http open-studio https://api.yourdomain.com/mcp \
      --header "Authorization: Bearer <agent token>"

It answers each request on its own (no sessions kept between calls), so it
keeps working with many agents at once and with more than one backend machine.
The tools are in board_tools.py, read_tools.py, write_tools.py and
chain_tools.py; how to use them well is in
skills/open-studio/SKILL.md. Mounted by main.py.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

from app.agent_server.board_tools import register_board_tools
from app.agent_server.chain_tools import register_chain_tools
from app.agent_server.read_tools import register_read_tools
from app.agent_server.write_tools import register_write_tools

INSTRUCTIONS = """\
Open Studio is one person's collection of their work and interests: projects,
sketches, books, links, notes. It is split into boards, each a separate space
with its own focus. Agents help a board grow by finding things that fit its
brief and connecting them into chains of work that build on each other.
Call list_boards and get_board_brief first, search_studio before adding
anything, write each description as "why it's here" in plain sentences, and
say what each find builds on. What you add stays unlisted until the owner
publishes it."""

studio_mcp = MCPServer(name="open-studio", instructions=INSTRUCTIONS)
register_board_tools(studio_mcp)
register_read_tools(studio_mcp)
register_write_tools(studio_mcp)
register_chain_tools(studio_mcp)


def mount_agent_server(app: FastAPI) -> None:
    """Serve the MCP endpoint at /mcp on the main app."""
    mcp_app = studio_mcp.streamable_http_app(
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
        # Callers prove who they are with a token, not by where they connect from.
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    )
    app.router.routes.extend(mcp_app.routes)


@asynccontextmanager
async def run_agent_server(_app: FastAPI) -> AsyncIterator[None]:
    """App lifespan: the MCP endpoint only answers while this is running."""
    async with studio_mcp.session_manager.run():
        yield
