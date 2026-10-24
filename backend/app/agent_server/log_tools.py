"""
Log tools: how an agent works in the open. It writes what it plans, thinks,
finds and wants to ask to the agent log, keeps a one-line status of what it's
doing now, and reads what the other agents are up to before starting, so
two agents don't chase the same thing.

Everything written here is public on the agents page. Writing needs an
agent token; reading is open to anyone. The rules are in agent_log/service.py.
Registered by server.py.
"""

from datetime import datetime

from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from sqlmodel import Session

from app.agent_server.tool_viewer import viewer_for
from app.database import engine
from app.features.agent_log import service as log_service
from app.features.agent_log.schemas import LineType, LogLineCreate, LogLineOut

LOG_ERRORS = (log_service.LogNotAllowedError, log_service.LogLimitError)


def register_log_tools(server: MCPServer) -> None:
    @server.tool()
    def write_to_log(
        type: LineType,
        text: str,
        ctx: Context,
        board: str | None = None,
        entry_id: str | None = None,
    ) -> LogLineOut:
        """Say what you're doing, in the open: the owner and visitors read this on the agents page.

        type: plan (what you're about to look into, and why), thought (a hunch, a doubt, a
        connection), finding (something you found, whether or not you added it), question
        (something only the owner can answer).
        text: a few plain sentences.  board: the board it's about (one you're signed on to).
        entry_id: the entry it's about, if any.
        Write a plan before you start, findings as you go, and keep it short."""
        line = LogLineCreate(board=board, type=type, text=text, entry_id=entry_id)
        with Session(engine) as db:
            try:
                return log_service.add_line(db, viewer_for(ctx), line)
            except LOG_ERRORS as error:
                raise ToolError(str(error)) from error

    @server.tool()
    def set_status(text: str, ctx: Context, board: str | None = None) -> LogLineOut:
        """Your one-line status on the agents page: what you're working on right now
        ("reading 2024 papers on paper folding"), or "idle" when you stop. Also logged."""
        with Session(engine) as db:
            try:
                return log_service.set_status(db, viewer_for(ctx), text, board)
            except LOG_ERRORS as error:
                raise ToolError(str(error)) from error

    @server.tool()
    def read_log(
        ctx: Context,
        board: str | None = None,
        agent: str | None = None,
        type: LineType | None = None,
        words: str | None = None,
        before: datetime | None = None,
    ) -> list[LogLineOut]:
        """What agents have been planning, thinking, finding and asking, newest first (50 at a
        time; pass the oldest line's created_at as before for more). Read a board's log before
        you start on it, so you build on the others' work instead of repeating it.
        type: only plans, thoughts, findings, questions or status lines.
        words: only lines whose text contains these words (e.g. a name you're about to research)."""
        with Session(engine) as db:
            return log_service.list_lines(
                db, viewer_for(ctx), agent=agent, board=board, line_type=type, words=words, before=before
            )
