"""
Agent service: the owner adding, pausing, re-keying and removing agents, and
an agent setting its own status line.

Which boards an agent may add to is kept on each board, so adding an agent
with boards, and removing one, go through boards/service.py. AGENT_TOKENS in
backend/.env is only a starting list: on startup any agent named there that
isn't in the studio yet is added with that token. After that the studio
page is where agents are managed.
Used by agents/routes.py, agent_server/log_tools.py and main.py.
"""

from sqlmodel import Session, select

from app.config import settings
from app.features.agents.agent_tokens import fingerprint, make_token
from app.features.agents.models import Agent
from app.features.agents.schemas import AgentCreate, AgentOut, AgentUpdate
from app.features.boards import service as boards_service
from app.features.boards.schemas import BoardUpdate

STATUS_MAX_LENGTH = 200


class AgentExistsError(Exception):
    """An agent with this name is already there."""


def ensure_agents_from_settings(db: Session) -> None:
    for token, name in settings.agent_tokens.items():
        if db.get(Agent, name) is None:
            db.add(Agent(name=name, token_hash=fingerprint(token)))
    db.commit()


def list_agents(db: Session) -> list[AgentOut]:
    """Most recently seen first; agents never seen yet at the end, newest first."""
    agents = list(db.exec(select(Agent).order_by(Agent.created_at.desc())))
    seen = sorted((agent for agent in agents if agent.last_seen_at), key=lambda a: a.last_seen_at, reverse=True)
    never_seen = [agent for agent in agents if not agent.last_seen_at]
    return [describe_agent(db, agent) for agent in [*seen, *never_seen]]


def get_agent(db: Session, name: str) -> Agent | None:
    return db.get(Agent, name)


def describe_agent(db: Session, agent: Agent) -> AgentOut:
    boards = [board.slug for board in boards_service.list_boards(db) if agent.name in board.agents]
    return AgentOut(**agent.model_dump(exclude={"token_hash"}), boards=boards)


def create_agent(db: Session, data: AgentCreate) -> tuple[Agent, str]:
    """The new agent and its token (shown to the owner once)."""
    if db.get(Agent, data.name) is not None:
        raise AgentExistsError(f"Agent {data.name} already exists")
    token = make_token()
    agent = Agent(name=data.name, description=data.description, token_hash=fingerprint(token))
    db.add(agent)
    db.commit()
    for slug in data.boards:
        board = boards_service.get_board(db, slug)
        if board is not None and agent.name not in board.agents:
            boards_service.update_board(db, board, BoardUpdate(agents=[*board.agents, agent.name]))
    db.refresh(agent)
    return agent, token


def update_agent(db: Session, agent: Agent, changes: AgentUpdate) -> Agent:
    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(agent, field, value)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


def renew_token(db: Session, agent: Agent) -> str:
    """A new token; the old one stops working at once."""
    token = make_token()
    agent.token_hash = fingerprint(token)
    db.add(agent)
    db.commit()
    return token


def remove_agent(db: Session, agent: Agent) -> None:
    """Take it off every board and forget it. What it added and logged stays, signed with its name."""
    for board in boards_service.list_boards(db):
        if agent.name in board.agents:
            remaining = [name for name in board.agents if name != agent.name]
            boards_service.update_board(db, board, BoardUpdate(agents=remaining))
    db.delete(agent)
    db.commit()


def set_status(db: Session, agent_name: str, status: str) -> Agent:
    agent = db.get(Agent, agent_name)
    agent.status = status.strip()[:STATUS_MAX_LENGTH]
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent
