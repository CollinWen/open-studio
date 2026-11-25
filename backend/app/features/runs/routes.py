"""
Run endpoints:

  POST /api/runs               issue a token for an agent, which starts a run (one
                               session); its kit (with the token) comes back once
                               (owner only)
  GET  /api/runs?agent=        runs, newest first (owner only)
  GET  /api/runs/{id}          one run: its brief, state, scopes, what it added
                               (the owner, or the run's agent)
  GET  /api/runs/{id}/sandbox?harness=pi|claude_code
                               what a fresh sandbox needs to start the run in that
                               harness: the files for the run's folder (prompt,
                               skills, studio connection) and the start command
                               (the owner, or the run's agent, while it's live)
  GET  /api/runs/{id}/sandbox.sh?harness=pi|claude_code
                               the same, as the shell script the kit's lines run;
                               a refusal is a script too, which says why
  POST /api/runs/{id}/session  note where the harness keeps its session (a link the
                               owner can follow to watch the agent work)
                               (the owner, or the run's agent, while it's live; only
                               to a site in SESSION_LINK_SITES)
  POST /api/runs/{id}/finish   end it with a summary; its token stops working
                               (the owner, or the run's agent)

Agents on a run read it, leave their session link and finish it with the
get_my_run, set_run_session and finish_run tools
(agent_server/run_tools.py).
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from sqlmodel import Session

from app.auth.owner_auth import require_owner
from app.auth.viewer import Viewer, current_viewer
from app.database import get_db
from app.features.runs import service
from app.features.runs.models import Run
from app.features.runs.sandbox_script import write_refusal_script, write_sandbox_script
from app.features.runs.schemas import HarnessName, RunCreate, RunFinish, RunKit, RunOut, RunSession, SandboxSetup
from app.features.skills.service import SkillsUnavailableError, UnknownSkillsError

router = APIRouter(prefix="/runs", tags=["runs"])


def _visible(run_id: str, viewer: Viewer, db: Session) -> Run:
    run = service.get_run(db, run_id)
    if run is None or not service.can_see_run(viewer, run):
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.post("", response_model=RunKit, dependencies=[Depends(require_owner)])
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


@router.get("/{run_id}/sandbox", response_model=SandboxSetup)
def get_sandbox_setup(
    run_id: str,
    request: Request,
    harness: HarnessName = "pi",
    viewer: Viewer = Depends(current_viewer),
    db: Session = Depends(get_db),
):
    if viewer.role == "visitor":
        raise HTTPException(
            status_code=401,
            detail="No live run token: set OPEN_STUDIO_TOKEN to the token from the run's kit "
            "(a token stops working when its run finishes or runs out, or its agent is paused)",
        )
    run = _visible(run_id, viewer, db)
    try:
        return service.make_sandbox_setup(db, run, harness, str(request.base_url))
    except service.RunNotAllowedError as error:
        raise HTTPException(status_code=409, detail=str(error))
    except UnknownSkillsError as error:
        raise HTTPException(status_code=409, detail=f"{error}. Check AGENT_RESOURCES or the agent's skills")
    except SkillsUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error))


@router.get("/{run_id}/sandbox.sh", response_class=PlainTextResponse)
def get_sandbox_script(
    run_id: str,
    request: Request,
    harness: HarnessName = "pi",
    viewer: Viewer = Depends(current_viewer),
    db: Session = Depends(get_db),
):
    try:
        setup = get_sandbox_setup(run_id, request, harness, viewer, db)
    except HTTPException as error:
        return PlainTextResponse(write_refusal_script(str(error.detail)), status_code=error.status_code)
    return PlainTextResponse(write_sandbox_script(setup), media_type="text/x-shellscript")


@router.post("/{run_id}/session", response_model=RunOut)
def set_run_session(run_id: str, data: RunSession, viewer: Viewer = Depends(current_viewer), db: Session = Depends(get_db)):
    try:
        run = service.set_run_session(db, _visible(run_id, viewer, db), data.url)
    except service.SessionSiteNotAllowedError as error:
        raise HTTPException(status_code=422, detail=str(error))
    except service.RunNotAllowedError as error:
        raise HTTPException(status_code=409, detail=str(error))
    return service.describe_run(db, run)


@router.post("/{run_id}/finish", response_model=RunOut)
def finish_run(run_id: str, data: RunFinish, viewer: Viewer = Depends(current_viewer), db: Session = Depends(get_db)):
    run = service.finish_run(db, _visible(run_id, viewer, db), data.summary)
    return service.describe_run(db, run)
