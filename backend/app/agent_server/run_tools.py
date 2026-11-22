"""
Run tools: how an agent on a run token reads its task (the owner's brief,
its board, where to start, what it may use, when it ends), leaves a link to
its harness's own session (for the owner to watch), and finishes it with a
summary, which ends the run and its token.

All need a run token (runs/routes.py starts runs and hands out the token).
The rules are in runs/service.py. Registered by server.py.
"""

from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import ValidationError
from sqlmodel import Session

from app.agent_server.tool_viewer import viewer_for
from app.auth.viewer import Viewer
from app.database import engine
from app.features.runs import service as runs_service
from app.features.runs.models import Run
from app.features.runs.schemas import RunOut, RunSession


def register_run_tools(server: MCPServer) -> None:
    @server.tool()
    def get_my_run(ctx: Context) -> RunOut:
        """Your run: the task kind, the owner's brief (in their words), the board you may add
        to, the entry to start from, the outside tools you may use (scopes), when your token
        stops working, and the entries you've added so far."""
        viewer = viewer_for(ctx)
        with Session(engine) as db:
            return runs_service.describe_run(db, _own_run(db, viewer))

    @server.tool()
    def set_run_session(url: str, ctx: Context) -> RunOut:
        """If your harness keeps a page for this session (e.g. a claude.ai/code session link),
        leave it here once, when you start, so the owner can watch how you work. Only the owner
        sees it. Skip this if there's no such link."""
        viewer = viewer_for(ctx)
        try:
            url = RunSession(url=url).url
        except ValidationError as error:
            raise ToolError(error.errors()[0]["msg"])
        with Session(engine) as db:
            try:
                run = runs_service.set_run_session(db, _own_run(db, viewer), url)
            except runs_service.RunNotAllowedError as error:
                raise ToolError(str(error))
            return runs_service.describe_run(db, run)

    @server.tool()
    def finish_run(summary: str, ctx: Context) -> RunOut:
        """End your run when the task is done. summary: what you did and found, in a few plain
        sentences, with what the owner should read first and what's still open. Your token
        stops working once this returns."""
        viewer = viewer_for(ctx)
        with Session(engine) as db:
            return runs_service.describe_run(db, runs_service.finish_run(db, _own_run(db, viewer), summary))


def _own_run(db: Session, viewer: Viewer) -> Run:
    if not viewer.is_run:
        raise ToolError("This tool needs a run token (connect with the token from your run's kit)")
    run = runs_service.get_run(db, viewer.run_id)
    if run is None:
        raise ToolError(f"No run {viewer.run_id}")
    return run
