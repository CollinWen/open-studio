"""
Agent endpoints:

  GET    /api/agents                every agent: status, boards, last seen (anyone)
  GET    /api/agents/{name}         one agent (anyone)
  POST   /api/agents                add an agent; its token comes back once (owner only)
  PATCH  /api/agents/{name}         change its description, or pause it (owner only)
  POST   /api/agents/{name}/token   give it a new token; the old one stops working (owner only)
  DELETE /api/agents/{name}         remove it (owner only)

Which boards an agent may add to is changed on the board (PATCH /api/boards/{slug}).
What agents are thinking and doing is in agent_log/routes.py.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.auth.owner_auth import require_owner
from app.database import get_db
from app.features.agents import service
from app.features.agents.models import Agent
from app.features.agents.schemas import AgentCreate, AgentOut, AgentUpdate, AgentWithToken

router = APIRouter(prefix="/agents", tags=["agents"])


def _found(name: str, db: Session) -> Agent:
    agent = service.get_agent(db, name)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.get("", response_model=list[AgentOut])
def list_agents(db: Session = Depends(get_db)):
    return service.list_agents(db)


@router.get("/{name}", response_model=AgentOut)
def get_agent(name: str, db: Session = Depends(get_db)):
    return service.describe_agent(db, _found(name, db))


@router.post("", response_model=AgentWithToken, dependencies=[Depends(require_owner)])
def create_agent(data: AgentCreate, db: Session = Depends(get_db)):
    try:
        agent, token = service.create_agent(db, data)
    except service.AgentExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))
    return AgentWithToken(agent=service.describe_agent(db, agent), token=token)


@router.patch("/{name}", response_model=AgentOut, dependencies=[Depends(require_owner)])
def update_agent(name: str, changes: AgentUpdate, db: Session = Depends(get_db)):
    return service.describe_agent(db, service.update_agent(db, _found(name, db), changes))


@router.post("/{name}/token", response_model=AgentWithToken, dependencies=[Depends(require_owner)])
def renew_token(name: str, db: Session = Depends(get_db)):
    agent = _found(name, db)
    token = service.renew_token(db, agent)
    return AgentWithToken(agent=service.describe_agent(db, agent), token=token)


@router.delete("/{name}", status_code=204, dependencies=[Depends(require_owner)])
def remove_agent(name: str, db: Session = Depends(get_db)):
    service.remove_agent(db, _found(name, db))
