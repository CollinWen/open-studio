"""
Viewer: who is making a request (a visitor, an agent or the owner) and what
name their writes are recorded under.

Agents are other programs the owner has given a token to (AGENT_TOKENS in
backend/.env): a Claude session, a research bot. They can read the studio and
add entries, which arrive unlisted for the owner to publish.
Used by every route that reads or writes entries, and by agent_server/.
What each kind of viewer may see or edit lives in entries/visibility_rules.py.
"""

import secrets
from dataclasses import dataclass
from typing import Literal

from fastapi import Depends, Header, HTTPException

from app.auth.agent_write_limit import record_agent_write
from app.auth.owner_auth import is_owner
from app.config import settings

OWNER = "owner"


@dataclass(frozen=True)
class Viewer:
    role: Literal["visitor", "agent", "owner"]
    agent_name: str = ""

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


def identify_viewer(authorization: str | None) -> Viewer:
    """Owner token, then agent tokens; anything else is a visitor."""
    if is_owner(authorization):
        return Viewer(role="owner")
    supplied = (authorization or "").removeprefix("Bearer ").strip()
    if supplied:
        for token, name in settings.agent_tokens.items():
            if secrets.compare_digest(supplied, token):
                return Viewer(role="agent", agent_name=name)
    return Viewer(role="visitor")


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
