"""
Run endpoints:

  POST /api/runs               start a run; its kit (with the token) comes back once
                               (the owner for any agent, or an agent for itself)
  GET  /api/runs?agent=        runs, newest first (owner only)
  GET  /api/runs/{id}          one run: its brief, state, scopes, what it added
                               (the owner, or the run's agent)
  POST /api/runs/{id}/finish   end it with a summary; its token stops working
                               (the owner, or the run's agent)

Agents on a run read and finish it with the get_my_run and finish_run tools
(agent_server/run_tools.py).
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from app.auth.owner_auth import require_owner
from app.auth.viewer import Viewer, current_viewer
from app.database import get_db
from app.features.runs import service
from app.features.runs.models import Run
from app.features.runs.schemas import RunCreate, RunFinish, RunKit, RunOut

router = APIRouter(prefix="/runs", tags=["runs"])


def _visible(run_id: str, viewer: Viewer, db: Session) -> Run:
    run = service.get_run(db, run_id)
    if run is None or not service.can_see_run(viewer, run):
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.post("", response_model=RunKit)
def start_run(data: RunCreate, request: Request, viewer: Viewer = Depends(current_viewer), db: Session = Depends(get_db)):
    try:
        run, token = service.start_run(db, data, viewer)
    except service.RunNotAllowedError as error:
        raise HTTPException(status_code=403, detail=str(error))
    return service.make_kit(db, run, token, str(request.base_url))


@router.get("", response_model=list[RunOut], dependencies=[Depends(require_owner)])
def list_runs(agent: str | None = None, db: Session = Depends(get_db)):
    return service.list_runs(db, agent)


@router.get("/{run_id}", response_model=RunOut)
def get_run(run_id: str, viewer: Viewer = Depends(current_viewer), db: Session = Depends(get_db)):
    return service.describe_run(db, _visible(run_id, viewer, db))


@router.post("/{run_id}/finish", response_model=RunOut)
def finish_run(run_id: str, data: RunFinish, viewer: Viewer = Depends(current_viewer), db: Session = Depends(get_db)):
    run = service.finish_run(db, _visible(run_id, viewer, db), data.summary)
    return service.describe_run(db, run)
