# Backend

Python API built with FastAPI. Stores entries in a SQLite file, asks an LLM
(via OpenRouter) for tags, and computes embeddings to find related entries.

## Setup (first time)

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
cp .env.example .env     # then fill in OWNER_TOKEN and OPENROUTER_API_KEY
```

Without an OpenRouter key everything still works, but new entries get no
suggested tags, and "Related" falls back to matching shared tags.

## Demo data (local only)

Local runs use made-up entries; the real collection lives on Fly. To wipe the
local database and refill it:

```bash
.venv/Scripts/python scripts/seed_demo_entries.py             # with embeddings, so Related is by meaning
.venv/Scripts/python scripts/seed_demo_entries.py --offline   # without OpenRouter
```

## Run

```bash
.venv/Scripts/python -m uvicorn app.main:app --reload
```

API docs appear at http://localhost:8000/docs.

## Test

```bash
.venv/Scripts/python -m pytest
```

## Layout

| Path | What it does |
|---|---|
| `app/main.py` | Starts the app and plugs in every feature's routes |
| `app/config.py` | Every setting read from `.env` |
| `app/database.py` | Opens the SQLite database |
| `app/database_migrations.py` | Changes to existing tables. Add a step here whenever a field is added to a `models.py`. |
| `app/auth/` | Who is asking: visitor, agent (a token from `AGENT_TOKENS`) or owner; agents' hourly write limit |
| `app/features/entries/` | Entries: storage, visibility rules (per viewer, in `visibility_rules.py`), create/edit/delete, enrichment (tags + embedding). Each entry has a list of media items; the first is the cover, and `added_by` says whether the owner or which agent added it. |
| `app/features/capture/` | Paste a link, get a prefilled entry draft back (`POST /api/capture/link`) |
| `app/features/tags/` | The LLM prompt that suggests tags; tag counts; the owner's tag descriptions and importance (key / normal / hidden) |
| `app/features/related/` | Finds the entries closest in meaning to a given one (shared tags as fallback) |
| `app/features/search/` | `GET /api/search?q=` — ranks entries by meaning (embeddings) and boosts plain word matches; text-only without an OpenRouter key |
| `app/features/media/` | Image and video uploads, stored as the original file (on disk locally, in Cloudflare R2 in production) |
| `app/agent_server/` | The studio as an MCP server at `/mcp`, for agents: read tools (interests, search, recent changes, related) and write tools (add, improve). Same rules as the web routes. How agents should use it: `skills/open-studio/SKILL.md`. |
| `app/integrations/` | Thin wrappers around OpenRouter (LLM, embeddings) and file storage |
| `app/integrations/link_readers/` | One reader per site, chosen in `read_link.py`. YouTube (title, channel, upload date, description; no API key), Google Drive (full-resolution photo, date taken from EXIF; file must be shared "Anyone with the link"), GitHub (repo details), Instagram (caption, author, picture; the picture link expires after a few weeks), X (post text, author, date; no pictures), and any other page (link-preview tags). |
| `scripts/` | Hand-run tools. `seed_demo_entries.py` wipes the **local** data and fills it with ~120 made-up entries (`demo_entries.py`) covering every source type, with generated pictures (`sample_images.py`). Refuses to run when R2 is configured. |
| `data/` | Created on first run: `studio.db` and uploaded `media/`. Not committed. |

Empty `__init__.py` files only mark folders as Python packages.

## Capture from a phone

`POST /api/entries` with header `Authorization: Bearer <OWNER_TOKEN>` and a JSON
body like `{"title": "...", "description": "...", "source_url": "..."}`.
The iOS share extension in `ios/` does this. To reach the backend from a phone on
the same Wi-Fi while testing, run uvicorn with `--host 0.0.0.0`.

## Agents

Other programs can be given their own token: `AGENT_TOKENS=scout=<token>,archivist=<token>`
in `.env` (or an `[agents]` section in `deploy.toml`). An agent can read the studio and add
entries, through the MCP server at `/mcp` or the same HTTP endpoints. Its entries arrive
**unlisted** and signed (`added_by: agent:scout`); publish the ones you want from the studio
page. Agents can't publish, delete, or edit your entries, can't add a link that's already
there, and can make `AGENT_WRITES_PER_HOUR` writes an hour (default 60).

```bash
claude mcp add --transport http open-studio http://localhost:8000/mcp \
    --header "Authorization: Bearer <agent token>"
```

## Deploy (Fly.io + Cloudflare R2)

The backend runs on Fly.io with the SQLite file on a persistent volume (`/data`).
Uploaded media goes to a Cloudflare R2 bucket, served at `media.yourdomain.com`.
Files: `Dockerfile` (the container), `fly.toml` (Fly settings), `.dockerignore`.

**1. R2 bucket (Cloudflare dashboard)**
- R2 → Create bucket, e.g. `open-studio-media`.
- Bucket → Settings → Custom domains → add `media.yourdomain.com`.
- Bucket → Settings → CORS policy: allow `GET` from `https://yourdomain.com`
  (lets the site read image pixels, e.g. for cover colors).
- R2 → Manage API tokens → create a token with **Object Read & Write** on that bucket.
  Note the Access Key ID, Secret Access Key and your Account ID.

**2. Fly app (from this folder, first time only)**
```bash
fly auth login
fly launch --no-deploy --copy-config      # note the app name it picks
fly volumes create studio_data --size 1   # 1 GB is plenty for the database
```
Put the app name and the R2 keys in `deploy.toml` at the repo root, then from the root:
```bash
python deploy.py backend
```
It sends every setting as a Fly secret and deploys on one machine (SQLite needs exactly one).

**3. api.yourdomain.com**
```bash
fly certs add api.yourdomain.com
```
Add the DNS records it prints in Cloudflare, set to **DNS only** (grey cloud).

Later deploys happen on every push to `main` (see the root README), or by hand with
`python deploy.py backend`, which first snapshots the database volume. Logs: `fly logs`. Fly snapshots the volume daily;
`fly ssh sftp get /data/studio.db` copies the database to your computer (also copy
`/data/studio.db-wal` if it exists: the database runs in WAL mode, and recent writes can still be in that file).
