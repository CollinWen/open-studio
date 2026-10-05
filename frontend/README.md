# Frontend

React + TypeScript site. Text and images on white, nothing else.

## Setup (first time)

```bash
npm install
```

## Run

```bash
npm run dev
```

Requests to `/api` and `/media` are passed through to the backend on port 8000
(see `vite.config.ts`), so start the backend too.

## Pages

| URL | File | What it shows |
|---|---|---|
| `/` | `pages/HomePage.tsx` | The whole collection. `?tag=` highlights a tag and shows its description, `?q=` searches, `?view=small\|large\|rows`, `?sort=oldest\|title\|relevance` |
| `/entry/:id` | `pages/EntryPage.tsx` | One entry: media, wall label, tags, related entries |
| `/about` | `pages/AboutPage.tsx` | The welcome text |
| `/studio` | `pages/StudioPage.tsx` | Owner-only: add, edit, delete entries. Linked as "owner" in the footer. `?edit=<id>` opens one entry. |

## Layout

| Path | What it does |
|---|---|
| `src/pages/` | One file per URL |
| `src/features/grid/` | Home page browsing: grid and rows views, cards, the tag line, search/view/sort controls, and `useBrowseParams` (all of it kept in the URL) |
| `src/features/entries/` | Pieces of the entry page (wall label, the full series of pictures and videos, tags, related) |
| `src/features/studio/` | The owner's form: paste-a-link capture, the media list (cover, captions, uploads), the entry list, and tag notes (description + importance) |
| `src/components/` | Site-wide pieces (header, footer, crosshair cursor) |
| `src/api/` | Every call to the backend, and the stored owner token |
| `src/types/` | Data shapes, matching the backend's `schemas.py` files |
| `src/styles/global.css` | The entire visual style |

Config files (`package.json`, `tsconfig.json`, `vite.config.ts`, `index.html`) are standard Vite + React setup.
