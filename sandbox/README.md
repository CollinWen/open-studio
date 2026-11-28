# Sandbox

The harness image: what every agent sandbox has before a run starts. Pi
(the pi coding agent), git, curl and python, and a start script. Nothing in
it knows about a particular run, and it holds no keys.

An agent's sandbox has three layers, each set by a different hand:

| Layer | Set by | Holds |
|---|---|---|
| Harness | Whoever runs the sandbox (this image, plus what you pass in) | Pi, its model and its model key (e.g. `OPENROUTER_API_KEY`) |
| Run | The studio, at start, from the agent's settings and the run's token | The run's prompt, its AGENTS.md (each add-on and how to use it), its skills, the studio's MCP server (on the token), the tools it may use |
| Grants | The owner, on the studio's agents and add-ons pages | Boards, skills, add-ons: checked by the studio on every call (and by Composio, for its own) |

The studio never sees the harness's keys, and the sandbox never sees the
studio's. At start, `start-run.sh` fetches the run's setup script with the
run token alone (`GET /api/runs/current/sandbox.sh?harness=pi`, see
`backend/app/features/runs/sandbox_setup.py`). The script writes everything
into `./open-studio-run-<id>/`, sets `OPEN_STUDIO_API_URL`, `OPEN_STUDIO_MCP_URL`
and `OPEN_STUDIO_RUN` for the harness, and starts Pi there.

## Keys: the agent gets tools, not keys

| What the agent needs | Where its key lives |
|---|---|
| Its model (OpenRouter, ...) | The harness layer: this container's environment (`docker run -e`, or the sandbox app's Fly secrets) |
| The studio | The run token, in `OPEN_STUDIO_TOKEN`; it stops working when the run ends |
| Outside services' APIs (email, Exa, ...) | Composio, never the sandbox: the agent calls them as add-ons through the studio (`backend/README.md`, Add-ons) |
| A program in the sandbox that reads a key itself (a CLI) | The harness layer too, kept apart per agent: run each agent's sandboxes from its own Fly app (or image) holding only that agent's keys. The studio never stores them |
| `git push` | Planned: one-hour GitHub App tokens limited to a grant's repositories, which a git credential helper asks the studio for with the run token. Until then, Composio's GitHub tools (new repositories, files, issues), or a harness-layer key for a bot account that can reach only those repositories |

## Files

| File | What it does |
|---|---|
| `Dockerfile` | The image: Debian with Node 24, Pi 1.6.1, git, curl, ripgrep, python3 |
| `start-run.sh` | The entrypoint: fetch the run's setup with its token alone, run it |

## Run it

Issue a token on the studio page; each run needs only that token. The
studio's address is the same for every run.

```bash
docker build -t open-studio-sandbox sandbox/
docker run --rm \
  -e OPEN_STUDIO_URL='https://api.yourdomain.com' \
  -e OPEN_STUDIO_TOKEN='run.…' \
  -e OPENROUTER_API_KEY \
  open-studio-sandbox
```

Pi picks its model from its own settings. To choose one, mount a
`~/.pi/agent/settings.json` (`{"defaultProvider": "openrouter", "defaultModel": "…"}`)
or bake it into an image built on this one.

Without Docker: anywhere Pi 1.6 or later is installed, paste the kit's "pi"
line in an empty folder; it does the same there. Only `./open-studio-run-<id>/`
is written, so it's safe on a laptop too.

On Fly: create a separate app for sandboxes, give it the harness's keys as
its own secrets and the studio's address once (`fly secrets set
OPENROUTER_API_KEY=… OPEN_STUDIO_URL=https://api.yourdomain.com`), then
start one machine per run with just its token:

```bash
fly machine run . --app open-studio-sandboxes --rm --env OPEN_STUDIO_TOKEN='run.…'
```
