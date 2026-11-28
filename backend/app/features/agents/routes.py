"""
Agent endpoints:

  GET    /api/agents                every agent: status, boards, add-ons, last seen (anyone; add-on
                                    instructions only for the owner)
  GET    /api/agents/export         every agent as agents.yaml: boards, skills, add-ons; no tokens (owner only)
  GET    /api/agents/{name}         one agent (anyone; its add-on instructions only for the owner)
  GET    /api/agents/{name}/agents-md  the AGENTS.md a run of it would get: its add-ons, skills,
                                    boards (owner only)
  POST   /api/agents                add an agent (owner only)
  PATCH  /api/agents/{name}         change its description, boards, skills, add-ons or instructions, or pause it
                                    (owner only)
  DELETE /api/agents/{name}         remove it; its tokens stop working (owner only)

Skills must be in the agent resources (GET /api/skills) and add-ons defined
(GET /api/addons); an unknown name is refused. Agents have no token of their own: the owner issues one per
session with POST /api/runs (runs/routes.py). A board's agents can also be changed on the
board (PATCH /api/boards/{slug}).
What agents are thinking and doing is in agent_log/routes.py.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlmodel import Session

from app.auth.owner_auth import require_owner
from app.auth.viewer import Viewer, current_viewer
from app.database import get_db
from app.features.agents import service
from app.features.agents.agents_yaml import write_agents_yaml
from app.features.agents.models import Agent
from app.features.agents.schemas import AgentCreate, AgentOut, AgentUpdate
from app.features.addons.service import UnknownAddonsError
from app.features.runs import service as runs_service
from app.features.skills.service import SkillsUnavailableError, UnknownSkillsError

router = APIRouter(prefix="/agents", tags=["agents"])


def _found(name: str, db: Session) -> Agent:
    agent = service.get_agent(db, name)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.get("", response_model=list[AgentOut])
def list_agents(viewer: Viewer = Depends(current_viewer), db: Session = Depends(get_db)):
    return service.list_agents(db, for_owner=viewer.is_owner)


@router.get("/export", response_class=PlainTextResponse, dependencies=[Depends(require_owner)])
def export_agents(db: Session = Depends(get_db)):
    headers = {"Content-Disposition": 'attachment; filename="agents.yaml"'}
    agents = service.list_agents(db, for_owner=True)
    return PlainTextResponse(write_agents_yaml(agents), media_type="application/yaml", headers=headers)


@router.get("/{name}", response_model=AgentOut)
def get_agent(name: str, viewer: Viewer = Depends(current_viewer), db: Session = Depends(get_db)):
    return service.describe_agent(db, _found(name, db), for_owner=viewer.is_owner)


@router.get("/{name}/agents-md", response_class=PlainTextResponse, dependencies=[Depends(require_owner)])
def preview_agents_md(name: str, db: Session = Depends(get_db)):
    return PlainTextResponse(runs_service.preview_agents_md(db, _found(name, db)), media_type="text/markdown")


@router.post("", response_model=AgentOut, dependencies=[Depends(require_owner)])
def create_agent(data: AgentCreate, db: Session = Depends(get_db)):
    try:
        agent = service.create_agent(db, data)
    except service.AgentExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))
    except (UnknownSkillsError, UnknownAddonsError) as error:
        raise HTTPException(status_code=422, detail=str(error))
    except SkillsUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error))
    return service.describe_agent(db, agent, for_owner=True)


@router.patch("/{name}", response_model=AgentOut, dependencies=[Depends(require_owner)])
def update_agent(name: str, changes: AgentUpdate, db: Session = Depends(get_db)):
    try:
        agent = service.update_agent(db, _found(name, db), changes)
    except (UnknownSkillsError, UnknownAddonsError) as error:
        raise HTTPException(status_code=422, detail=str(error))
    except SkillsUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error))
    return service.describe_agent(db, agent, for_owner=True)


@router.delete("/{name}", status_code=204, dependencies=[Depends(require_owner)])
def remove_agent(name: str, db: Session = Depends(get_db)):
    service.remove_agent(db, _found(name, db))
