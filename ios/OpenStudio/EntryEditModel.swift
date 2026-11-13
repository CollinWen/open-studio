/**
 * EntryEditModel: one entry being edited in the app: a draft of its title,
 * note, board, visibility, tags and pictures, what has changed since it was
 * opened, and saving just those changes (PATCH). New photos and videos are
 * prepared (PreparedMedia) and uploaded as they're picked, each keeping its
 * size, and join the draft's pictures.
 *
 * EntryEditView shows it and reports each save back to the list.
 */

import Foundation
import Observation

@MainActor @Observable
final class EntryEditModel {
    private(set) var saved: StudioEntry
    var title: String
    var note: String
    var board: String
    var visibility: Visibility
    /// The tags as typed: "bread, sourdough".
    var tagsText: String
    var media: [MediaItem]

    private(set) var isSaving = false
    private(set) var isUploading = false
    /// While uploading: what's happening. Otherwise what went wrong, if anything.
    private(set) var message: String?

    private let api: StudioApi

    init(entry: StudioEntry, api: StudioApi) {
        saved = entry
        self.api = api
        title = entry.title
        note = entry.description
        board = entry.board
        visibility = entry.visibility
        tagsText = entry.tags.joined(separator: ", ")
        media = entry.media
    }

    /// Lowercase, trimmed, no empties or repeats, in the order typed.
    var tags: [String] {
        var seen = Set<String>()
        return tagsText.split(separator: ",")
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() }
            .filter { !$0.isEmpty && seen.insert($0).inserted }
    }

    var changes: EntryChanges {
        EntryChanges(
            title: title == saved.title ? nil : title,
            description: note == saved.description ? nil : note,
            media: media == saved.media ? nil : media,
            visibility: visibility == saved.visibility ? nil : visibility,
            tags: tags == saved.tags ? nil : tags,
            board: board == saved.board ? nil : board
        )
    }

    var hasChanges: Bool { !changes.isEmpty }
    var canSave: Bool { hasChanges && !isSaving && !isUploading }

    /// The saved entry, or nil if saving failed (message says why).
    func save() async -> StudioEntry? {
        guard canSave else { return nil }
        isSaving = true
        defer { isSaving = false }
        do {
            let updated = try await api.updateEntry(id: saved.id, changes: changes)
            saved = updated
            tagsText = updated.tags.joined(separator: ", ")
            media = updated.media
            message = nil
            return updated
        } catch {
            message = error.localizedDescription
            return nil
        }
    }

    func discardChanges() {
        title = saved.title
        note = saved.description
        board = saved.board
        visibility = saved.visibility
        tagsText = saved.tags.joined(separator: ", ")
        media = saved.media
        message = nil
    }

    func makeCover(at index: Int) {
        guard media.indices.contains(index) else { return }
        media.insert(media.remove(at: index), at: 0)
    }

    func removeMedia(at index: Int) {
        guard media.indices.contains(index) else { return }
        media.remove(at: index)
    }

    /// Uploads each picked photo or video in turn; ones already uploaded stay if a later one fails.
    func addMedia(from providers: [NSItemProvider]) async {
        guard !providers.isEmpty else { return }
        isUploading = true
        defer { isUploading = false }
        do {
            for (index, provider) in providers.enumerated() {
                message = "preparing \(index + 1) of \(providers.count)…"
                let prepared = try await PreparedMedia.prepare(provider)
                defer { try? FileManager.default.removeItem(at: prepared.file) }
                let size = ByteCountFormatter.string(fromByteCount: Int64(prepared.sizeBytes), countStyle: .file)
                message = "uploading \(index + 1) of \(providers.count) · \(size)…"
                let url = try await api.uploadMedia(fileAt: prepared.file)
                media.append(MediaItem(type: prepared.isVideo ? "video" : "image", url: url, sizeBytes: prepared.sizeBytes))
            }
            message = nil
        } catch {
            message = "Upload stopped: \(error.localizedDescription)"
        }
    }
}
