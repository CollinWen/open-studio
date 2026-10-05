/**
 * ShareFormModel: everything the share sheet does, step by step:
 *   1. read what was shared (SharedItems): a link, a note, or photos/videos
 *   2. for a link, ask the backend to capture it, in the background;
 *      for a note, fill in its title and text so they can be edited
 *   3. on "save": upload any photos/videos, then create the entry
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
    private(set) var summary = "reading…"
    /// Who made it, for links: "Collin Wen, YouTube".
    private(set) var sourceLine = ""
    /// Progress while saving, or what went wrong.
    private(set) var message: String?
    private(set) var isSaving = false

    private var shared: SharedThing = .nothingUsable

    /// Notes get an editable title instead of a fixed summary line.
    var isNote: Bool {
        if case .note = shared { return true }
        return false
    }
    private var capture: Task<CapturedLink?, Never>?
    private let api = StudioApi(settings: .load())

    var canSave: Bool {
        if isSaving { return false }
        if case .nothingUsable = shared { return false }
        return true
    }

    func load(from context: NSExtensionContext?) async {
        guard api.settings.isComplete else {
            summary = "Not set up yet"
            message = "Open the Open Studio app and enter the server address and owner token."
            return
        }
        shared = await SharedItems.read(from: context)
        switch shared {
        case .link(let link, let pageTitle):
            summary = pageTitle ?? link.absoluteString
            sourceLine = link.host() ?? ""
            choices.origin = .inspiration
            let api = self.api
            capture = Task { try? await api.captureLink(link) }
            if let captured = await capture?.value {
                summary = captured.title.isEmpty ? summary : captured.title
                sourceLine = captured.sourceName.isEmpty ? sourceLine : captured.sourceName
            }
        case .note(let title, let body):
            choices.title = title
            choices.note = body
            choices.origin = .mine
        case .media(let providers):
            summary = Self.describe(providers)
            choices.origin = .mine
        case .nothingUsable:
            summary = "Nothing to add"
            message = "Open Studio can take a link, a note, photos or videos."
        }
    }

    /// Returns true once the entry is saved, so the share sheet can close.
    func save() async -> Bool {
        isSaving = true
        defer { isSaving = false }
        do {
            switch shared {
            case .link(let link, let pageTitle):
                message = "saving…"
                let captured = await capture?.value
                try await api.createEntry(
                    EntryBuilder.entryForLink(link, captured: captured, pageTitle: pageTitle, choices: choices))
            case .note:
                message = "saving…"
                try await api.createEntry(EntryBuilder.entryForNote(choices: choices))
            case .media(let providers):
                var uploaded: [UploadedMedia] = []
                for (index, provider) in providers.enumerated() {
                    message = "uploading \(index + 1) of \(providers.count)…"
                    let prepared = try await PreparedMedia.prepare(provider)
                    defer { try? FileManager.default.removeItem(at: prepared.file) }
                    let url = try await api.uploadMedia(fileAt: prepared.file)
                    let item = MediaItem(type: prepared.isVideo ? "video" : "image", url: url)
                    uploaded.append(UploadedMedia(item: item, takenAt: prepared.takenAt))
                }
                message = "saving…"
                try await api.createEntry(EntryBuilder.entryForMedia(uploaded, choices: choices))
            case .nothingUsable:
                return false
            }
            return true
        } catch {
            message = error.localizedDescription
            return false
        }
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
