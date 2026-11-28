"""
Add-on endpoints:

  GET    /api/addons                    every add-on: kind, service, account, guide (owner only)
  POST   /api/addons                    define one; its guide starts from a template (owner only)
  PATCH  /api/addons/{name}             change its guide (owner only)
  DELETE /api/addons/{name}             remove one; the built-in ones stay (owner only)
  GET    /api/addons/{name}/catalog?q=  a Composio add-on's tools, with Composio's hints (owner only)
  POST   /api/addons/{name}/connect     a Connect Link: Composio's sign-in page for it (owner only)
  POST   /api/addons/{name}/connection  keep the account it came back with, once Composio confirms it
                                        (owner only)

  GET    /api/addon-tools?q=            the tools of the caller's run's Composio add-ons (a run token)
  POST   /api/addon-tools/{tool}        run one, body {"arguments": {...}} (a run token)

Which agents use an add-on, and the owner's instructions for each, are on
the agent (agents/routes.py). Agents with MCP use list_addon_tools and
call_addon_tool instead (agent_server/addon_tools.py).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.auth.owner_auth import require_owner
from app.auth.viewer import Viewer, current_viewer
from app.database import get_db
from app.features.addons import connections, relay, service
from app.features.addons.models import Addon
from app.features.addons.schemas import (
    AddonCall,
    AddonCallResult,
    AddonCreate,
    AddonOut,
    AddonTool,
    AddonUpdate,
    CatalogTool,
    ConnectionSave,
    ConnectLink,
    ConnectRequest,
)

router = APIRouter(prefix="/addons", tags=["addons"], dependencies=[Depends(require_owner)])
tools_router = APIRouter(prefix="/addon-tools", tags=["addons"])


def _found(name: str, db: Session) -> Addon:
    addon = service.get_addon(db, name)
    if addon is None:
        raise HTTPException(status_code=404, detail="Add-on not found")
    return addon


@router.get("", response_model=list[AddonOut])
def list_addons(db: Session = Depends(get_db)):
    return [service.describe_addon(addon) for addon in service.list_addons(db)]


@router.post("", response_model=AddonOut)
def create_addon(data: AddonCreate, db: Session = Depends(get_db)):
    try:
        return service.describe_addon(service.create_addon(db, data))
    except service.AddonExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))


@router.patch("/{name}", response_model=AddonOut)
def update_addon(name: str, changes: AddonUpdate, db: Session = Depends(get_db)):
    return service.describe_addon(service.update_guide(db, _found(name, db), changes.guide))


@router.delete("/{name}", status_code=204)
def remove_addon(name: str, db: Session = Depends(get_db)):
    try:
        service.remove_addon(db, _found(name, db))
    except service.AddonNotAllowedError as error:
        raise HTTPException(status_code=409, detail=str(error))


@router.get("/{name}/catalog", response_model=list[CatalogTool])
def list_catalog(name: str, q: str = "", db: Session = Depends(get_db)):
    try:
        return service.list_catalog(_found(name, db), q)
    except service.AddonNotAllowedError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except service.CatalogUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error))


@router.post("/{name}/connect", response_model=ConnectLink)
def start_connection(name: str, data: ConnectRequest, db: Session = Depends(get_db)):
    try:
        return ConnectLink(url=connections.start_connection(_found(name, db), data.return_url))
    except connections.ConnectionNotAllowedError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except connections.ConnectionUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error))


@router.post("/{name}/connection", response_model=AddonOut)
def save_connection(name: str, data: ConnectionSave, db: Session = Depends(get_db)):
    try:
        addon = connections.save_connection(db, _found(name, db), data.connected_account_id)
    except connections.ConnectionNotAllowedError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except connections.ConnectionUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error))
    return service.describe_addon(addon)


@tools_router.get("", response_model=list[AddonTool])
def list_run_tools(q: str = "", viewer: Viewer = Depends(current_viewer), db: Session = Depends(get_db)):
    try:
        return relay.list_run_tools(db, viewer, q)
    except relay.AddonRefusedError as error:
        raise HTTPException(status_code=403, detail=str(error))
    except relay.AddonUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error))


@tools_router.post("/{tool}", response_model=AddonCallResult)
def call_run_tool(tool: str, call: AddonCall, viewer: Viewer = Depends(current_viewer), db: Session = Depends(get_db)):
    try:
        return relay.call_run_tool(db, viewer, tool, call.arguments)
    except relay.AddonRefusedError as error:
        raise HTTPException(status_code=403, detail=str(error))
    except relay.AddonUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error))
