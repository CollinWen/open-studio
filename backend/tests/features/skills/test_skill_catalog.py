"""
Tests for the skill catalog: this repository's skills are read with their
descriptions and files; a skill folder needs a SKILL.md with a valid name
and a description; a GitHub source is read from the repository's archive
(here a made-up one, never the network), the first source wins a name, a
source that can't be read keeps the last good catalog and with none says
the catalog is unavailable; and only the owner lists the catalog.
"""

import io
import tarfile
from dataclasses import replace

import pytest

from conftest import OWNER_HEADERS, SCOUT_HEADERS

from app.config import REPO_SKILLS_DIR, settings
from app.features.skills import service
from app.features.skills import skill_sources
from app.integrations.github_archive import files_in_archive

SKILL = b"---\nname: {name}\ndescription: {description}\n---\n\n# Instructions\n"


def _archive(files: dict[str, bytes]) -> bytes:
    """A tarball shaped like GitHub's: everything under one top folder."""
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        for path, content in files.items():
            info = tarfile.TarInfo(f"repo-main/{path}")
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))
    return buffer.getvalue()


@pytest.fixture
def sources(monkeypatch):
    """Point AGENT_RESOURCES at the given sources for one test, reading them afresh."""

    def use(*names: str):
        monkeypatch.setattr(service, "settings", replace(settings, agent_resources=names))
        service.forget_catalog()

    yield use
    service.forget_catalog()


def test_the_repositorys_skills_are_in_the_catalog():
    skills = {skill.name: skill for skill in service.list_skills()}
    assert {"open-studio", "studio-collaborator", "gathering-sources", "studio-writeup"} <= set(skills)
    assert skills["open-studio"].description.startswith("Read and add to an Open Studio")
    writeup = service.find_skills(["studio-writeup"])[0]
    assert {"SKILL.md", "example.html"} <= set(writeup.files)


def test_a_skill_needs_a_skill_file_a_valid_name_and_a_description():
    files = {
        "good/SKILL.md": SKILL.replace(b"{name}", b"good").replace(b"{description}", b"Does good things."),
        "no-description/SKILL.md": b"---\nname: no-description\n---\n",
        "Bad Name/SKILL.md": SKILL.replace(b"{name}", b"Bad Name").replace(b"{description}", b"x"),
        "loose/notes.md": b"no SKILL.md here",
        "README.md": b"top-level files aren't skills",
    }
    skills = skill_sources.skills_in_files(files, "test")
    assert [skill.name for skill in skills] == ["good"]


def test_a_github_source_is_read_from_its_archive(sources, monkeypatch):
    archive = _archive({
        "skills/exa-search/SKILL.md": SKILL.replace(b"{name}", b"exa-search").replace(b"{description}", b"Search with Exa."),
        "skills/exa-search/scripts/search.sh": b"echo hi",
        "other/ignored/SKILL.md": b"---\nname: ignored\ndescription: outside the folder\n---\n",
    })
    asked = []

    def read_github_folder(owner, repo, ref, folder):
        asked.append((owner, repo, ref, folder))
        return files_in_archive(archive, folder)

    monkeypatch.setattr(skill_sources, "read_github_folder", read_github_folder)
    sources("github:someone/agent-resources@main/skills")
    skills = service.list_skills()
    assert asked == [("someone", "agent-resources", "main", "skills")]
    assert [(skill.name, skill.source) for skill in skills] == [("exa-search", "github:someone/agent-resources@main/skills")]
    assert set(service.find_skills(["exa-search"])[0].files) == {"SKILL.md", "scripts/search.sh"}


def test_the_first_source_wins_a_name(sources, tmp_path):
    for folder, description in (("first", "From the first."), ("second", "From the second.")):
        skill = tmp_path / folder / "shared"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_bytes(SKILL.replace(b"{name}", b"shared").replace(b"{description}", description.encode()))
    sources(str(tmp_path / "first"), str(tmp_path / "second"))
    assert [skill.description for skill in service.list_skills()] == ["From the first."]


def test_an_unreadable_source_keeps_the_last_catalog_or_says_so(sources, monkeypatch):
    sources("/no/such/folder")
    with pytest.raises(service.SkillsUnavailableError):
        service.list_skills()

    sources(str(REPO_SKILLS_DIR))
    names = [skill.name for skill in service.list_skills()]
    # The source breaks once the catalog is due to be read again: the last good one is kept.
    monkeypatch.setattr(service, "settings", replace(settings, agent_resources=("/no/such/folder",)))
    monkeypatch.setattr(service, "_read_again_at", 0.0)
    assert [skill.name for skill in service.list_skills()] == names


def test_unknown_names_are_named():
    with pytest.raises(service.UnknownSkillsError) as error:
        service.check_skill_names(["gathering-sources", "no-such-skill"])
    assert error.value.names == ["no-such-skill"]


def test_only_the_owner_lists_the_catalog(client):
    assert client.get("/api/skills").status_code == 401
    assert client.get("/api/skills", headers=SCOUT_HEADERS).status_code == 401
    listed = client.get("/api/skills", headers=OWNER_HEADERS)
    assert listed.status_code == 200
    building = next(skill for skill in listed.json() if skill["name"] == "building")
    assert building["description"] and building["source"] == str(REPO_SKILLS_DIR)
