"""
Viewer: who is making a request (a visitor, an agent or the owner) and what
name their writes are recorded under.

Agents are other programs the owner has let in from the studio page (or
AGENT_TOKENS in backend/.env, added on startup): a Claude session, a research
bot. Their tokens are checked against the agents table (agents/agent_tokens.py);
a paused agent counts as a visitor. They can read the studio and add entries,
which arrive unlisted for the owner to publish.

An agent can also come in on a run token (auth/run_tokens.py): a short-lived
pass for one task, whose scopes narrow what the agent may do to one board.
It stops working when it expires, when its run is finished, or when its agent
is paused. Everything the agent writes on it carries the run's id.
Used by every route that reads or writes entries, and by agent_server/.
What each kind of viewer may see or edit lives in entries/visibility_rules.py.
"""

from dataclasses import dataclass
from typing import Literal

from fastapi import Depends, Header, HTTPException
from sqlmodel import Session

from app.auth.agent_write_limit import record_agent_write
from app.auth.owner_auth import is_owner
from app.auth.run_tokens import looks_like_run_token, read_run_token
from app.database import engine
from app.features.agents.agent_tokens import find_active_agent, find_active_agent_by_name
from app.features.runs.live_runs import find_live_run

OWNER = "owner"


@dataclass(frozen=True)
class Viewer:
    role: Literal["visitor", "agent", "owner"]
    agent_name: str = ""
    # Set when the agent came in on a run token: the run, and what its token allows.
    run_id: str = ""
    scopes: frozenset[str] | None = None

    @property
    def is_owner(self) -> bool:
        return self.role == "owner"

    @property
    def is_agent(self) -> bool:
        return self.role == "agent"

    @property
    def added_by(self) -> str:
        """What a new entry's `added_by` says: "owner" or "agent:<name>"."""
        return f"agent:{self.agent_name}" if self.is_agent else OWNER

    @property
    def is_run(self) -> bool:
        return bool(self.run_id)

    def run_allows_board(self, board: str) -> bool:
        """False only when a run token leaves this board out. Whether the agent is
        signed on to the board at all is a separate check (boards/service.py)."""
        return self.scopes is None or f"board:{board}" in self.scopes


def identify_viewer(authorization: str | None) -> Viewer:
    """Owner, then a live run's token, then an active agent's token; anything else is a visitor."""
    if is_owner(authorization):
        return Viewer(role="owner")
    supplied = (authorization or "").removeprefix("Bearer ").strip()
    if looks_like_run_token(supplied):
        return _run_viewer(supplied)
    if supplied:
        with Session(engine) as db:
            agent = find_active_agent(db, supplied)
            if agent is not None:
                return Viewer(role="agent", agent_name=agent.name)
    return Viewer(role="visitor")


def _run_viewer(token: str) -> Viewer:
    claims = read_run_token(token)
    if claims is None:
        return Viewer(role="visitor")
    with Session(engine) as db:
        if find_live_run(db, claims.run_id) is None or find_active_agent_by_name(db, claims.agent) is None:
            return Viewer(role="visitor")
    return Viewer(role="agent", agent_name=claims.agent, run_id=claims.run_id, scopes=claims.scopes)


def current_viewer(authorization: str | None = Header(default=None)) -> Viewer:
    """Route helper: the viewer behind this request."""
    return identify_viewer(authorization)


def require_writer(viewer: Viewer = Depends(current_viewer)) -> Viewer:
    """Route guard for adding or editing entries: the owner, or an agent within its hourly limit."""
    check_can_write(viewer)
    return viewer


def check_can_write(viewer: Viewer) -> None:
    """Shared by require_writer and the agent server's write tools."""
    if viewer.role == "visitor":
        raise HTTPException(status_code=401, detail="Owner or agent token required")
    if viewer.is_agent and not record_agent_write(viewer.agent_name):
        raise HTTPException(status_code=429, detail="Hourly write limit reached for this agent")
