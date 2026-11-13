# iOS

Adds "Open Studio" to the iPhone share sheet. Share a post from Instagram, X, YouTube, TikTok or
Pinterest (or any link from Safari), a note from Notes, or photos and videos from Photos, and it
goes straight onto a board. In the sheet you pick:

- the **space** (board) it goes on: home or any other board, starting on the one you used last.
  The agents signed on to that board are named under it.
- **made by me** or **inspiration**, and **private / unlisted / public**
- what it **builds on** (behind the caret): one of that board's newest entries, so it joins a chain
- a line on **why it's here**

then tap **save**. Tags are suggested as usual.

A shared note arrives with its first line as the title and the rest as the text, both editable
before saving. It's saved as kind `note`. (In Notes: share > **Send a Copy** > Open Studio.)
Photos shared with a caption (some apps send the post's text along) take its first line as the title.

The sheet looks like the site: Inter on the warm paper, a double rule under the header, a section
line for the boards with the current one in red, the shaded control band, plain words for every
control. The look lives in `Shared/StudioStyle.swift`, copied from the tokens at the top of
`frontend/src/styles/global.css`; change both together.

## The app: the studio page

Open the app and you're on the website's studio page, already signed in: add an entry with the plus
(pictures and videos from the phone, or a link), edit, publish, and manage boards, tags and agents.
It's the real site in a web view, so anything the site gains, the app has the same day. Links to other
sites (a source, YouTube) open in Safari. Swipe back, pull down to reload. A line of words at the bottom:
**back**, **studio** (return to the studio page) and **setup**.

Every uploaded picture or video keeps its file size (in the entry form, on the entry page under the
picture, and while the share sheet uploads), so you can see when something is heavy enough to link to instead.

The first time (and from **setup**) it asks for:
- the **server address**: the backend, e.g. `https://api.yourdomain.com` (the share sheet uses this)
- the **site address**: the website, e.g. `https://yourdomain.com` (the app opens this)
- the **owner token**

Saving checks the server and lists the boards; then **open the studio**.

## What's where

| Path | What it does |
|---|---|
| `project.yml` | Describes the Xcode project (targets, bundle IDs, fonts, share-sheet rules). Edit this, not the generated `.xcodeproj`. |
| `OpenStudio/` | The app: `OpenStudioApp.swift` starts it and picks the screen. `SetupView.swift` takes the server address, site address and owner token, and checks the server. `StudioSiteView.swift` is the website with the back · studio · setup line; `StudioWebView.swift` is the web view itself: it signs in by writing the owner token where the site keeps it (the key in `frontend/src/api/ownerSignIn.ts`; change both together) and sends other sites' links to Safari. |
| `ShareToStudio/` | The share extension. `ShareViewController` is the entry point, `ShareForm` is what you see, `ShareFormModel` does the work: `SharedItems` reads what was shared (link, note, or photos), `PreparedMedia` + `PhotoDate` get photos/videos ready to upload, `EntryBuilder` turns it all into an entry. `ShareChoices` holds the answers. |
| `Shared/` | Used by both. Talking to the backend: `StudioApi` (every call), `EntryShapes` (data shapes matching the backend), `StudioSettings` + `SharedKeychain` (where the address, token and last board are kept), `MultipartBody` (file upload format). The look: `StudioStyle` (colors, type, space, motion), `Fonts/` (Inter, with its license), and the phone versions of the site's page pieces: `LabelRow`, `SectionLine`, `ControlBand`, `WordList`, `WordChoice`, `CaretIcon`, `StudioMark` (the logo's panel of squares, which sweeps while waiting), `LoadingWord` (the mark beside a soft word). |

## How it uses the backend

No new endpoints. The app shows the site itself; the share sheet calls the same API as the site:

1. `GET /api/boards` for the boards and their agents, then `GET /api/entries/page?board=` for the
   picked board's newest entries (what it could build on).
2. A link → `POST /api/capture/link` (title, author, picture, date), in the background while you type.
3. Photos/videos → `POST /api/media`, one file at a time. (Notes skip steps 2 and 3.)
4. `POST /api/entries` with the board, your choices and note.
5. If you picked something it builds on: `POST /api/entries/{id}/builds-on`.

"Made by me" leaves the source name empty, which is how the site already marks the owner's own work.
Entries from the phone are signed `added_by: owner`, because the phone uses the owner token.

## Building it (needs a Mac)

iOS apps can only be built with Xcode, which only runs on macOS. (GitHub Actions also builds it on
a Mac whenever `ios/` changes, `.github/workflows/ios-build.yml`, to catch code that doesn't compile.)

1. Install Xcode (App Store) and XcodeGen: `brew install xcodegen`.
2. In `project.yml`, set `DEVELOPMENT_TEAM` (your Apple team ID) and `BASE_BUNDLE_ID` (e.g. `com.collinwen.openstudio`).
3. In this folder: `xcodegen`. Open `OpenStudio.xcodeproj`.
4. Plug in your iPhone, pick it as the run destination, press Run. The first time, the phone asks you to
   trust the developer (Settings > General > VPN & Device Management) and to turn on Developer Mode.
5. Open the app, enter the server address, site address and owner token, save. It should say `connected · 5 boards: home, …`. Tap **open the studio**.
6. In any app, tap share. If "Open Studio" isn't in the row of apps, scroll to the end, tap **More**, and add it.

## Getting it onto your phone for good

| Way | Cost | Catch |
|---|---|---|
| Run from Xcode with a free Apple ID | free | The app stops opening after **7 days**; re-run from Xcode to renew. |
| Paid Apple Developer Program, run from Xcode | $99/yr | Lasts a year. |
| Paid program + **TestFlight** | $99/yr | Install from the TestFlight app, no cable. Builds last 90 days. Uploading needs a Mac, or a cloud Mac (e.g. GitHub Actions). |

It never needs to go on the App Store: it's for one person.

## The server has to be reachable from the phone

`localhost` on your computer isn't reachable from the phone. While testing, start the backend with
`--host 0.0.0.0` and use your computer's address on the same Wi-Fi (e.g. `http://192.168.1.20:8000`).
For the app, also start the frontend with `npm run dev -- --host` and use `http://192.168.1.20:5173` as the
site address. For everyday use, the site and backend need to be hosted (with https) somewhere the phone can reach.
