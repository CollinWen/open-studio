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
| `app/auth/` | Checks the owner token on write requests |
| `app/features/entries/` | Entries: storage, visibility rules, create/edit/delete, enrichment (tags + embedding). Each entry has a list of media items; the first is the cover. |
| `app/features/capture/` | Paste a link, get a prefilled entry draft back (`POST /api/capture/link`) |
| `app/features/tags/` | The LLM prompt that suggests tags; tag counts; the owner's tag descriptions and importance (key / normal / hidden) |
| `app/features/related/` | Finds the entries closest in meaning to a given one (shared tags as fallback) |
| `app/features/search/` | `GET /api/search?q=` — ranks entries by meaning (embeddings) and boosts plain word matches; text-only without an OpenRouter key |
| `app/features/media/` | Image and video uploads, stored as the original file |
| `app/integrations/` | Thin wrappers around OpenRouter (LLM, embeddings) and file storage |
| `app/integrations/link_readers/` | One reader per site, chosen in `read_link.py`. YouTube (title, channel, upload date, description; no API key), Google Drive (full-resolution photo, date taken from EXIF; file must be shared "Anyone with the link"), GitHub (repo details), Instagram (caption, author, picture; the picture link expires after a few weeks), X (post text, author, date; no pictures), and any other page (link-preview tags). |
| `scripts/` | Hand-run tools. `seed_sample_entries.py` adds (or `--remove`s) a dozen made-up entries with generated images. |
| `data/` | Created on first run: `studio.db` and uploaded `media/`. Not committed. |

Empty `__init__.py` files only mark folders as Python packages.

## Capture from a phone

`POST /api/entries` with header `Authorization: Bearer <OWNER_TOKEN>` and a JSON
body like `{"title": "...", "description": "...", "source_url": "..."}`.
The iOS share extension in `ios/` does this. To reach the backend from a phone on
the same Wi-Fi while testing, run uvicorn with `--host 0.0.0.0`.
