"""
Agent service: the owner adding, changing, pausing and removing agents
(their description, boards and outside tools), and an agent setting its own
status line.

Which boards an agent may add to is kept on each board, so setting an
agent's boards, and removing one, go through boards/service.py. Agents have
no token of their own: the owner issues each session's token as a run
(runs/service.py).
Used by agents/routes.py and agent_server/log_tools.py.
"""

from sqlmodel import Session, select

from app.features.agents.models import Agent
from app.features.agents.schemas import AgentCreate, AgentOut, AgentUpdate
from app.features.boards import service as boards_service
from app.features.boards.models import Board
from app.features.boards.schemas import BoardUpdate

STATUS_MAX_LENGTH = 200


class AgentExistsError(Exception):
    """An agent with this name is already there."""


def list_agents(db: Session) -> list[AgentOut]:
    """Most recently seen first; agents never seen yet at the end, newest first."""
    agents = list(db.exec(select(Agent).order_by(Agent.created_at.desc())))
    seen = sorted((agent for agent in agents if agent.last_seen_at), key=lambda a: a.last_seen_at, reverse=True)
    never_seen = [agent for agent in agents if not agent.last_seen_at]
    boards = boards_service.list_boards(db)  # read once, not once per agent
    return [_describe(agent, boards) for agent in [*seen, *never_seen]]


def get_agent(db: Session, name: str) -> Agent | None:
    return db.get(Agent, name)


def describe_agent(db: Session, agent: Agent) -> AgentOut:
    return _describe(agent, boards_service.list_boards(db))


def _describe(agent: Agent, boards: list[Board]) -> AgentOut:
    return AgentOut(**agent.model_dump(), boards=[board.slug for board in boards if agent.name in board.agents])


def create_agent(db: Session, data: AgentCreate) -> Agent:
    if db.get(Agent, data.name) is not None:
        raise AgentExistsError(f"Agent {data.name} already exists")
    agent = Agent(name=data.name, description=data.description, tools=data.tools, skills=data.skills)
    db.add(agent)
    db.commit()
    _sign_on_to_boards(db, agent.name, data.boards)
    db.refresh(agent)
    return agent


def update_agent(db: Session, agent: Agent, changes: AgentUpdate) -> Agent:
    fields = changes.model_dump(exclude_unset=True)
    boards = fields.pop("boards", None)
    for field, value in fields.items():
        setattr(agent, field, value)
    db.add(agent)
    db.commit()
    if boards is not None:
        _sign_on_to_boards(db, agent.name, boards)
    db.refresh(agent)
    return agent


def _sign_on_to_boards(db: Session, name: str, slugs: list[str]) -> None:
    """Put the agent on exactly these boards (unknown slugs are skipped)."""
    for board in boards_service.list_boards(db):
        on = name in board.agents
        if board.slug in slugs and not on:
            boards_service.update_board(db, board, BoardUpdate(agents=[*board.agents, name]))
        elif board.slug not in slugs and on:
            boards_service.update_board(db, board, BoardUpdate(agents=[n for n in board.agents if n != name]))


def remove_agent(db: Session, agent: Agent) -> None:
    """Take it off every board and forget it; its tokens stop working. What it added and
    logged stays, signed with its name."""
    _sign_on_to_boards(db, agent.name, [])
    db.delete(agent)
    db.commit()


def set_status(db: Session, agent_name: str, status: str) -> Agent:
    agent = db.get(Agent, agent_name)
    agent.status = status.strip()[:STATUS_MAX_LENGTH]
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent
