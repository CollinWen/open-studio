"""
Board service: listing, making and changing boards, and who may add entries
to which board.

The owner may add to any board. An agent may add only to boards that list its
name; that keeps each agent's work inside the effort it was signed on to.
Used by boards/routes.py, entries/service.py and agent_server/.
"""

from sqlmodel import Session, select

from app.auth.viewer import Viewer
from app.features.boards.models import HOME_BOARD, Board
from app.features.boards.schemas import BoardCreate, BoardUpdate


class BoardExistsError(Exception):
    """A board with this slug is already there."""


def ensure_home_board(db: Session) -> None:
    """The home board always exists; every entry without a board belongs to it."""
    if db.get(Board, HOME_BOARD) is None:
        db.add(Board(slug=HOME_BOARD, name="Home", description="The owner's own collection."))
        db.commit()


def list_boards(db: Session) -> list[Board]:
    """Home first, then the others in the order they were made."""
    boards = list(db.exec(select(Board).order_by(Board.created_at)))
    return sorted(boards, key=lambda board: board.slug != HOME_BOARD)


def get_board(db: Session, slug: str) -> Board | None:
    return db.get(Board, slug)


def create_board(db: Session, data: BoardCreate) -> Board:
    if db.get(Board, data.slug) is not None:
        raise BoardExistsError(f"Board {data.slug} already exists")
    board = Board(**data.model_dump())
    db.add(board)
    db.commit()
    db.refresh(board)
    return board


def update_board(db: Session, board: Board, changes: BoardUpdate) -> Board:
    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(board, field, value)
    db.add(board)
    db.commit()
    db.refresh(board)
    return board


def can_add_to_board(viewer: Viewer, board: Board) -> bool:
    return viewer.is_owner or (viewer.is_agent and viewer.agent_name in board.agents)
