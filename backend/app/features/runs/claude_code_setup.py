"""
Claude Code setup: how a run starts in Claude Code inside the run's folder:
its skills in .claude/skills/ (where Claude Code finds a project's skills),
the studio's MCP server given on the command line and no other server, with
the token read from OPEN_STUDIO_TOKEN only when it starts, then one
headless pass (-p) that may use only the run's tools.

Claude Code's own sign-in or API key stays where the sandbox keeps it. What
"github" can reach is decided by the GitHub credentials the sandbox holds,
since "code" gives a shell that can run git and gh too.
Used by sandbox_setup.py; pi_setup.py is the same for Pi.
"""

import json
import shlex

PROGRAM = "claude"
SKILLS_FOLDER = ".claude/skills"
MCP_SERVER_NAME = "open-studio"
# Reading the run's own folder and loading its skills, and the studio's tools.
TOOLS_ALWAYS = (f"mcp__{MCP_SERVER_NAME}", "Skill", "Read", "Glob", "Grep")
# The Claude Code tools (permission rules) that give a run each outside tool.
TOOLS_FOR_OUTSIDE_TOOL: dict[str, tuple[str, ...]] = {
    "web": ("WebSearch", "WebFetch"),
    "code": ("Bash", "Edit", "Write"),
    "github": ("Bash(gh repo create:*)", "Bash(git:*)"),
}
_TOKEN_PLACE = "TOKEN_GOES_HERE"


def config_files(mcp_url: str) -> dict[str, str]:
    """Nothing besides the skills: the MCP server is given on the command line."""
    return {}


def allowed_tools(outside_tools: list[str]) -> list[str]:
    tools = list(TOOLS_ALWAYS)
    for outside_tool in outside_tools:
        tools += [tool for tool in TOOLS_FOR_OUTSIDE_TOOL[outside_tool] if tool not in tools]
    return tools


def start_command(prompt_file: str, mcp_url: str, outside_tools: list[str]) -> str:
    """The shell commands that run the task in Claude Code, from inside the run's folder.
    printf puts the token into the MCP config as it starts, so it's never written to a file."""
    server = {"type": "http", "url": mcp_url, "headers": {"Authorization": f"Bearer {_TOKEN_PLACE}"}}
    template = json.dumps({"mcpServers": {MCP_SERVER_NAME: server}}).replace("%", "%%").replace(_TOKEN_PLACE, "%s")
    tools = " ".join(shlex.quote(tool) for tool in allowed_tools(outside_tools))
    return "\n".join([
        f'mcp_config=$(printf {shlex.quote(template)} "$OPEN_STUDIO_TOKEN")',
        f'exec claude -p "$(cat {shlex.quote(prompt_file)})" --mcp-config "$mcp_config" --strict-mcp-config --allowedTools {tools}',
    ])
