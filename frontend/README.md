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
| `/`, `/b/<slug>` | `pages/BoardPage.tsx` | One board: `/` is home (the owner's own collection), `/b/bread` the bread board, and so on; a board shows only its own entries. `?tag=` highlights a tag and shows its description, `?from=2023-04&to=2024-09` highlights a span of months (and turns the sphere to it), `?q=` searches the board, `?view=small\|medium\|large\|rows` (default: the sphere), `?sort=oldest\|title\|relevance` |
| `/entry/:id` | `pages/EntryPage.tsx` | One entry: media, wall label, tags, related entries |
| `/about` | `pages/AboutPage.tsx` | The welcome text |
| `/sketch` | `pages/SketchPage.tsx` | Scratch page, not linked: home-page ideas on the real collection. `?sketch=hover\|threads\|kinship`, `?size=`, `?gap=` |
| `/agents` | `pages/AgentsPage.tsx` | Every agent (status, boards, last seen) and the agent log, newest first. `?agent=<name>` or `?board=<slug>` narrows the log. |
| `/studio` | `pages/StudioPage.tsx` | Owner-only: every entry to edit or delete, tag notes, and agents (add, pause, new token, remove, which boards). Linked as "owner" in the footer. |
| any page `?add`, `?edit=<id>` | `features/studio/EntryFormModal.tsx` | Owner-only: the entry form as a sheet over whatever page you're on ("add" in the header, "edit" under an entry's title). |

## Layout

| Path | What it does |
|---|---|
| `src/pages/` | One file per URL |
| `src/features/grid/` | Browsing a board. `BrowsePanel` holds every way to move around in one block: `BoardLine` (the spaces), `TagFilter` (tags in ovals), `TimeRangeFilter` (the month slider, with `monthRange` for months), `BrowseControls` (search, sphere / size dots / rows, sort, clear). The views: the sphere (`SphereView`, with `sphereLayout` for where things sit and `sphereMotion` for turning and perspective), the grid and rows, cards. `entryHighlight` (which entries fade when a tag or span of months is picked), `useBrowseParams` (all of it kept in the URL), `boardPath` (a board's address), and `useEntryPages` (loads a board a page at a time; new cards rise in and the sphere re-spreads as pages arrive) |
| `src/features/entries/` | Pieces of the entry page (wall label, the full series of pictures and videos, tags, related) |
| `src/features/sketches/` | The sketch page's experiments: a justified contact sheet (`justifyRows`), threads between related entries (`LinkLines`, `relatedLinks`) |
| `src/features/agents/` | The agents page's pieces: the list of agents (`AgentList`), the log (`AgentLog`), and `formatTimeAgo` |
| `src/features/studio/` | The owner's entry form, shown as a sheet over any page (`EntryFormModal`, opened by `?add` / `?edit=<id>`; `entrySavedEvent` tells the page to reload): paste-a-link capture, the essentials first with the rest behind "more", the media list (cover, captions, uploads); plus the entry list, tag notes (description + importance) and the agents list (`AgentManager`) |
| `src/components/` | Site-wide pieces (the labeled page row, the word-as-a-control `WordChoice`, the size dot `DotChoice`, header, footer) |
| `src/api/` | Every call to the backend, and the stored owner token |
| `src/types/` | Data shapes, matching the backend's `schemas.py` files |
| `src/styles/global.css` | The entire visual style; tokens (colors, type sizes, line unit, gutter, margins) at the top. The typeface comes from `@fontsource-variable/inter`, loaded in `main.tsx` |

Config files (`package.json`, `tsconfig.json`, `vite.config.ts`, `index.html`) are standard Vite + React setup.

## Deploy (Firebase Hosting)

`firebase.json` serves the built `dist/` folder and sends every URL to
`index.html` so links like `/entry/12` work.

```bash
npm install -g firebase-tools
firebase login
```
Put the Firebase project ID in `deploy.toml` at the repo root, then from the root:
```bash
python deploy.py frontend
```
It builds with `VITE_API_URL=https://api.<your domain>` and deploys.
Then in the Firebase console: Hosting → Add custom domain → `yourdomain.com`,
and add the records it shows in Cloudflare as **DNS only** (grey cloud).
