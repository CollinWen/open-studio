"""
Toolkit API shapes: what the owner grants an agent for one toolkit (which
of its tools, the account it acts as, the arguments it may not choose),
what an agent sees of the tools its run may call, a call and its result,
and one tool of a toolkit's catalog for the owner picking tools.

Names are Composio's own, so a grant reads like a Composio session's
settings: toolkit "github", tool "GITHUB_CREATE_AN_ISSUE", connected
account "ca_...". Pinned arguments are the studio's own addition.
"""

from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel, Field, StringConstraints

ToolkitName = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9_]{0,59}$")]
ToolName = Annotated[str, StringConstraints(pattern=r"^[A-Z0-9][A-Z0-9_]{0,119}$")]
ArgumentName = Annotated[str, StringConstraints(pattern=r"^[A-Za-z_][A-Za-z0-9_]{0,59}$")]
PinnedValue = Annotated[str, StringConstraints(min_length=1, max_length=200)]


class ToolkitGrant(BaseModel):
    """What an agent may do with one toolkit."""

    # The toolkit's tools it may call: Composio's slugs, each starting with the toolkit's name.
    tools: list[ToolName] = Field(min_length=1)
    # The connected account it acts as (Composio's id, "ca_..."); empty: the studio user's own.
    connected_account: str = Field(default="", max_length=100)
    # Arguments it may not choose freely, each with its allowed values. A value ending in "*"
    # allows any that starts with the rest ("proto-*").
    pins: dict[ArgumentName, Annotated[list[PinnedValue], Field(min_length=1)]] = {}


def _tools_belong_to_their_toolkit(grants: dict[str, ToolkitGrant]) -> dict[str, ToolkitGrant]:
    for toolkit, grant in grants.items():
        strays = [tool for tool in grant.tools if not tool.startswith(f"{toolkit.upper()}_")]
        if strays:
            raise ValueError(f"Not {toolkit} tools: {', '.join(strays)}")
    return grants


# An agent's grants, by toolkit name.
ToolkitGrants = Annotated[dict[ToolkitName, ToolkitGrant], AfterValidator(_tools_belong_to_their_toolkit)]


class ToolkitTool(BaseModel):
    """One tool a run may call, as its agent sees it."""

    tool: str
    toolkit: str
    description: str
    # What it takes, as a JSON schema; empty when Composio couldn't be asked.
    input_schema: dict[str, Any]
    # Arguments the owner pinned: only these values are allowed ("x*": anything starting with x).
    pins: dict[str, list[str]]


class ToolkitCall(BaseModel):
    arguments: dict[str, Any] = {}


class ToolkitCallResult(BaseModel):
    tool: str
    # False when the tool ran but failed (error says why).
    successful: bool
    data: Any = None
    error: str | None = None


class CatalogTool(BaseModel):
    """One tool of a toolkit on Composio, for the owner picking an agent's tools."""

    tool: str
    name: str
    description: str
    # Composio's hints about it, e.g. "readOnlyHint", "destructiveHint".
    tags: list[str]
