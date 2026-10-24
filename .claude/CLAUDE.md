# Open Studio: Code Practices

This file is for any agent (or person) working in this repo. Read it before you add or change code.

What we're building is described in [open-studio-brief.md](../open-studio-brief.md). This file covers **how** we build it.

### Current direction (where we differ from the brief)

- **Every board opens on the sphere view**: each entry's picture floats on the surface of one orb in time order, newest at the top and oldest at the bottom, so each year is a band. It turns slowly and can be dragged. A Time slider (`?from=2023-04&to=2024-09`) picks a span of months, highlights it in every view and turns the orb so that band faces you. The masonry grid (newest first) and rows are one click away. (A free-form canvas/map and an ink-blot view were tried and dropped.)
- **Boards are separate spaces, and never mix.** Every entry is on one board. `home` is the owner's own collection, shown at `/`; every other board (bread, ceramics, graphics, photography in the demo data; or a focused effort agents are signed on to) has its own page at `/b/<slug>` with only its own entries, tags, time, search and Related. Boards aren't the brief's subjects: they separate whose work and which effort, not topics within one collection.
- **Entries build on each other.** A "builds on" link (an entry link with a direction and a note) chains entries into lines and trees; `GET /api/entries/{id}/chain` shows the tree around one entry.
- **The subject → project → session hierarchy is on hold.** Structure comes from LLM tags (filtering) and embeddings ("Related") for now. Don't add subjects, projects, sessions or lenses until the owner asks.
- **Design: a Swiss page grid, after Müller-Brockmann's "Grid Systems".** A 12-column grid inside generous margins; every page is a stack of labeled rows (`components/LabelRow.tsx`): a quiet label hangs in columns 1–3, content starts at column 4, wide rows (the sphere, the picture grid) span all 12. One line of body text is the unit for all vertical space, and the column gutter is one line too. Pictures span whole columns (masonry column counts divide 12). Rules run the full width of the screen: a double rule for major breaks (under the header, before the footer), a single hairline for minor ones; no vertical rules. One typeface, Inter (self-hosted), in few sizes; hierarchy comes from size, ink strength (full, soft) and space, never extra colors. Dark ink on a warm off-white paper, plus two small accents kept for the controls so they read apart from the work: a Swiss red (`--accent`) for the space you're in and the underline of picked modes, and a shaded paper band (`--paper-shade`) under the view and filter lines. No boxes, cards, shadows or button styling, with two exceptions that say "this can be picked": tags sit in thin flat ovals (key tags first, with a stronger outline; a picked tag's oval fills with ink), and picture sizes are three dots (`components/DotChoice.tsx`). A board's intro is a fixed three display lines tall, so its length never moves the page. Everything for moving around a board sits in the browse panel above the work: Space (the boards, as larger words, on the paper, never mixed with tags), then on the shaded band View (search · sphere ●●● rows · sort · clear) and Filter ("show tags & time" opens Tags and the Time slider; when closed, picked filters still show there). Modes (space, view, sort) stay underlined. Otherwise controls are plain words: a line of words is always a `.word-list`, and a pick-one word is always `components/WordChoice.tsx`. The normal mouse pointer is used everywhere (a custom cursor was tried and dropped). Labels use the small size, the site name the large one. Apart from those two accents, color comes only from the work itself. Motion is quiet and controlled, with no overshoot: things arrive decelerating and leave accelerating, using the motion tokens in `global.css` (after LottieFiles' motion-design skill), always with a reduced-motion alternative. The one overlay is the entry form's sheet: paper dropped over the page, closed by a double rule, with the page fading back behind it. All styling lives in `frontend/src/styles/global.css`, with the tokens at the top; change the look through those tokens, never one-off sizes or spacing in a component. Don't add a CSS framework or component library.
- **Links are the navigation (Zettelkasten-style).** Every view is a URL: entry pages, tag selection, search, view and sort (`/?tag=bread&view=rows`). Anything a visitor can see should be reachable by a link, and pages should link to each other (tags, related entries) so you can wander between them.
- **Controls are words, never icons.** "sphere · ●●● · rows", "recent · oldest · title". The only marks that aren't words are the three size dots and the tag ovals. The current mode is underlined; a picked tag is a filled oval.
- **Media is never altered.** Uploads are stored as the original file. Linked media (YouTube, Google Drive) is shown from where it lives, not copied. Deal with storage limits when they come.
- **Hosting:** backend on Fly.io (SQLite on a persistent volume), uploaded media in Cloudflare R2, frontend on Firebase Hosting, domain and DNS on Cloudflare. Every deploy setting lives in `deploy.toml` (not committed); `deploy.py` pushes it out, by hand or from GitHub Actions on every push to `main`. Setup steps are in the backend and frontend READMEs. Keep storage behind `backend/app/database.py` and `integrations/media_storage.py` so it can be swapped later.

---

## 1. The core idea

The owner of this project reads the codebase **at the level of files and folders, not individual lines.**
They should be able to open any folder, read the file names and the header at the top of each file, and understand:

- what this part of the system does
- where a given behavior lives
- what to change to adjust a feature

Every rule below supports that. When a rule doesn't cover a situation, pick the option that makes the file tree easier to understand.

---

## 2. Principles

1. **One file, one job.** You should be able to describe a file's purpose in one sentence without using "and". If you can't, split it.
2. **Names say what's inside.** A file name should tell you what's in it without opening it. `entry_card.tsx` and `link_unfurler.py` are good names. `utils.py`, `helpers.ts`, `misc/`, `common.py` and `stuff/` are banned.
3. **Every file starts with a header.** (Format is in section 5.)
4. **Group by feature, then by role.** Code for "entries" lives together. Inside that group, files are split by role: HTTP routes, business logic, database tables and so on.
5. **Clear boundaries.** Each layer talks only to the layer below it (section 4). The frontend never knows about the database. Routes never write SQL.
6. **Small and flat over clever and deep.** Prefer a few obvious files over abstractions, base classes or generic frameworks. Don't build for features we don't have yet.
7. **Use the project's words.** Code uses the vocabulary in section 7, everywhere, exactly.

---

## 3. Project structure

React frontend, Python backend, one repo.

```
open-studio/
├── .claude/                  Agent guidelines (this file) + local run config
├── .github/workflows/        deploy.yml: runs the tests and deploy.py on every push to main
├── open-studio-brief.md      Product brief: what we're building and why
├── README.md                 How to run it; map of the top-level folders
├── deploy.py                 Ships backend (Fly.io) and frontend (Firebase) using deploy.toml
├── deploy.toml.example       Every deploy setting and key in one file (copy to deploy.toml)
│
├── backend/                  Python API (FastAPI + SQLite)
│   ├── README.md
│   ├── app/
│   │   ├── main.py           Starts the app, registers every feature's routes
│   │   ├── config.py         Every setting read from backend/.env
│   │   ├── database.py       Opens the database
│   │   ├── database_migrations.py  Changes to existing tables (new fields), run once each on startup
│   │   ├── auth/             Who is asking (visitor, agent, owner) + agents' write limit
│   │   ├── features/
│   │   │   ├── boards/       Boards: separate spaces, each with a brief and the agents signed on to it
│   │   │   ├── agents/       Agents: the owner adds, pauses, re-keys and removes them; their status and last seen
│   │   │   ├── agent_log/    The public agent log: what agents plan, think, find and ask
│   │   │   ├── entries/      Entries: storage, visibility per viewer, CRUD, pages, enrichment (tags + embedding)
│   │   │   ├── entry_links/  "Builds on" links between entries, and the chain around an entry
│   │   │   ├── capture/      Paste a link → prefilled entry draft
│   │   │   ├── tags/         LLM tag suggestions; tag descriptions + importance (key / normal / hidden)
│   │   │   ├── related/      Closest entries by meaning (shared tags as fallback)
│   │   │   ├── search/       Search by meaning (embeddings) + plain word matches
│   │   │   └── media/        Image/video upload
│   │   ├── agent_server/     The studio as an MCP server (/mcp) for agents: board, read, write, chain and log tools
│   │   └── integrations/     OpenRouter (LLM, embeddings), file storage. One file each.
│   │       └── link_readers/ One reader per site (YouTube, Google Drive, GitHub, Instagram, X) + a general webpage reader
│   ├── scripts/              One-off tools run by hand (e.g. wipe local data and seed ~200 demo entries on five boards, with chains and two demo agents)
│   └── tests/                Mirrors app/ folder-for-folder
│
├── frontend/                 React + TypeScript (Vite dev server)
│   ├── README.md
│   └── src/
│       ├── main.tsx          Mounts the app
│       ├── App.tsx           Route table: which URL shows which page
│       ├── pages/            One file per URL (BoardPage for / and /b/<slug>, EntryPage, AgentsPage, AboutPage, StudioPage, SketchPage)
│       ├── features/
│       │   ├── grid/         Browsing a board: the browse panel (spaces, tag ovals, time slider, view controls), sphere/grid/rows views, cards, the shared highlight rule, URL state, loading a page at a time
│       │   ├── entries/      Pieces of the entry page (wall label, media series, tags, related)
│       │   ├── agents/       Pieces of the agents page (agent list, agent log)
│       │   ├── studio/       Owner-only entry form (a sheet over any page: ?add, ?edit=<id>), link capture, media list editor, entry list, tag notes, agent list
│       │   └── sketches/     Scratch: home-page ideas tried on real data at /sketch (contact sheet + threads). Delete when one graduates.
│       ├── components/       Site-wide pieces with no knowledge of our data (LabelRow, WordChoice, DotChoice, SiteHeader, SiteFooter)
│       ├── api/              Every call to the backend, one file per area
│       ├── types/            Shared data shapes, matching the backend schemas
│       └── styles/           global.css: the entire visual style
│
├── skills/open-studio/       SKILL.md: how an agent researches for and adds to a studio over MCP
│
└── ios/                      iPhone share-sheet extension + one-screen setup app (Swift)
    ├── README.md             How to build it on a Mac and get it onto a phone
    ├── project.yml           Xcode project description (XcodeGen); the .xcodeproj is generated
    ├── OpenStudio/           The app: enter server address + owner token
    ├── ShareToStudio/        The share extension: link, note or photos → made by me / inspiration, visibility, note → entry
    └── Shared/               Used by both: backend calls, data shapes, settings storage
```

**Adding a new top-level folder, a new feature folder, or a new dependency is a structural decision. Propose it to the owner first.** Adding files inside existing folders doesn't need approval.

---

## 4. How the pieces connect

### Backend: feature folders share the same file roles

```
features/entries/
├── routes.py     HTTP endpoints. Reads the request, calls the service, returns the response. No logic.
├── service.py    The actual behavior: rules, decisions, orchestration.
├── models.py     Database tables (what's stored).
└── schemas.py    API shapes (what goes over the wire).
```

A feature only has the files it needs (related has no table, so no `models.py`). When a job outgrows `service.py`, give it its own descriptively named file (`entries/enrichment.py`, `related/similarity.py`, `tags/tag_suggester.py`).

Dependencies only point **down**:

```
routes  →  service  →  models / integrations
```

- Routes never touch the database or outside services directly.
- A feature reads another feature's data through that feature's **service** (related and tags both go through `entries/service.py`). It may reuse another feature's **schemas** as response shapes, and small pure helpers (search uses `related/similarity.py`). It never queries another feature's tables.
- `agent_server/` is a second front door beside the routes, for agents (MCP). Its tools are like routes: they call feature services and never decide visibility or write SQL themselves.
- Integrations know nothing about our features. `llm_client.py` doesn't know what an entry is. Prompts live with the feature that uses them.

### Frontend: same idea

```
pages/  →  features/  →  components/
   ↓           ↓
        api/  (the only place that talks to the backend)
```

- **pages/** decide what a URL shows. They load data and arrange features. Filter state (e.g. `?tag=`) lives in the URL so views can be shared.
- **features/** are UI pieces that know about our data (`EntryCard`, `WallLabel`, `EntryForm`).
- **components/** are generic UI that could be reused in another project.
- **api/** holds every `fetch` call. Nothing else calls the backend.

One React component per file. The file name matches the component name (`EntryCard.tsx` exports `EntryCard`).

---

## 5. File headers

Every source file starts with a short header. It's the most important part of the file for the owner, so keep it accurate.

The header answers:
1. **What** this file does (1–2 sentences, plain English).
2. **Where it fits**: what uses it, or what it relies on, when that's not obvious.
3. **Not here** (optional): where a closely related thing lives, if someone might look here for it.

**Python** uses a module docstring:

```python
"""
Entry service: the rules for creating, updating and publishing entries.

Used by entries/routes.py and capture/service.py.
Visibility checks (who can see what) live in entries/visibility_rules.py.
"""
```

**TypeScript / React** uses a block comment:

```tsx
/**
 * EntryCard: one tile in the browsing grid, showing the "wall label"
 * (title · kind · date · source) and the "why it's here" line.
 *
 * Used by every grid page. Clicking it goes to EntryPage.
 */
```

Rules:
- Write for someone who has never seen the code. No jargon the brief doesn't use.
- **If you change what a file does, update its header in the same change.** A wrong header is worse than none.
- Config files that can't hold comments (like `package.json`) are exempt. Explain them in the folder's README instead.

---

## 6. Naming

| Thing | Convention | Example |
|---|---|---|
| Python files | `snake_case`, named for what they contain | `link_unfurler.py`, `visibility_rules.py` |
| React component files | `PascalCase`, same as the component | `EntryCard.tsx`, `SubjectPage.tsx` |
| Other TS files | `camelCase` | `entriesApi.ts`, `useTagFilters.ts` |
| Swift files | `PascalCase`, same as the main type inside | `ShareForm.swift`, `StudioApi.swift` |
| Folders | lowercase, plural for collections | `features/entries/`, `pages/` |
| Pages | end in `Page` | `BoardPage.tsx`, `LensPage.tsx` |
| Functions | verb first, says the result | `publish_entry`, `find_related_entries`, `fetchSubjects` |

Choose the longer, clearer name over the short, vague one: `suggest_tags_for_entry` over `process`.

---

## 7. Shared vocabulary

Use these words exactly, in file names, function names, database tables, API routes and UI. Don't invent synonyms.

| Word | Meaning |
|---|---|
| **Entry** | The core unit: one thing in the collection. (The brief also says "artifact"; in code, always say `entry`.) |
| **Subject**, **Project**, **Session** | The brief's hierarchy. Reserved words, not built yet. |
| **Tag** | A short, plain, lowercase label ("bread", "machine learning"). Suggested by the LLM, editable. Can have a description and an importance: key (first, in black), normal, or hidden. |
| **Lens** | A saved, curated view for one audience (e.g. `/work`). Not built yet. |
| **Kind** | An entry's medium: `link`, `note`, `book`, `sketch`, ... |
| **Capture** | Pasting a link and getting a prefilled entry draft back (title, date, author, pictures). |
| **Link reader** | Code that knows how to read one site (`youtube_reader.py`). Anything else uses `webpage_reader.py`. |
| **Media item** | One picture or video in an entry: `image`, `video` or `embed` (a player in an iframe). An entry has a list. |
| **Cover** | The first media item; what the grid shows. |
| **Visibility** | `private`, `unlisted` or `public`. |
| **Related** | Entries found by embedding similarity. |
| **Embedding** | An entry's meaning as a list of numbers. Computed from title, description, kind, source and tags. |
| **Grid** | A board's public entries as cards, newest first, in three picture sizes. One of a board's views. |
| **Sphere** | A board's default view: its entries' pictures floating on one orb, newest at the top, oldest at the bottom. |
| **Band** | One year's ring of entries around the sphere. |
| **Highlight** | A picked tag or span of months: matching entries stand out, the rest fade (`grid/entryHighlight.ts`). |
| **Browse panel** | The one block above a board's work holding every way to move around it: Space, Tags, Time, View (`grid/BrowsePanel.tsx`). |
| **Studio page** | The owner's hidden admin page at `/studio`. |
| **Owner token** | The admin password (`OWNER_TOKEN` in `backend/.env`). |
| **Agent** | Another program (a Claude session, a research bot) the owner added on the studio page, with its own token. Reads the studio and adds entries to the boards it is signed on to, which arrive unlisted and signed `added_by: agent:<name>` until the owner publishes them. Can be paused (reads only). |
| **Agent log** | The public record of agents' work at `/agents`: each line a `plan`, `thought`, `finding`, `question` or `status`, about a board and maybe an entry. |
| **Status** | An agent's one line about what it's doing now, set by the agent. |
| **Board** | A separate space in the studio. Every entry is on one board. `home` is the owner's own collection; other boards hold one focused effort, with a description agents read as their brief. |
| **Entry link** | A "builds on" connection: one entry builds on an earlier one, with a note on how. |
| **Chain** | The entries an entry builds on and that build on it, a few steps each way: the line of work it belongs to. |
| **Wall label** | The consistent placard shown on every card. |

If a new concept needs a name, add it here.

---

## 8. Keep files readable at a glance

- **Aim for under ~200 lines per file.** Past ~300, split it. Long files are where structure gets lost.
- Put the most important thing (the main function, the exported component) near the top, below the header.
- Comments explain **why**, not what. The header already covers what.
- No dead code, no commented-out code, no leftover TODOs without a short reason.
- No magic values buried in logic. Put settings in `config.py` (backend) or a clearly named constants file (frontend).

---

## 9. How agents should work in this repo

1. **Find the right place first.** Before writing code, decide which folder and file it belongs in using sections 3–4. If nothing fits, propose a new file and say why.
2. **Explain changes at the file level.** When you finish, summarize which files you created, changed or deleted and what each one now does. The owner reviews structure, not syntax.
3. **Keep the map current.** If you add a folder or change what a folder holds, update this file's structure diagram and that area's README.
4. **Ask before structural changes** (new top-level folders, new feature folders, new dependencies, changes to the data model in the brief).
5. **Follow the brief's build phases.** Don't build phase 4 features while working on phase 1 unless asked.
6. **New fields need a migration.** Adding or renaming a field in a `models.py` also needs a step at the end of `backend/app/database_migrations.py`, or the live database won't have it.
7. **Tests mirror the code.** Tests for `backend/app/features/tags/tag_suggester.py` live in `backend/tests/features/tags/test_tag_suggester.py`. Test file names say what they test. Tests never call OpenRouter.
8. **Keep it minimal.** Before adding a feature, page, setting or style, ask whether the site works without it. If it does, leave it out or ask first.
