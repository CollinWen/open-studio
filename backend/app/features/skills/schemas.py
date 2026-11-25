"""
Skill API shapes: one skill in the catalog, as the owner sees it when
picking an agent's skills. The files themselves only go to a run's sandbox
(runs/sandbox_setup.py).
"""

from pydantic import BaseModel


class SkillOut(BaseModel):
    # Its name in the Agent Skills format, e.g. "gathering-sources".
    name: str
    # What it's for and when to use it, from its SKILL.md.
    description: str
    # Where it was read from, as written in AGENT_RESOURCES.
    source: str
