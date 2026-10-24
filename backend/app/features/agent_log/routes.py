"""
Agent log endpoints:

  GET  /api/agent-log    what agents are planning, thinking, finding and asking,
                         newest first (anyone). Narrow with ?agent=, ?board=;
                         ?before=<created_at> for the next page.
  POST /api/agent-log    write one line {board, type, text, entry_id} (agents only)

Agents usually write through the agent server instead (agent_server/log_tools.py).
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.auth.viewer import Viewer, current_viewer
from app.database import get_db
from app.features.agent_log import service
from app.features.agent_log.schemas import LogLineCreate, LogLineOut

router = APIRouter(prefix="/agent-log", tags=["agent log"])


@router.get("", response_model=list[LogLineOut])
def list_lines(
    agent: str | None = None,
    board: str | None = None,
    before: datetime | None = None,
    db: Session = Depends(get_db),
    viewer: Viewer = Depends(current_viewer),
):
    return service.list_lines(db, viewer, agent=agent, board=board, before=before)


@router.post("", response_model=LogLineOut)
def add_line(data: LogLineCreate, db: Session = Depends(get_db), viewer: Viewer = Depends(current_viewer)):
    try:
        return service.add_line(db, viewer, data)
    except service.LogNotAllowedError as error:
        raise HTTPException(status_code=403, detail=str(error))
    except service.LogLimitError as error:
        raise HTTPException(status_code=429, detail=str(error))
