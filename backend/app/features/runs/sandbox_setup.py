"""
Sandbox setup: everything a fresh sandbox needs to start one run in one
harness: the files for the run's own folder (its prompt, its skills, how to
reach the studio) and the command that starts the harness there. The
skills are the run's (open-studio, studio-collaborator, its task's and its
agent's), read from the agent resources, files and all.

Holds no secret: the token stays in the sandbox's OPEN_STUDIO_TOKEN. The
harness itself and its model key belong to the sandbox, never the studio.
Each harness's parts are in pi_setup.py and claude_code_setup.py;
sandbox_script.py writes a setup out as the shell script the kit's line runs.
Used by runs/service.py.
"""

import base64

from app.features.runs import claude_code_setup, pi_setup
from app.features.runs.models import Run
from app.features.runs.schemas import SandboxFile, SandboxSetup
from app.features.skills import service as skills_service

# Each harness's module gives the same names: PROGRAM, SKILLS_FOLDER,
# config_files, allowed_tools and start_command.
HARNESSES = {"pi": pi_setup, "claude_code": claude_code_setup}
PROMPT_FILE = ".open-studio/prompt.md"
TOKEN_VARIABLE = "OPEN_STUDIO_TOKEN"


def build_sandbox_setup(run: Run, harness: str, prompt: str, skill_names: list[str], mcp_url: str) -> SandboxSetup:
    """The setup for this run in this harness. Raises skills_service.UnknownSkillsError if a skill
    the run needs isn't in the agent resources any more."""
    parts = HARNESSES[harness]
    skills = skills_service.find_skills(skill_names)
    files: dict[str, bytes] = {PROMPT_FILE: prompt.encode()}
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
        command=parts.start_command(PROMPT_FILE, mcp_url, run.tools),
        allowed_tools=parts.allowed_tools(run.tools),
    )
