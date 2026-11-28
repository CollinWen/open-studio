"""
Skill catalog: every skill the studio can give an agent, read from the
sources in AGENT_RESOURCES (the first source wins when two hold a skill of
the same name) and kept for AGENT_RESOURCES_CACHE_MINUTES, so GitHub isn't
asked on every call. If a source can't be read, the last good catalog is
kept; with none, the catalog is unavailable rather than quietly empty.

Used by skills/routes.py (the list the agent window picks from),
agents/service.py (checking an agent's picks) and runs/sandbox_setup.py
(writing a run's skills into its sandbox). Reading one source is in
skill_sources.py.
"""

import threading
import time

from app.config import settings
from app.features.skills.schemas import SkillOut
from app.features.skills.skill_sources import Skill, SkillSourceError, read_source

# After a failed read, try again this soon rather than waiting out the whole cache time.
RETRY_SECONDS = 60

_lock = threading.Lock()
_catalog: dict[str, Skill] | None = None
_read_again_at = 0.0


class SkillsUnavailableError(Exception):
    """No source could be read, and there's no earlier catalog to fall back on."""


class UnknownSkillsError(Exception):
    """Some names aren't skills in the agent resources."""

    def __init__(self, names: list[str]):
        self.names = names
        super().__init__(f"Not in the agent resources: {', '.join(names)}")


def list_skills() -> list[SkillOut]:
    """Every skill, by name."""
    return [
        SkillOut(name=skill.name, description=skill.description, source=skill.source)
        for skill in sorted(_read_catalog().values(), key=lambda skill: skill.name)
    ]


def check_skill_names(names: list[str]) -> None:
    """Raise UnknownSkillsError naming any that aren't in the catalog."""
    catalog = _read_catalog()
    unknown = [name for name in dict.fromkeys(names) if name not in catalog]
    if unknown:
        raise UnknownSkillsError(unknown)


def find_skills(names: list[str]) -> list[Skill]:
    """These skills, files and all, in the order asked; every one must be in the catalog."""
    check_skill_names(names)
    catalog = _read_catalog()
    return [catalog[name] for name in dict.fromkeys(names)]


def forget_catalog() -> None:
    """Read the sources again on the next call (tests, or after AGENT_RESOURCES changes)."""
    global _catalog, _read_again_at
    with _lock:
        _catalog, _read_again_at = None, 0.0


def _read_catalog() -> dict[str, Skill]:
    global _catalog, _read_again_at
    with _lock:
        if _catalog is not None and time.monotonic() < _read_again_at:
            return _catalog
        skills: dict[str, Skill] = {}
        problems: list[str] = []
        for source in settings.agent_resources:
            try:
                for skill in read_source(source):
                    skills.setdefault(skill.name, skill)
            except SkillSourceError as error:
                problems.append(str(error))
        if problems and _catalog is not None:
            _read_again_at = time.monotonic() + RETRY_SECONDS
            return _catalog
        if problems:
            raise SkillsUnavailableError("Can't read the agent resources: " + "; ".join(problems))
        _catalog = skills
        _read_again_at = time.monotonic() + settings.agent_resources_cache_minutes * 60
        return _catalog
