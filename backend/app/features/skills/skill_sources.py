"""
Skill sources: reading the skills in one place AGENT_RESOURCES names, a
folder on this machine or a folder in a GitHub repository at a branch, tag
or commit ("github:owner/repo@ref/path"). Each skill is a folder holding
SKILL.md (the Agent Skills format: a frontmatter with its name and
description, then its instructions) and any files it refers to.

Used by skills/service.py, which keeps the catalog. Downloading from GitHub
is in integrations/github_archive.py.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from app.integrations.github_archive import MAX_FILE_BYTES, GithubArchiveError, read_github_folder

SKILL_FILE = "SKILL.md"
# The Agent Skills rule for names: lowercase letters, digits and single hyphens, at most 64.
SKILL_NAME = re.compile(r"^[a-z0-9](?:[a-z0-9]|-(?=[a-z0-9])){0,63}$")
GITHUB_SOURCE = re.compile(r"^github:(?P<owner>[\w.-]+)/(?P<repo>[\w.-]+)@(?P<ref>[^/\s]+)(?:/(?P<folder>.*))?$")


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    # Where it was read from, as written in AGENT_RESOURCES.
    source: str
    # Every file in the skill's folder, by its path inside that folder (SKILL.md included).
    files: dict[str, bytes]


class SkillSourceError(Exception):
    """A source couldn't be read."""


def read_source(source: str) -> list[Skill]:
    """The skills in one source, by folder name order."""
    if source.startswith("github:"):
        match = GITHUB_SOURCE.match(source)
        if not match:
            raise SkillSourceError(f'"{source}" should read github:owner/repo@ref/path')
        try:
            files = read_github_folder(match["owner"], match["repo"], match["ref"], match["folder"] or "")
        except GithubArchiveError as error:
            raise SkillSourceError(str(error)) from error
    else:
        files = _read_folder(Path(source))
    return skills_in_files(files, source)


def skills_in_files(files: dict[str, bytes], source: str) -> list[Skill]:
    """Group a folder's files into skills: each folder directly inside it that holds a SKILL.md
    with a valid name and a description. Others are skipped, as Pi and Claude Code skip them."""
    by_folder: dict[str, dict[str, bytes]] = {}
    for path, content in files.items():
        folder, _, inside = path.partition("/")
        if inside:
            by_folder.setdefault(folder, {})[inside] = content
    skills = []
    for folder, skill_files in sorted(by_folder.items()):
        if SKILL_FILE not in skill_files:
            continue
        name, description = read_frontmatter(skill_files[SKILL_FILE].decode("utf-8", "replace"))
        name = name or folder
        if SKILL_NAME.match(name) and description:
            skills.append(Skill(name=name, description=description, source=source, files=skill_files))
    return skills


def read_frontmatter(text: str) -> tuple[str, str]:
    """The name and description in a SKILL.md's frontmatter (one "key: value" a line)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return "", ""
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, separator, value = line.partition(":")
        if separator and not key.startswith((" ", "\t")):
            fields[key.strip()] = value.strip().strip("'\"")
    return fields.get("name", ""), fields.get("description", "")


def _read_folder(folder: Path) -> dict[str, bytes]:
    if not folder.is_dir():
        raise SkillSourceError(f"No folder {folder}")
    files: dict[str, bytes] = {}
    for path in sorted(folder.rglob("*")):
        relative = path.relative_to(folder)
        hidden = any(part.startswith(".") or part == "__pycache__" for part in relative.parts)
        if path.is_file() and not path.is_symlink() and not hidden and path.stat().st_size <= MAX_FILE_BYTES:
            files[relative.as_posix()] = path.read_bytes()
    return files
