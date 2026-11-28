"""
Tests for a run's sandbox setup: the owner and the run's own agent get it,
and a run's token alone gets its own through /current (another run's token,
a visitor or a finished run don't, each with a reason); for Pi it holds the
prompt, an AGENTS.md with each add-on's guide and the owner's instructions,
the run's skills with all their files, and an MCP config that reads the
token from the environment, with only the tools its add-ons allow; for
Claude Code the same text is CLAUDE.md and the skills go where Claude Code
finds them; no token is ever written into it; a skill gone from the agent
resources is refused by name; and the script, run with sh in an empty
folder, writes everything into the run's folder, sets the studio's
addresses and starts the harness there (a stand-in pi that records what it
was given), or stops with a reason.
"""

import base64
import os
import subprocess
import uuid
from pathlib import Path

from conftest import AGENT_BOARD, OWNER_HEADERS, SCOUT_HEADERS

from app.features.skills import service as skills_service


def _agent_with_run(client, addons=(), skills=(), kind="open", instructions=None) -> tuple[str, dict]:
    name = f"s-{uuid.uuid4().hex[:8]}"
    body = {"name": name, "boards": [AGENT_BOARD], "addons": list(addons), "skills": list(skills),
            "addon_instructions": instructions or {}, "description": "Finds sources for the research board"}
    assert client.post("/api/agents", json=body, headers=OWNER_HEADERS).status_code == 200
    run = {"agent": name, "boards": [AGENT_BOARD], "kind": kind, "brief": "a note from the owner"}
    kit = client.post("/api/runs", json=run, headers=OWNER_HEADERS).json()
    return name, kit


def _bearer(kit: dict) -> dict:
    return {"Authorization": f"Bearer {kit['token']}"}


def _files(setup: dict) -> dict[str, bytes]:
    return {file["path"]: base64.b64decode(file["content_base64"]) for file in setup["files"]}


def test_the_owner_and_the_runs_agent_get_the_setup_and_no_one_else(client):
    _, kit = _agent_with_run(client)
    url = f"/api/runs/{kit['run']['id']}/sandbox"
    assert client.get(url, headers=OWNER_HEADERS).status_code == 200
    assert client.get(url, headers=_bearer(kit)).status_code == 200
    current = client.get("/api/runs/current/sandbox", headers=_bearer(kit))
    assert current.status_code == 200 and current.json()["run_id"] == kit["run"]["id"]
    assert client.get("/api/runs/current/sandbox", headers=OWNER_HEADERS).status_code == 400
    assert client.get(url, headers=SCOUT_HEADERS).status_code == 404
    visitor = client.get(url)
    assert visitor.status_code == 401 and "OPEN_STUDIO_TOKEN" in visitor.json()["detail"]

    client.post(f"/api/runs/{kit['run']['id']}/finish", json={"summary": "done"}, headers=OWNER_HEADERS)
    finished = client.get(url, headers=OWNER_HEADERS)
    assert finished.status_code == 409 and "finished" in finished.json()["detail"]


def test_a_pi_setup_holds_the_prompt_the_skills_and_the_studio(client):
    instructions = {"web": "Prefer primary sources; quote the passage you rely on."}
    _, kit = _agent_with_run(client, skills=["studio-writeup"], kind="study", addons=["web"], instructions=instructions)
    setup = client.get(f"/api/runs/{kit['run']['id']}/sandbox", headers=_bearer(kit)).json()
    files = _files(setup)
    assert setup["folder"] == f"open-studio-run-{kit['run']['id']}"
    assert setup["skills"] == ["open-studio", "studio-collaborator", "studying-sources", "gathering-sources", "studio-writeup"]
    assert files[".open-studio/prompt.md"].decode() == kit["prompt"]
    agents_md = files["AGENTS.md"].decode()
    assert agents_md.startswith(f"# What you have, {kit['run']['agent']}\n\nFinds sources for the research board")
    assert "### web" in agents_md and "**What it is:** the web" in agents_md
    assert "Prefer primary sources; quote the passage you rely on." in agents_md
    assert f"You may add to and log on: {AGENT_BOARD}." in agents_md
    assert setup["exports"] == {"OPEN_STUDIO_API_URL": kit["api_url"], "OPEN_STUDIO_MCP_URL": kit["mcp_url"],
                                "OPEN_STUDIO_RUN": kit["run"]["id"]}
    assert ".pi/skills/studio-writeup/example.html" in files
    assert files[".pi/skills/open-studio/SKILL.md"].startswith(b"---\nname: open-studio\n")
    mcp = files[".pi/mcp.json"].decode()
    assert f'"url": "{kit["mcp_url"]}"' in mcp
    assert '"Bearer ${OPEN_STUDIO_TOKEN}"' in mcp and '"exposure": "direct"' in mcp
    # No code add-on: Pi may read, but not run commands or write.
    assert setup["allowed_tools"] == ["read", "grep", "find", "ls", "mcp__open_studio__*"]
    assert setup["program"] == "pi" and setup["env"] == ["OPEN_STUDIO_TOKEN"]
    assert kit["token"] not in str(setup)


