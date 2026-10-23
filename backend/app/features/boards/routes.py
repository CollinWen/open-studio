"""
Board endpoints:

  GET   /api/boards           every board, home first
  GET   /api/boards/{slug}    one board
  POST  /api/boards           make a board (owner only)
  PATCH /api/boards/{slug}    change a board's name, description or agents (owner only)

A board's entries come from GET /api/entries?board=<slug>.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.auth.owner_auth import require_owner
from app.database import get_db
from app.features.boards import service
from app.features.boards.schemas import BoardCreate, BoardOut, BoardUpdate

router = APIRouter(prefix="/boards", tags=["boards"])


@router.get("", response_model=list[BoardOut])
def list_boards(db: Session = Depends(get_db)):
    return service.list_boards(db)


@router.get("/{slug}", response_model=BoardOut)
def get_board(slug: str, db: Session = Depends(get_db)):
    board = service.get_board(db, slug)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


@router.post("", response_model=BoardOut, dependencies=[Depends(require_owner)])
def create_board(data: BoardCreate, db: Session = Depends(get_db)):
    try:
        return service.create_board(db, data)
    except service.BoardExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))


@router.patch("/{slug}", response_model=BoardOut, dependencies=[Depends(require_owner)])
def update_board(slug: str, changes: BoardUpdate, db: Session = Depends(get_db)):
    board = service.get_board(db, slug)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    return service.update_board(db, board, changes)
