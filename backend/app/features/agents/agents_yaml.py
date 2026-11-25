"""
Agents as YAML: every agent written out as one agents.yaml file, so the
owner can see (and keep) the whole setup in one place: each agent's
description, whether it's active, its boards, outside tools, skills and
toolkits (in Composio's terms: tools, connected account, plus pinned arguments).

Export only, for visibility; the database stays the truth, and nothing reads
this file back in. Tokens are never in it (they're runs, issued one per
session). Strings and lists are written as JSON, which is also valid YAML,
so no YAML library is needed.
Used by agents/routes.py (GET /api/agents/export).
"""

import json
from datetime import datetime, timezone

from app.features.agents.schemas import AgentOut

FORMAT_VERSION = 1


def write_agents_yaml(agents: list[AgentOut]) -> str:
    lines = [
        f"# Open Studio agents, exported {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC.",
        "# For reading and keeping: the studio doesn't read this file back. No tokens are in it.",
        f"version: {FORMAT_VERSION}",
        "agents:" if agents else "agents: []",
    ]
    for agent in sorted(agents, key=lambda one: one.name):
        lines += [
            f"  - name: {agent.name}",
            f"    description: {json.dumps(agent.description, ensure_ascii=False)}",
            f"    active: {'true' if agent.active else 'false'}",
            f"    boards: {json.dumps(sorted(agent.boards))}",
            f"    tools: {json.dumps(agent.tools)}",
            f"    skills: {json.dumps(agent.skills)}",
            f"    toolkits: {json.dumps({name: grant.model_dump() for name, grant in agent.toolkits.items()})}",
        ]
    return "\n".join(lines) + "\n"