def test_code_gives_pi_a_shell_and_claude_code_gets_its_own_folders(client):
    _, kit = _agent_with_run(client, addons=["web", "code"])
    run_id = kit["run"]["id"]
    pi = client.get(f"/api/runs/{run_id}/sandbox?harness=pi", headers=_bearer(kit)).json()
    assert {"bash", "edit", "write"} <= set(pi["allowed_tools"])

    claude = client.get(f"/api/runs/{run_id}/sandbox?harness=claude_code", headers=_bearer(kit)).json()
    files = _files(claude)
    assert ".claude/skills/open-studio/SKILL.md" in files and ".pi/mcp.json" not in files
    assert "### code" in files["CLAUDE.md"].decode() and "AGENTS.md" not in files
    assert {"WebFetch", "Bash", "mcp__open-studio", "Skill"} <= set(claude["allowed_tools"])
    assert "--strict-mcp-config" in claude["command"] and '"$OPEN_STUDIO_TOKEN"' in claude["command"]
    assert kit["token"] not in str(claude)


def test_a_skill_gone_from_the_agent_resources_is_refused_by_name(client, monkeypatch):
    _, kit = _agent_with_run(client, skills=["brainstorming"])
    real_find = skills_service.find_skills

    def find_without_brainstorming(names):
        if "brainstorming" in names:
            raise skills_service.UnknownSkillsError(["brainstorming"])
        return real_find(names)

    monkeypatch.setattr(skills_service, "find_skills", find_without_brainstorming)
    refused = client.get(f"/api/runs/{kit['run']['id']}/sandbox", headers=_bearer(kit))
    assert refused.status_code == 409 and "brainstorming" in refused.json()["detail"]
    script = client.get(f"/api/runs/{kit['run']['id']}/sandbox.sh", headers=_bearer(kit))
    assert script.status_code == 409 and "brainstorming" in script.text and "exit 1" in script.text


def _stand_in(folder: Path, program: str) -> None:
    """A fake harness that writes down how it was started, in the folder it was started in."""
    folder.mkdir(exist_ok=True)
    path = folder / program
    path.write_text(
        "#!/bin/sh\n"
        "printf '%s\\n' \"$@\" > started-with.txt\n"
        "printf '%s' \"$OPEN_STUDIO_TOKEN\" > token-seen.txt\n"
        "printf '%s %s %s' \"$OPEN_STUDIO_API_URL\" \"$OPEN_STUDIO_MCP_URL\" \"$OPEN_STUDIO_RUN\" > studio-seen.txt\n"
    )
    path.chmod(0o755)


def _run_script(script: str, folder: Path, env: dict) -> subprocess.CompletedProcess:
    (folder / "setup.sh").write_text(script)
    return subprocess.run(["sh", "setup.sh"], cwd=folder, env=env, capture_output=True, text=True, timeout=30)


def test_the_script_sets_up_the_folder_and_starts_pi_there(client, tmp_path):
    _, kit = _agent_with_run(client, skills=["studio-writeup"])
    script = client.get("/api/runs/current/sandbox.sh", headers=_bearer(kit))
    assert script.status_code == 200 and script.text.startswith("#!/bin/sh")
    assert kit["token"] not in script.text
    _stand_in(tmp_path / "bin", "pi")
    env = {"PATH": f"{tmp_path / 'bin'}:{os.environ['PATH']}", "OPEN_STUDIO_TOKEN": kit["token"]}

    done = _run_script(script.text, tmp_path, env)
    assert done.returncode == 0, done.stderr
    folder = tmp_path / f"open-studio-run-{kit['run']['id']}"
    assert (folder / ".pi/skills/studio-writeup/example.html").exists()
    assert (folder / ".open-studio/prompt.md").read_text() == kit["prompt"]
    started_with = (folder / "started-with.txt").read_text()
    assert started_with.startswith("--approve\n--print\n--tools\nread,grep,find,ls,mcp__open_studio__*\n")
    assert kit["prompt"] in started_with
    assert (folder / "token-seen.txt").read_text() == kit["token"]
    assert (folder / "studio-seen.txt").read_text() == f"{kit['api_url']} {kit['mcp_url']} {kit['run']['id']}"
    assert (folder / "AGENTS.md").read_text().startswith("# What you have")
    assert sorted(path.name for path in tmp_path.iterdir()) == ["bin", folder.name, "setup.sh"]


def test_the_script_stops_with_a_reason_when_something_is_missing(client, tmp_path):
    _, kit = _agent_with_run(client)
    script = client.get(f"/api/runs/{kit['run']['id']}/sandbox.sh", headers=_bearer(kit)).text
    no_token = _run_script(script, tmp_path, {"PATH": os.environ["PATH"]})
    assert no_token.returncode != 0 and "set OPEN_STUDIO_TOKEN first" in no_token.stderr

    no_pi = _run_script(script, tmp_path, {"PATH": "/usr/bin:/bin", "OPEN_STUDIO_TOKEN": kit["token"]})
    assert no_pi.returncode != 0 and "pi is not installed here" in no_pi.stderr

    refused = client.get(f"/api/runs/{kit['run']['id']}/sandbox.sh")
    assert refused.status_code == 401
    stopped = _run_script(refused.text, tmp_path, {"PATH": os.environ["PATH"]})
    assert stopped.returncode == 1 and "OPEN_STUDIO_TOKEN" in stopped.stderr
