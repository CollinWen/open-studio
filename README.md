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
| `ios/` | iPhone share-sheet extension: add links and photos from any app. See [ios/README.md](ios/README.md). |
| `.claude/` | Guidelines for agents working on this repo, plus local run settings. |

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

**Sample entries** (to see the layout before adding real work):

```bash
cd backend && .venv/Scripts/python scripts/seed_sample_entries.py
```

Remove them again with `--remove`.

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

**Changing the data:** when a field is added to a `models.py`, add a step to
`backend/app/database_migrations.py`. It runs once on the live database at the next deploy,
right after a snapshot of the database is taken.
