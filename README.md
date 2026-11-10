# Open Studio

A personal website that works as a museum in progress: a growing collection
of things I make and things I'm curious about, shown as a quiet grid of
images and text.

- What and why: [open-studio-brief.md](open-studio-brief.md)
- How the code is organized, and the rules for changing it: [.claude/CLAUDE.md](.claude/CLAUDE.md)

## Folders

| Folder | What's in it |
|---|---|
| `backend/` | Python API: stores entries, asks an LLM for tags, computes embeddings for "Related". See [backend/README.md](backend/README.md). |
| `frontend/` | React site: the home grid, entry pages, and the owner's `/studio` page. See [frontend/README.md](frontend/README.md). |
| `skills/` | How an agent (a Claude session, a research bot) reads and adds to the studio through its MCP server. See [skills/open-studio/SKILL.md](skills/open-studio/SKILL.md). |
| `ios/` | iPhone share-sheet extension: add links, notes and photos from any app straight onto a board. See [ios/README.md](ios/README.md). |
| `.claude/` | Guidelines for agents working on this repo, plus local run settings. |
| `.mcp.json` | Connects every Claude Code session opened on this repo to the live studio's MCP server, as the agent whose token is in `OPEN_STUDIO_AGENT_TOKEN`. See "Working as an agent" below. |

## Working as an agent

Open this folder in Claude Code (the desktop app's Code tab, or `claude` in a terminal) and it
connects to the studio's MCP server by itself, through `.mcp.json`. The token isn't in the repo:

1. On `/studio`, under Agents, add an agent (or re-key one), sign it on to a board, and copy its token.
2. Save the token as a user environment variable named `OPEN_STUDIO_AGENT_TOKEN`
   (Windows: Start → "Edit environment variables for your account" → New). To point at a local
   backend instead, also set `OPEN_STUDIO_MCP_URL` to `http://localhost:8000/mcp`.
3. Quit and reopen the desktop app so it sees the variable, open a session on this folder, and
   approve the `open-studio` server when asked. `/mcp` shows it connected.
4. Ask for the work, e.g. *"Read skills/open-studio/SKILL.md and skills/finding-sources/SKILL.md,
   then work on the `os` board: read the brief and the log, set your status, log a plan, add three
   entries that build on existing ones, and set your status to idle when done."*

Everything it does shows on `/agents` (status, plan, findings) as it happens, and what it
adds waits unlisted on `/studio` for you to publish. Re-keying or pausing the agent there
cuts it off at once.

## Running it locally

Two terminals. First time only: follow the setup steps in each folder's README.

```bash
cd backend && .venv/Scripts/python -m uvicorn app.main:app --reload
```

```bash
cd frontend && npm run dev
```

Then open http://localhost:5173.

**Adding work:** click "owner" at the bottom of any page (or go to `/studio`) and enter the
`OWNER_TOKEN` from `backend/.env`. After that, this browser shows an "add" link in the header
and an "edit" link on every entry.

**Demo entries** (to see the layout before adding real work): this **wipes the local
database** and fills it with about 160 made-up entries on five boards (home, bread,
ceramics, graphics, photography):

```bash
cd backend && .venv/Scripts/python scripts/seed_demo_entries.py --offline
```

## Deploying

Backend on Fly.io, media in Cloudflare R2, site on Firebase Hosting, domain on Cloudflare.
Every deploy setting and key lives in one file, `deploy.toml` (copy `deploy.toml.example`;
never committed). Then:

```bash
python deploy.py
```

First-time account setup (R2 bucket, Fly volume, Firebase project, DNS) is in
[backend/README.md](backend/README.md) and [frontend/README.md](frontend/README.md).

**Automatic deploys:** every push to `main` runs the backend tests and then `deploy.py`
([.github/workflows/deploy.yml](.github/workflows/deploy.yml)). It needs three GitHub secrets,
listed at the top of that file. When you change `deploy.toml`, update the `DEPLOY_TOML` secret too.

**Versions:** each deploy from `main` is tagged with the next version (`v0.1.0`, `v0.1.1`, ...),
and the site's footer shows the version that's live. To start a new series, push a tag by hand
(`git tag v0.2.0 && git push origin v0.2.0`); the next deploy counts on from it.

**Changing the data:** when a field is added to a `models.py`, add a step to
`backend/app/database_migrations.py`. It runs once on the live database at the next deploy,
right after a snapshot of the database is taken.
