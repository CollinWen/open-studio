/**
 * ShareFormModel: everything the share sheet does, step by step:
 *   1. read what was shared (SharedItems): a link, a note, or photos/videos;
 *      at the same time load the boards, starting on the last one used, and
 *      that board's newest entries (to pick one this builds on)
 *   2. for a link, ask the backend to capture it, in the background;
 *      for a note or photos, fill in the title and text so they can be edited
 *   3. on "save": upload any photos/videos, create the entry on the picked
 *      board, then link it to the entry it builds on
 *
 * ShareForm shows this model; ShareViewController creates it.
 */

import Foundation
import Observation
import UniformTypeIdentifiers

@MainActor @Observable
final class ShareFormModel {
    var choices = ShareChoices()
    /// What's being shared, in a few words: the link's title, or "2 photos".
    private(set) var summary = ""
    /// Who made it, for links: "Collin Wen, YouTube".
    private(set) var sourceLine = ""
    /// A link's picture, once capture has found one.
    private(set) var cover: URL?
    private(set) var boards: [Board] = []
    /// The picked board's newest entries, offered as what this one builds on.
    private(set) var newestEntries: [EntrySummary] = []
    /// Why the boards are missing, if they couldn't be loaded.
    private(set) var boardsProblem: String?
    /// While reading or saving: what's happening. Otherwise what went wrong, if anything.
    private(set) var message: String?
    /// True while `message` says what's being waited for, rather than what went wrong.
    private(set) var isWaiting = true
    private(set) var isSaving = false
    private var hasRead = false

    private var shared: SharedThing = .nothingUsable
    private var capture: Task<CapturedLink?, Never>?
    /// Set once the entry exists, so a retry after a failed "builds on" link doesn't save it twice.
    private var savedEntryId: String?
    private let api = StudioApi(settings: .load())

    private static let newestEntryCount = 8

    var isNote: Bool {
        if case .note = shared { return true }
        return false
    }

    /// Notes and photos get an editable title; a link's comes from capture.
    var hasEditableTitle: Bool {
        if case .link = shared { return false }
        return true
    }

    var pickedBoard: Board? { boards.first { $0.slug == choices.board } }

    var buildsOnTitle: String? {
        newestEntries.first { $0.id == choices.buildsOn }?.title
    }

    /// Saving doesn't wait for a link's capture: save waits for it instead.
    var canSave: Bool { hasRead && !isSaving && shared.isUsable }

    func load(from context: NSExtensionContext?) async {
        guard api.settings.isComplete else {
            isWaiting = false
            summary = "Not set up yet"
            message = "Open the Open Studio app and enter the server address and owner token."
            return
        }
        message = "reading…"
        Task { await loadBoards() }
        shared = await SharedItems.read(from: context)
        hasRead = true
        switch shared {
        case .link(let link, let pageTitle):
            summary = pageTitle ?? link.absoluteString
            sourceLine = link.host() ?? ""
            choices.origin = .inspiration
            message = "reading the link…"
            let api = self.api
            capture = Task { try? await api.captureLink(link) }
            if let captured = await capture?.value {
                summary = captured.title.isEmpty ? summary : captured.title
                sourceLine = captured.sourceName.isEmpty ? sourceLine : captured.sourceName
                cover = captured.media.first.flatMap(Self.pictureURL)
            }
        case .note(let title, let body):
            choices.title = title
            choices.note = body
            choices.origin = .mine
        case .media(let providers, let title, let body):
            summary = Self.describe(providers)
            choices.title = title
            choices.note = body
            choices.origin = .mine
        case .nothingUsable:
            summary = "Nothing to add"
        }
        // Saving may have started while the link was read; its messages win.
        guard !isSaving else { return }
        isWaiting = false
        message = shared.isUsable ? nil : "Open Studio can take a link, a note, photos or videos."
    }

