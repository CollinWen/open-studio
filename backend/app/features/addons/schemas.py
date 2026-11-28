"""
Add-on API shapes: what the owner sends to define or change an add-on, what
comes back, connecting one to its account, a toolkit's tools for the owner
to look through, and what an agent sees of its add-ons' tools and a call.

A Composio add-on's service is Composio's own toolkit slug ("gmail") and its
tools are Composio's tool slugs ("GMAIL_CREATE_EMAIL_DRAFT").
"""

import re
from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, StringConstraints, model_validator

# Lowercase letters, digits and dashes, like an agent's name.
AddonName = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9-]{0,39}$")]
# The sandbox's own tools an add-on of kind "sandbox" can stand for.
SANDBOX_SERVICES = ("web", "code", "github")
TOOLKIT_SLUG = r"^[a-z0-9][a-z0-9_]{0,59}$"
GUIDE_MAX_LENGTH = 20_000

AddonKind = Literal["sandbox", "composio"]


class AddonCreate(BaseModel):
    name: AddonName
    kind: AddonKind
    # "web", "code" or "github" for a sandbox add-on; a Composio toolkit slug otherwise.
    service: str
    # Left out: a guide written from its kind's template, to edit later.
    guide: str | None = Field(default=None, max_length=GUIDE_MAX_LENGTH)

    @model_validator(mode="after")
    def _service_fits_kind(self) -> "AddonCreate":
        if self.kind == "sandbox" and self.service not in SANDBOX_SERVICES:
            raise ValueError(f"A sandbox add-on's service is one of: {', '.join(SANDBOX_SERVICES)}")
        if self.kind == "composio" and not re.match(TOOLKIT_SLUG, self.service):
            raise ValueError("A Composio add-on's service is a toolkit slug, e.g. gmail")
        return self


class AddonUpdate(BaseModel):
    """Only the guide changes here. Its kind and service stay (agents know it by them);
    its account changes by connecting it again."""

    guide: str = Field(max_length=GUIDE_MAX_LENGTH)


class AddonOut(BaseModel):
    name: str
    kind: str
    service: str
    account: str
    guide: str
    created_at: datetime
    # Built in (web, code, github): can't be removed.
    built_in: bool


class ConnectRequest(BaseModel):
    # The studio page to come back to after signing in on Composio's page.
    return_url: str = Field(max_length=500)


class ConnectLink(BaseModel):
    # Composio's own sign-in page for this toolkit.
    url: str


class ConnectionSave(BaseModel):
    connected_account_id: str = Field(min_length=1, max_length=100)


class CatalogTool(BaseModel):
    """One tool of a Composio toolkit, for the owner looking through an add-on."""

    tool: str
    name: str
    description: str
    # Composio's hint of what it does: readOnlyHint, createHint, updateHint, destructiveHint.
    tags: list[str]


class AddonTool(BaseModel):
    """One tool a run may call, as its agent sees it."""

    tool: str
    addon: str
    description: str
    # What it takes, as a JSON schema.
    input_schema: dict[str, Any]


class AddonCall(BaseModel):
    arguments: dict[str, Any] = {}


class AddonCallResult(BaseModel):
    tool: str
    # False when the tool ran but failed (error says why).
    successful: bool
    data: Any = None
    error: str | None = None
