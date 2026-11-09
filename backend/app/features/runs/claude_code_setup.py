"""
Claude Code setup: one optional way to run a kit, as a single `claude`
command that connects to the studio's MCP server with the run token, gives
the prompt, and allows only the tools the run was granted.

Nothing else in the studio depends on Claude Code. A kit's neutral parts
(token, MCP and API addresses, prompt, scopes) work with any harness; another
harness gets its own setup file like this one, added in run_kit.py.
"""

import json
import shlex

from app.features.runs.schemas import HarnessSetup

MCP_SERVER_NAME = "open-studio"

# The Claude Code tools (permission rules) that give an agent each outside tool.
TOOLS_FOR_OUTSIDE_TOOL: dict[str, tuple[str, ...]] = {
    "web": ("WebSearch", "WebFetch"),
    "code": ("Bash", "Edit", "Write"),
    "github": ("Bash(gh repo create:*)", "Bash(git:*)"),
}


def build_claude_code_setup(prompt: str, mcp_url: str, token: str, outside_tools: list[str]) -> HarnessSetup:
    allowed_tools = [f"mcp__{MCP_SERVER_NAME}"]
    for tool in outside_tools:
        allowed_tools.extend(TOOLS_FOR_OUTSIDE_TOOL[tool])
    mcp_config = {
        "mcpServers": {
            MCP_SERVER_NAME: {"type": "http", "url": mcp_url, "headers": {"Authorization": f"Bearer {token}"}}
        }
    }
    parts = ["claude", "-p", prompt, "--mcp-config", json.dumps(mcp_config), "--allowedTools", *allowed_tools]
    return HarnessSetup(command=" ".join(shlex.quote(part) for part in parts), allowed_tools=allowed_tools)
