"""
Sandbox setup: everything a fresh sandbox needs to start one run in one
harness, from its token alone: the files for the run's own folder (its
prompt, its AGENTS.md, its skills, how to reach the studio), the studio's
addresses for the harness's environment, and the command that starts the
harness there with only the run's tools. The skills are the run's
(open-studio, studio-collaborator, its task's and its agent's), read from
the agent resources, files and all.

Holds no secret: the token stays in the sandbox's OPEN_STUDIO_TOKEN. The
harness itself and its model key belong to the sandbox, never the studio.
Each harness's parts are in pi_setup.py and claude_code_setup.py;
sandbox_script.py writes a setup out as the shell script the kit's line
runs. Used by runs/service.py.
"""

import base64

from app.features.runs import claude_code_setup, pi_setup
from app.features.runs.models import Run
from app.features.runs.schemas import SandboxFile, SandboxSetup
from app.features.skills import service as skills_service

# Each harness's module gives the same names: PROGRAM, SKILLS_FOLDER, CONTEXT_FILE,
# config_files, allowed_tools and start_command.
HARNESSES = {"pi": pi_setup, "claude_code": claude_code_setup}
PROMPT_FILE = ".open-studio/prompt.md"
TOKEN_VARIABLE = "OPEN_STUDIO_TOKEN"


def build_sandbox_setup(
    run: Run,
    harness: str,
    prompt: str,
    skill_names: list[str],
    api_url: str,
    agents_md: str,
    sandbox_services: list[str],
) -> SandboxSetup:
    """The setup for this run in this harness. `sandbox_services` are the sandbox's own tools its
    add-ons allow (web, code, github). Raises skills_service.UnknownSkillsError if a skill the
    run needs isn't in the agent resources any more."""
    parts = HARNESSES[harness]
    mcp_url = f"{api_url}/mcp"
    skills = skills_service.find_skills(skill_names)
    files: dict[str, bytes] = {PROMPT_FILE: prompt.encode(), parts.CONTEXT_FILE: agents_md.encode()}
    files.update({path: text.encode() for path, text in parts.config_files(mcp_url).items()})
    for skill in skills:
        for path, content in skill.files.items():
            files[f"{parts.SKILLS_FOLDER}/{skill.name}/{path}"] = content
    return SandboxSetup(
        run_id=run.id,
        harness=harness,
        folder=f"open-studio-run-{run.id}",
        files=[SandboxFile(path=path, content_base64=base64.b64encode(content).decode()) for path, content in files.items()],
        skills=[skill.name for skill in skills],
        program=parts.PROGRAM,
        env=[TOKEN_VARIABLE],
        exports={"OPEN_STUDIO_API_URL": api_url, "OPEN_STUDIO_MCP_URL": mcp_url, "OPEN_STUDIO_RUN": run.id},
        command=parts.start_command(PROMPT_FILE, mcp_url, sandbox_services),
        allowed_tools=parts.allowed_tools(sandbox_services),
    )
