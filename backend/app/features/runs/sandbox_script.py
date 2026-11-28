"""
Sandbox script: a sandbox setup written out as one POSIX shell script, the
one the kit's line pipes into sh. It checks the sandbox has the run's token
and the harness's program, makes the run's folder where it is run, writes
every file into it (base64, so no file's content is ever read as shell),
sets the studio's addresses for the harness, and starts it there. Nothing
outside that folder is touched, so it is safe on a laptop too. A refusal
is a script as well, one that says why and stops.

Used by runs/routes.py (GET /api/runs/current/sandbox.sh and /{id}/sandbox.sh).
"""

import shlex

from app.features.runs.schemas import SandboxSetup

HARNESS_TITLES = {"pi": "Pi", "claude_code": "Claude Code"}
ENV_HINTS = {"OPEN_STUDIO_TOKEN": "the run's token, from its kit"}


def write_sandbox_script(setup: SandboxSetup) -> str:
    title = HARNESS_TITLES[setup.harness]
    folder = shlex.quote(setup.folder)
    lines = [
        "#!/bin/sh",
        f"# Open Studio: sets up run {setup.run_id} for {title} in ./{setup.folder}, then starts it.",
        f"# Skills: {', '.join(setup.skills) or 'none'}.",
        f"# The harness ({setup.program}) and its own model key come from this machine, not the studio.",
        "set -eu",
        *(f': "${{{name}:?set {name} first: {ENV_HINTS.get(name, "see the kit")}}}"' for name in setup.env),
        f"command -v {setup.program} >/dev/null 2>&1 || {{ echo 'open-studio: {setup.program} is not installed here' >&2; exit 1; }}",
        f"mkdir -p {folder}",
        f"cd {folder}",
        "put() { mkdir -p \"$(dirname \"$1\")\"; printf '%s' \"$2\" | base64 -d > \"$1\"; }",
        *(f"put {shlex.quote(file.path)} '{file.content_base64}'" for file in setup.files),
        "export " + " ".join(f"{name}={shlex.quote(value)}" for name, value in setup.exports.items()),
        f"echo 'open-studio: run {setup.run_id} is set up in ./{setup.folder}; starting {title}' >&2",
        setup.command,
    ]
    return "\n".join(lines) + "\n"


def write_refusal_script(reason: str) -> str:
    """A script that only says why the sandbox can't be set up, and fails."""
    return f"#!/bin/sh\necho {shlex.quote(f'open-studio: {reason}')} >&2\nexit 1\n"
