# Open Studio: Code Practices

This file is for any agent (or person) working in this repo. Read it before you add or change code.

What we're building is described in [open-studio-brief.md](../open-studio-brief.md). This file covers **how** we build it.

### Current direction (where we differ from the brief)

- **The home page is a grid** (masonry, newest first), as in the brief. A free-form canvas/map was tried and dropped.
- **The subject → project → session hierarchy is on hold.** Structure comes from LLM tags (filtering) and embeddings ("Related") for now. Don't add subjects, projects, sessions or lenses until the owner asks.
- **Design: raw and minimal.** One sans-serif face, black text on white. No boxes, borders, cards, shadows, icons or button styling. Controls are plain words. Color comes only from the work itself (images and video). All styling lives in `frontend/src/styles/global.css`. Don't add a CSS framework or component library.
- **Links are the navigation (Zettelkasten-style).** Every view is a URL: entry pages, tag selection, search, view size and sort (`/?tag=bread&view=rows`). Anything a visitor can see should be reachable by a link, and pages should link to each other (tags, related entries) so you can wander between them.
- **Controls are words, never icons.** "small · medium · large · rows", "recent · oldest · title". The current choice is underlined.
- **Media is never altered.** Uploads are stored as the original file. Linked media (YouTube, Google Drive) is shown from where it lives, not copied. Deal with storage limits when they come.
- **Hosting isn't decided yet** (likely Firebase, maybe AWS). Keep storage behind `backend/app/database.py` and `integrations/media_storage.py` so it can be swapped later.

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
├── open-studio-brief.md      Product brief: what we're building and why
├── README.md                 How to run it; map of the top-level folders
│
├── backend/                  Python API (FastAPI + SQLite)
│   ├── README.md
│   ├── app/
│   │   ├── main.py           Starts the app, registers every feature's routes
│   │   ├── config.py         Every setting read from backend/.env
│   │   ├── database.py       Opens the database
│   │   ├── auth/             Owner-token check for write requests
│   │   ├── features/
│   │   │   ├── entries/      Entries: storage, visibility, CRUD, enrichment (tags + embedding)
│   │   │   ├── capture/      Paste a link → prefilled entry draft
│   │   │   ├── tags/         LLM tag suggestions; tag descriptions + importance (key / normal / hidden)
│   │   │   ├── related/      Closest entries by meaning (shared tags as fallback)
│   │   │   ├── search/       Search by meaning (embeddings) + plain word matches
│   │   │   └── media/        Image/video upload
│   │   └── integrations/     OpenRouter (LLM, embeddings), file storage. One file each.
│   │       └── link_readers/ One reader per site (YouTube, Google Drive, GitHub, Instagram, X) + a general webpage reader
│   ├── scripts/              One-off tools run by hand (e.g. seed sample entries)
│   └── tests/                Mirrors app/ folder-for-folder
│
├── frontend/                 React + TypeScript (Vite dev server)
│   ├── README.md
│   └── src/
│       ├── main.tsx          Mounts the app
│       ├── App.tsx           Route table: which URL shows which page
│       ├── pages/            One file per URL (HomePage, EntryPage, AboutPage, StudioPage)
│       ├── features/
│       │   ├── grid/         Home page browsing: grid/rows views, cards, tag line, search/view/sort controls, URL state
│       │   ├── entries/      Pieces of the entry page (wall label, media series, tags, related)
│       │   └── studio/       Owner-only form, link capture, media list editor, entry list, tag notes
│       ├── components/       Site-wide pieces with no knowledge of our data (SiteHeader, SiteFooter, CrosshairCursor)
│       ├── api/              Every call to the backend, one file per area
│       ├── types/            Shared data shapes, matching the backend schemas
│       └── styles/           global.css: the entire visual style
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
| Pages | end in `Page` | `HomePage.tsx`, `LensPage.tsx` |
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
| **Grid** | The home page: every public entry as a card, newest first. |
| **Studio page** | The owner's hidden admin page at `/studio`. |
| **Owner token** | The admin password (`OWNER_TOKEN` in `backend/.env`). |
| **Entry link** | A manual connection between two entries. |
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
6. **Tests mirror the code.** Tests for `backend/app/features/tags/tag_suggester.py` live in `backend/tests/features/tags/test_tag_suggester.py`. Test file names say what they test. Tests never call OpenRouter.
7. **Keep it minimal.** Before adding a feature, page, setting or style, ask whether the site works without it. If it does, leave it out or ask first.