    /// A different board starts with nothing to build on: chains stay within one board.
    func pickBoard(_ slug: String) async {
        guard slug != choices.board else { return }
        choices.board = slug
        choices.buildsOn = nil
        await loadNewestEntries()
    }

    /// Returns true once the entry is saved (and linked), so the share sheet can close.
    func save() async -> Bool {
        isSaving = true
        isWaiting = true
        defer {
            isSaving = false
            isWaiting = false
        }
        do {
            if savedEntryId == nil {
                let saved = try await api.createEntry(try await buildEntry())
                savedEntryId = saved.id
                StudioSettings.rememberBoard(choices.board)
            }
            if let entryId = savedEntryId, let buildsOn = choices.buildsOn {
                message = "linking…"
                do {
                    try await api.addBuildsOn(entryId: entryId, buildsOnId: buildsOn)
                } catch {
                    throw StudioError("Saved, but the builds-on link didn't take: \(error.localizedDescription) Tap save to try the link again.")
                }
            }
            return true
        } catch {
            message = error.localizedDescription
            return false
        }
    }

    // MARK: - Steps

    private func buildEntry() async throws -> NewEntry {
        switch shared {
        case .link(let link, let pageTitle):
            message = "saving, suggesting tags…"
            let captured = await capture?.value
            return EntryBuilder.entryForLink(link, captured: captured, pageTitle: pageTitle, choices: choices)
        case .note:
            message = "saving, suggesting tags…"
            return EntryBuilder.entryForNote(choices: choices)
        case .media(let providers, _, _):
            var uploaded: [UploadedMedia] = []
            for (index, provider) in providers.enumerated() {
                message = "uploading \(index + 1) of \(providers.count)…"
                let prepared = try await PreparedMedia.prepare(provider)
                defer { try? FileManager.default.removeItem(at: prepared.file) }
                let url = try await api.uploadMedia(fileAt: prepared.file)
                let item = MediaItem(type: prepared.isVideo ? "video" : "image", url: url)
                uploaded.append(UploadedMedia(item: item, takenAt: prepared.takenAt))
            }
            message = "saving, suggesting tags…"
            return EntryBuilder.entryForMedia(uploaded, choices: choices)
        case .nothingUsable:
            throw StudioError("Open Studio can take a link, a note, photos or videos.")
        }
    }

    private func loadBoards() async {
        do {
            boards = try await api.fetchBoards()
        } catch {
            // The entry can still go to home; say why the other boards are missing.
            boardsProblem = "Couldn't load the boards, so this goes on home. \(error.localizedDescription)"
            return
        }
        if let last = StudioSettings.lastBoard, boards.contains(where: { $0.slug == last }) {
            choices.board = last
        } else if let first = boards.first {
            choices.board = first.slug
        }
        await loadNewestEntries()
    }

    private func loadNewestEntries() async {
        let board = choices.board
        let entries = (try? await api.fetchNewestEntries(onBoard: board, limit: Self.newestEntryCount)) ?? []
        // The board may have been changed again while these loaded.
        if board == choices.board { newestEntries = entries }
    }

    private static func pictureURL(_ item: MediaItem) -> URL? {
        let picture = item.thumbnailUrl.isEmpty && item.type == "image" ? item.url : item.thumbnailUrl
        return URL(string: picture)
    }

    private static func describe(_ providers: [NSItemProvider]) -> String {
        let videos = providers.filter { $0.hasItemConformingToTypeIdentifier(UTType.movie.identifier) }.count
        let photos = providers.count - videos
        let parts = [
            photos > 0 ? "\(photos) photo\(photos == 1 ? "" : "s")" : nil,
            videos > 0 ? "\(videos) video\(videos == 1 ? "" : "s")" : nil,
        ]
        return parts.compactMap { $0 }.joined(separator: ", ")
    }
}

private extension SharedThing {
    var isUsable: Bool {
        if case .nothingUsable = self { return false }
        return true
    }
}
