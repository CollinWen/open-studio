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

The sheet looks like the site: Inter on the warm paper (or the site's dark colors in dark mode), a double rule under the header, a section
line for the boards with the current one in red, the shaded control band, plain words for every
control. The look lives in `Shared/StudioStyle.swift`, copied from the tokens at the top of
`frontend/src/styles/global.css`; change both together.

## The app: the studio

The app is your studio, made for the phone (it's native, not the website in a frame):

- **Entries**, newest first: the date, title, board and who sees it, with a small square of the cover.
  Pick a board along the top (each with its count), search titles, notes and tags in the shaded band,
  and open **who sees it** to show only private, unlisted or everyone. Pull down to reload; swipe an
  entry left to delete it (it asks first).
- **Tap an entry** to change its title, board, who sees it (publishing is picking **everyone**), why
  it's here, its tags (separated by commas) and its pictures: make another the cover, remove one, or
  add more from Photos. Nothing is saved until **save**; while something is changed, **cancel** takes
  the back button's place and asks before throwing changes away. **Delete this entry** is at the end.
- **The plus** adds an entry: paste a link, choose photos or videos, or write a note, then the same
  form as the share sheet.

Boards, tags and agents are managed on the website's studio page.

Every uploaded picture or video keeps its file size (in the app, on the site's entry page under the
picture, and while uploading), so you can see when something is heavy enough to link to instead.
Light or dark follows the phone, with the site's dark colors.

The first time (and from **setup**) it asks for the **server address** (the backend, e.g.
`https://api.yourdomain.com`) and the **owner token**. Saving checks the server and lists the boards;
then **open the studio**.

## What's where

| Path | What it does |
|---|---|
| `project.yml` | Describes the Xcode project (targets, bundle IDs, fonts, share-sheet rules). Edit this, not the generated `.xcodeproj`. |
| `OpenStudio/` | The app. `OpenStudioApp` starts it and picks the screen; `SetupView` takes the server address and owner token and checks the server. The studio: `EntryListView` (the list, with `EntryRow` for each entry and `EntryListModel` loading, filtering and deleting), `EntryEditView` (one entry, with `MediaEditor` for its pictures and `EntryEditModel` saving the changes), `AddEntryView` (the plus: link, photos or note, then the add form) and `PhotoPicker` (the phone's photo picker, handing back the original files). |
| `ShareToStudio/` | The share extension: `ShareViewController` is its entry point, showing the add form from `Shared/`. |
| `Shared/` | Used by both. The add form: `ShareForm` is what you see, `ShareFormModel` does the work: `SharedItems` reads what was shared (link, note, or photos), `PreparedMedia` + `PhotoDate` get photos/videos ready to upload, `EntryBuilder` turns it all into an entry. `ShareChoices` holds the answers. Talking to the backend: `StudioApi` (every call), `EntryShapes` (data shapes matching the backend), `StudioSettings` + `SharedKeychain` (where the address, token and last board are kept), `MultipartBody` (file upload format). The look: `StudioStyle` (colors, type, space, motion), `Fonts/` (Inter, with its license), and the phone versions of the site's page pieces: `LabelRow`, `SectionLine`, `ControlBand`, `WordList`, `WordChoice`, `CaretIcon`, `PlusIcon`, `StudioMark` (the logo's panel of squares, which sweeps while waiting), `LoadingWord` (the mark beside a soft word). |

## How it uses the backend

No new endpoints: the phone calls the same API as the site. Adding an entry (share sheet or plus):

1. `GET /api/boards` for the boards and their agents, then `GET /api/entries/page?board=` for the
   picked board's newest entries (what it could build on).
2. A link → `POST /api/capture/link` (title, author, picture, date), in the background while you type.
3. Photos/videos → `POST /api/media`, one file at a time. (Notes skip steps 2 and 3.)
4. `POST /api/entries` with the board, your choices and note.
5. If you picked something it builds on: `POST /api/entries/{id}/builds-on`.

The studio: `GET /api/entries` (every entry; the owner token sees private and unlisted ones too) and
`GET /api/boards`, then `PATCH /api/entries/{id}` with only the changed fields, `POST /api/media` for added
pictures, and `DELETE /api/entries/{id}`.

"Made by me" leaves the source name empty, which is how the site already marks the owner's own work.
Entries from the phone are signed `added_by: owner`, because the phone uses the owner token.

## Building it (needs a Mac)

iOS apps can only be built with Xcode, which only runs on macOS. (GitHub Actions also builds it on
a Mac whenever `ios/` changes, `.github/workflows/ios-build.yml`, to catch code that doesn't compile.)

1. Install Xcode (App Store) and XcodeGen: `brew install xcodegen`.
2. In `project.yml`, set `DEVELOPMENT_TEAM` (your Apple team ID) and `BASE_BUNDLE_ID` (e.g. `com.collinwen.openstudio`).
3. In this folder: `xcodegen`. Open `OpenStudio.xcodeproj`.
   Run `xcodegen` again after every pull that adds or removes Swift files: the project lists the files
   that existed when it was made, so a stale one fails with errors like "Cannot find 'StudioMark' in scope".
4. Plug in your iPhone, pick it as the run destination, press Run. The first time, the phone asks you to
   trust the developer (Settings > General > VPN & Device Management) and to turn on Developer Mode.
5. Open the app, enter the server address and owner token, save. It should say `connected · 5 boards: home, …`. Tap **open the studio**.
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
For everyday use, the backend needs to be hosted (with https) somewhere the phone can reach.
