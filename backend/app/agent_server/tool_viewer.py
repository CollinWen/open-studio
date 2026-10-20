"""
Tool viewer: works out who is calling an agent tool from the request's
Authorization header, exactly as the web routes do, and turns refusals into
tool errors the agent can read.

Used by read_tools.py and write_tools.py.
"""

from collections.abc import Iterator
from contextlib import contextmanager

from fastapi import HTTPException
from mcp.server.mcpserver import Context
from mcp.server.mcpserver.exceptions import ToolError

from app.auth.viewer import Viewer, check_can_write, identify_viewer


def viewer_for(ctx: Context) -> Viewer:
    headers = ctx.headers or {}
    return identify_viewer(headers.get("authorization"))


def writer_for(ctx: Context) -> Viewer:
    """The calling viewer, if it may write now (owner, or an agent within its hourly limit)."""
    viewer = viewer_for(ctx)
    with refusals_as_tool_errors():
        check_can_write(viewer)
    return viewer


@contextmanager
def refusals_as_tool_errors() -> Iterator[None]:
    try:
        yield
    except HTTPException as error:
        raise ToolError(str(error.detail)) from error
