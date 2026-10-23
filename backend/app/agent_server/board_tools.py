"""
Board tools: how an agent finds the boards and reads one board's brief (what
it's for, its key tags, its most used tags) before going to work on it.

Anyone may call these. Registered by server.py.
"""

from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel
from sqlmodel import Session

from app.agent_server.tool_viewer import viewer_for
from app.database import engine
from app.features.boards import service as boards_service
from app.features.boards.schemas import BoardOut
from app.features.tags import service as tags_service
from app.features.tags.models import NORMAL
from app.features.tags.schemas import TagInfo

MOST_USED_TAG_COUNT = 30


class BoardForAgent(BoardOut):
    you_can_add: bool


class BoardBrief(BaseModel):
    board: BoardForAgent
    key_tags: list[TagInfo]
    most_used_tags: list[TagInfo]


def register_board_tools(server: MCPServer) -> None:
    @server.tool()
    def list_boards(ctx: Context) -> list[BoardForAgent]:
        """Every board: a separate space in the studio with its own focus. you_can_add says
        whether you're signed on to add entries there. "home" is the owner's own collection."""
        viewer = viewer_for(ctx)
        with Session(engine) as db:
            return [_for_agent(board, viewer) for board in boards_service.list_boards(db)]

    @server.tool()
    def get_board_brief(board: str, ctx: Context) -> BoardBrief:
        """Start here before working on a board: what it is for (its description is your brief),
        its key tags (with what each means), and its most used tags."""
        viewer = viewer_for(ctx)
        with Session(engine) as db:
            found = boards_service.get_board(db, board)
            if found is None:
                raise ToolError(f"No board {board}")
            tags = tags_service.list_tags(db, viewer, board=board)
            return BoardBrief(
                board=_for_agent(found, viewer),
                key_tags=[tag for tag in tags if tag.importance > NORMAL],
                most_used_tags=sorted(tags, key=lambda tag: -tag.count)[:MOST_USED_TAG_COUNT],
            )


def _for_agent(board, viewer) -> BoardForAgent:
    return BoardForAgent(
        **BoardOut.model_validate(board).model_dump(),
        you_can_add=boards_service.can_add_to_board(viewer, board),
    )
