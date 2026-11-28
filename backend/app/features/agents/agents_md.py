"""
AGENTS.md: what an agent has, written for the agent itself, so it knows
before it starts what it can use, where it is and how. One section per
add-on (where it comes from, its guide, then the owner's instructions for
this agent), then its skills, its boards and how to reach the studio.
Pi reads AGENTS.md on its own when it starts; Claude Code gets the same
text as CLAUDE.md.

Each run's sandbox gets it, narrowed to that run's boards and add-ons
(runs/sandbox_setup.py); the agent window shows the same text as a preview.
"""

from app.features.addons.schemas import AddonOut
from app.features.runs.schemas import ALL_BOARDS


def write_agents_md(
    agent: str,
    description: str,
    boards: list[str],
    addons: list[AddonOut],
    instructions: dict[str, str],
    skills: list[str],
) -> str:
    sections = [
        f"# What you have, {agent}",
        description.strip() or "An agent working for an Open Studio.",
        "This lists everything you can use on this run. You have nothing else: if you need more, "
        "write a question in the agent log and carry on with what you have.",
        "## Add-ons",
        *(_addon_section(addon, instructions.get(addon.name, "")) for addon in addons),
        *([] if addons else ["None on this run."]),
        "## Skills",
        f"{', '.join(skills)}. Your harness lists them; load one when its kind of work comes up.",
        "## Boards",
        _boards_line(boards),
        "## The studio",
        "- Its tools are already connected (the MCP server \"open-studio\"). Add-on tools that run "
        "through the studio: `list_addon_tools`, then `call_addon_tool`.\n"
        "- Without MCP: `$OPEN_STUDIO_API_URL/api`, with `Authorization: Bearer $OPEN_STUDIO_TOKEN`.\n"
        "- Your run is `$OPEN_STUDIO_RUN`: `get_my_run` shows its task, the owner's note and when it ends.",
    ]
    return "\n\n".join(sections) + "\n"


def _addon_section(addon: AddonOut, instructions: str) -> str:
    parts = [f"### {addon.name}", _where_it_comes_from(addon), addon.guide.strip()]
    if instructions.strip():
        parts.append(f"**The owner's instructions for you:**\n\n{instructions.strip()}")
    return "\n\n".join(part for part in parts if part)


def _where_it_comes_from(addon: AddonOut) -> str:
    if addon.kind == "sandbox":
        return f"*Your sandbox's own {addon.service} tools.*"
    if addon.account:
        return f"*{addon.service}, through the studio (Composio), as the account the owner connected.*"
    return f"*{addon.service}, through the studio (Composio). Not connected yet: its tools won't work until the owner connects it.*"


def _boards_line(boards: list[str]) -> str:
    if boards == [ALL_BOARDS]:
        return "Every board you're signed on to (`list_boards` shows them). Read each one's brief first."
    if not boards:
        return "None: you can read the studio, but not add to it."
    return f"You may add to and log on: {', '.join(boards)}. Read each one's brief first."
