# iOS

Adds "Open Studio" to the iPhone share sheet. Share a post from Instagram, X or
YouTube (or any link), a note from Notes, or photos and videos from Photos. Choose **made by me** or
**inspiration**, pick **private / unlisted / public**, write a line on why it's here,
and tap **save**. The entry goes straight to the site; tags are suggested as usual.

A shared note arrives with its first line as the title and the rest as the text, both editable
before saving. It's saved as kind `note`. (In Notes: share > **Send a Copy** > Open Studio.)

iOS only allows share-sheet extensions inside an app, so there's a tiny app too.
You open it once to enter the server address and owner token.

## What's where

| Path | What it does |
|---|---|
| `project.yml` | Describes the Xcode project (targets, bundle IDs, share-sheet rules). Edit this, not the generated `.xcodeproj`. |
| `OpenStudio/` | The app: `OpenStudioApp.swift` starts it, `SetupView.swift` is its one screen (server address + owner token). |
| `ShareToStudio/` | The share extension. `ShareViewController` is the entry point, `ShareForm` is what you see, `ShareFormModel` does the work: `SharedItems` reads what was shared (link, note, or photos), `PreparedMedia` + `PhotoDate` get photos/videos ready to upload, `EntryBuilder` turns it all into an entry. `WordChoice` is the tap-a-word picker; `ShareChoices` holds the three answers. |
| `Shared/` | Used by both: `StudioApi` (every call to the backend), `EntryShapes` (data shapes matching the backend), `StudioSettings` + `SharedKeychain` (where the address and token are kept), `MultipartBody` (file upload format). |

## How it uses the backend

No new endpoints. The phone calls the same API as the `/studio` page:

1. A link → `POST /api/capture/link` (title, author, picture, date), in the background while you type.
2. Photos/videos → `POST /api/media`, one file at a time. (Notes skip steps 1 and 2.)
3. `POST /api/entries` with your choices and note.

"Made by me" leaves the source name empty, which is how the site already marks the owner's own work.

## Building it (needs a Mac)

iOS apps can only be built with Xcode, which only runs on macOS.

1. Install Xcode (App Store) and XcodeGen: `brew install xcodegen`.
2. In `project.yml`, set `DEVELOPMENT_TEAM` (your Apple team ID) and `BASE_BUNDLE_ID` (e.g. `com.collinwen.openstudio`).
3. In this folder: `xcodegen`. Open `OpenStudio.xcodeproj`.
4. Plug in your iPhone, pick it as the run destination, press Run. The first time, the phone asks you to
   trust the developer (Settings > General > VPN & Device Management) and to turn on Developer Mode.
5. Open the app, enter the server address and owner token, save.
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
