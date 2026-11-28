"""
Pi setup: how a run starts in Pi (the pi coding agent, npm
@earendil-works/pi-coding-agent 1.6 or later) inside the run's folder: its
AGENTS.md at the top (Pi reads it on its own), its skills in .pi/skills/,
the studio's MCP server in .pi/mcp.json (its tools declared to the model
directly, the token read from OPEN_STUDIO_TOKEN only when Pi starts), then
one pass in print mode that may use only the run's tools: read, grep, find
and ls always, bash, edit and write with the code add-on, and the studio's
own tools.

Pi's settings, model and model key (OPENROUTER_API_KEY, say) stay where the
sandbox keeps them, in ~/.pi/agent and its environment: they belong to the
harness, not to the run. Pi only reads a folder's .pi/ when it's trusted,
hence --approve. Pi has no web tool of its own, so the web add-on reaches
the web through bash (with the code add-on), or a Composio add-on searches.
Used by sandbox_setup.py; claude_code_setup.py is the same for Claude Code.
"""

import json
import shlex

PROGRAM = "pi"
SKILLS_FOLDER = ".pi/skills"
# Pi reads this from the folder it starts in, as context.
CONTEXT_FILE = "AGENTS.md"
MCP_SERVER_NAME = "open-studio"
# Pi names a server's tools mcp__<server>__<tool>, with "-" written as "_".
STUDIO_TOOLS = "mcp__open_studio__*"
TOOLS_ALWAYS = ("read", "grep", "find", "ls")
# The Pi tools that give a run each of the sandbox's own add-ons.
TOOLS_FOR_SERVICE: dict[str, tuple[str, ...]] = {
    "web": (),
    "code": ("bash", "edit", "write"),
    "github": (),
}


def config_files(mcp_url: str) -> dict[str, str]:
    """The files Pi reads from the run's folder, besides the skills."""
    server = {
        "url": mcp_url,
        "headers": {"Authorization": "Bearer ${OPEN_STUDIO_TOKEN}"},
        "exposure": "direct",
        "description": "Open Studio: the boards, entries, log and run you work on",
    }
    return {".pi/mcp.json": json.dumps({"mcpServers": {MCP_SERVER_NAME: server}}, indent=2) + "\n"}


def allowed_tools(services: list[str]) -> list[str]:
    """Pi's tools for a run whose add-ons allow these of the sandbox's own (web, code, github)."""
    tools = list(TOOLS_ALWAYS)
    for service in services:
        tools += [tool for tool in TOOLS_FOR_SERVICE[service] if tool not in tools]
    return [*tools, STUDIO_TOOLS]


def start_command(prompt_file: str, mcp_url: str, services: list[str]) -> str:
    """The shell command that runs the task in Pi, from inside the run's folder."""
    tools = ",".join(allowed_tools(services))
    return f'exec pi --approve --print --tools {shlex.quote(tools)} "$(cat {shlex.quote(prompt_file)})"'
