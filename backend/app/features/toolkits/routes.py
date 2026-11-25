"""
Toolkit endpoints:

  GET  /api/toolkits/tools                 the toolkit tools the caller's run may call, each
                                           with what it does, its input schema and its
                                           pinned arguments (an agent on a run token)
  POST /api/toolkits/tools/{tool}          call one, body {"arguments": {...}}; it runs on
                                           Composio as the account the owner chose, once the
                                           studio has checked it (an agent on a run token)
  GET  /api/toolkits/{toolkit}/catalog?q=  every tool of a toolkit on Composio, to pick an
                                           agent's tools from (owner only)

Agents with MCP use list_toolkit_tools and call_toolkit_tool instead
(agent_server/toolkit_tools.py). What each agent is granted is saved on the
agent (agents/routes.py); which toolkits a run may use, on the run.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Path as PathPart
from sqlmodel import Session

from app.auth.owner_auth import require_owner
from app.auth.viewer import Viewer, current_viewer
from app.database import get_db
from app.features.toolkits import service
from app.features.toolkits.schemas import CatalogTool, ToolkitCall, ToolkitCallResult, ToolkitTool

TOOLKIT_NAME = r"^[a-z0-9][a-z0-9_]{0,59}$"

router = APIRouter(prefix="/toolkits", tags=["toolkits"])


@router.get("/tools", response_model=list[ToolkitTool])
def list_run_tools(viewer: Viewer = Depends(current_viewer), db: Session = Depends(get_db)):
    try:
        return service.list_run_tools(db, viewer)
    except service.ToolkitRefusedError as error:
        raise HTTPException(status_code=403, detail=str(error))


@router.post("/tools/{tool}", response_model=ToolkitCallResult)
def call_run_tool(tool: str, call: ToolkitCall, viewer: Viewer = Depends(current_viewer), db: Session = Depends(get_db)):
    try:
        return service.call_run_tool(db, viewer, tool, call.arguments)
    except service.ToolkitRefusedError as error:
        raise HTTPException(status_code=403, detail=str(error))
    except service.ToolkitUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error))


@router.get("/{toolkit}/catalog", response_model=list[CatalogTool], dependencies=[Depends(require_owner)])
def list_catalog(toolkit: str = PathPart(pattern=TOOLKIT_NAME), q: str = ""):
    try:
        return service.list_catalog(toolkit, q)
    except service.ToolkitUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error))
