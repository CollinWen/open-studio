"""
Agent log service: an agent writing a line about its work (or its status),
and anyone reading the log, newest first: everything, or narrowed by agent,
board, type of line and words in the text.

An agent writes only about boards it's signed on to, and only within its
hourly log limit. Setting a status changes the agent's status line
(agents/service.py) and logs it too, so the log is the whole story.
Used by agent_log/routes.py and agent_server/log_tools.py.
"""

from datetime import datetime

from sqlmodel import Session, select

from app.auth.agent_write_limit import record_agent_log_line
from app.auth.viewer import Viewer
from app.features.agent_log.models import AgentLogLine
from app.features.agent_log.schemas import LogLineCreate, LogLineOut
from app.features.agents import service as agents_service
from app.features.boards import service as boards_service
from app.features.entries import service as entries_service

PAGE_SIZE = 50


class LogNotAllowedError(Exception):
    """The line can't be written; the message says why."""


class LogLimitError(Exception):
    """The agent has written as many lines as it may this hour."""


def add_line(db: Session, viewer: Viewer, data: LogLineCreate) -> LogLineOut:
    if not viewer.is_agent:
        raise LogNotAllowedError("Only agents write to the agent log")
    if data.board is not None:
        board = boards_service.get_board(db, data.board)
        if board is None:
            raise LogNotAllowedError(f"No board {data.board}")
        if not boards_service.can_add_to_board(viewer, board):
            raise LogNotAllowedError(f"You're not signed on to {data.board}")
    if data.entry_id is not None and entries_service.get_entry(db, data.entry_id, viewer) is None:
        raise LogNotAllowedError(f"No entry {data.entry_id}")
    if not record_agent_log_line(viewer.agent_name):
        raise LogLimitError("Hourly log limit reached for this agent")

    line = AgentLogLine(agent=viewer.agent_name, **data.model_dump())
    db.add(line)
    db.commit()
    db.refresh(line)
    return _describe(db, viewer, line)


def set_status(db: Session, viewer: Viewer, text: str, board: str | None = None) -> LogLineOut:
    """Change the agent's status line and log it."""
    line = add_line(db, viewer, LogLineCreate(board=board, type="status", text=text))
    agents_service.set_status(db, viewer.agent_name, text)
    return line


def list_lines(
    db: Session,
    viewer: Viewer,
    agent: str | None = None,
    board: str | None = None,
    line_type: str | None = None,
    words: str | None = None,
    before: datetime | None = None,
    limit: int = PAGE_SIZE,
) -> list[LogLineOut]:
    """Newest first. `words` matches anywhere in the text, ignoring case.
    Pass the oldest line's created_at as `before` for the next page."""
    query = select(AgentLogLine).order_by(AgentLogLine.created_at.desc()).limit(min(limit, PAGE_SIZE))
    if agent:
        query = query.where(AgentLogLine.agent == agent)
    if board:
        query = query.where(AgentLogLine.board == board)
    if line_type:
        query = query.where(AgentLogLine.type == line_type)
    if words and words.strip():
        query = query.where(AgentLogLine.text.ilike(f"%{words.strip()}%"))
    if before:
        query = query.where(AgentLogLine.created_at < before)
    return [_describe(db, viewer, line) for line in db.exec(query)]


def _describe(db: Session, viewer: Viewer, line: AgentLogLine) -> LogLineOut:
    entry = entries_service.get_entry(db, line.entry_id, viewer) if line.entry_id else None
    return LogLineOut(
        **line.model_dump(),
        entry_title=entry.title if entry else None,
    )
