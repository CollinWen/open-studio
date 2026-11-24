"""
Agent endpoints:

  GET    /api/agents                every agent: status, boards, last seen (anyone)
  GET    /api/agents/export         every agent as agents.yaml: boards, tools, skills; no tokens (owner only)
  GET    /api/agents/{name}         one agent (anyone)
  POST   /api/agents                add an agent (owner only)
  PATCH  /api/agents/{name}         change its description, boards or outside tools, or pause it (owner only)
  DELETE /api/agents/{name}         remove it; its tokens stop working (owner only)

Agents have no token of their own: the owner issues one per session with
POST /api/runs (runs/routes.py). A board's agents can also be changed on the
board (PATCH /api/boards/{slug}).
What agents are thinking and doing is in agent_log/routes.py.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlmodel import Session

from app.auth.owner_auth import require_owner
from app.database import get_db
from app.features.agents import service
from app.features.agents.agents_yaml import write_agents_yaml
from app.features.agents.models import Agent
from app.features.agents.schemas import AgentCreate, AgentOut, AgentUpdate

router = APIRouter(prefix="/agents", tags=["agents"])


def _found(name: str, db: Session) -> Agent:
    agent = service.get_agent(db, name)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.get("", response_model=list[AgentOut])
def list_agents(db: Session = Depends(get_db)):
    return service.list_agents(db)


@router.get("/export", response_class=PlainTextResponse, dependencies=[Depends(require_owner)])
def export_agents(db: Session = Depends(get_db)):
    headers = {"Content-Disposition": 'attachment; filename="agents.yaml"'}
    return PlainTextResponse(write_agents_yaml(service.list_agents(db)), media_type="application/yaml", headers=headers)


@router.get("/{name}", response_model=AgentOut)
def get_agent(name: str, db: Session = Depends(get_db)):
    return service.describe_agent(db, _found(name, db))


@router.post("", response_model=AgentOut, dependencies=[Depends(require_owner)])
def create_agent(data: AgentCreate, db: Session = Depends(get_db)):
    try:
        agent = service.create_agent(db, data)
    except service.AgentExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))
    return service.describe_agent(db, agent)


@router.patch("/{name}", response_model=AgentOut, dependencies=[Depends(require_owner)])
def update_agent(name: str, changes: AgentUpdate, db: Session = Depends(get_db)):
    return service.describe_agent(db, service.update_agent(db, _found(name, db), changes))


@router.delete("/{name}", status_code=204, dependencies=[Depends(require_owner)])
def remove_agent(name: str, db: Session = Depends(get_db)):
    service.remove_agent(db, _found(name, db))
