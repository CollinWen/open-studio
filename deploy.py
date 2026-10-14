"""
Deploy: reads every setting from deploy.toml and ships the site.

  python deploy.py            backend, then frontend
  python deploy.py backend    Fly.io only: snapshots the database, sends settings as Fly secrets, deploys
  python deploy.py frontend   Firebase only: builds with the API address, then deploys
  python deploy.py secrets    Fly secrets only: sends the settings now (restarts a running backend)

Run by hand, or by .github/workflows/deploy.yml on every push to main.
The backend's settings are listed in backend/app/config.py; the setup steps
are in backend/README.md and frontend/README.md.
"""

import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> None:
    config = tomllib.loads((ROOT / "deploy.toml").read_text())
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target == "secrets":
        send_fly_secrets(config, stage=False)
    if target in ("backend", "all"):
        deploy_backend(config)
    if target in ("frontend", "all"):
        deploy_frontend(config)


def deploy_backend(config: dict) -> None:
    app = config["fly"]["app"]
    snapshot_database(app)
    # Staged secrets take effect with the deploy, so the backend restarts only once.
    send_fly_secrets(config, stage=True)
    run(["flyctl", "deploy", "--app", app, "--ha=false"], cwd="backend")


def snapshot_database(app: str) -> None:
    """Save a copy of the database volume first, in case a migration goes wrong."""
    listing = subprocess.run(
        [find_executable("flyctl"), "volumes", "list", "--app", app, "--json"],
        capture_output=True, text=True, check=True,
    )
    for volume in json.loads(listing.stdout):
        if volume["name"] == "studio_data":
            run(["flyctl", "volumes", "snapshots", "create", volume["id"]], cwd="backend")


def send_fly_secrets(config: dict, stage: bool) -> None:
    domain, r2, secrets = config["site"]["domain"], config["r2"], config["secrets"]
    firebase_project = config["firebase"]["project"]
    # The site is reachable at Firebase's own addresses as well as the custom domain.
    site_addresses = [
        f"https://{domain}",
        f"https://www.{domain}",
        f"https://{firebase_project}.web.app",
        f"https://{firebase_project}.firebaseapp.com",
    ]
    settings = {
        "OWNER_TOKEN": secrets["owner_token"],
        "OPENROUTER_API_KEY": secrets["openrouter_api_key"],
        "FRONTEND_ORIGIN": ",".join(site_addresses),
        "R2_ACCOUNT_ID": r2["account_id"],
        "R2_ACCESS_KEY_ID": r2["access_key_id"],
        "R2_SECRET_ACCESS_KEY": r2["secret_access_key"],
        "R2_BUCKET": r2["bucket"],
        "MEDIA_PUBLIC_URL": f"https://media.{domain}",
    }
    # Secrets go in through stdin so they never show up in the command line or shell history.
    secret_lines = "\n".join(f"{key}={value}" for key, value in settings.items())
    command = ["flyctl", "secrets", "import", "--app", config["fly"]["app"]]
    run(command + (["--stage"] if stage else []), cwd="backend", stdin=secret_lines)


def deploy_frontend(config: dict) -> None:
    api_url = f"https://api.{config['site']['domain']}"
    # Vite bakes VITE_ variables from the environment into the build.
    run(["npm", "run", "build"], cwd="frontend", env={"VITE_API_URL": api_url})
    run(["firebase", "deploy", "--only", "hosting", "--project", config["firebase"]["project"]], cwd="frontend")


def run(command: list[str], cwd: str, stdin: str | None = None, env: dict | None = None) -> None:
    print(f"> {' '.join(command)}")
    subprocess.run(
        [find_executable(command[0]), *command[1:]],
        cwd=ROOT / cwd,
        input=stdin,
        text=True,
        env={**os.environ, **(env or {})},
        check=True,
    )


def find_executable(name: str) -> str:
    executable = shutil.which(name)
    if not executable:
        sys.exit(f"'{name}' isn't installed or isn't on PATH (see the READMEs).")
    return executable


if __name__ == "__main__":
    main()
