/**
 * EntryBuilder: turns what was shared, plus the owner's choices, into the
 * new entry sent to the backend. No network calls here; ShareFormModel does those.
 *
 *   A link:   title, source, pictures and date come from capture (the backend's
 *             link readers). If capture failed, the link itself is enough.
 *   A note:   kind "note", titled with its first line; the rest is the description.
 *   Photos:   one entry holding every photo/video, dated when the first was taken.
 *
 * What's typed in the sheet becomes the description ("why it's here"). Tags are left to the backend.
 */

import Foundation

struct UploadedMedia {
    let item: MediaItem
    let takenAt: Date?
}

enum EntryBuilder {
    static func entryForLink(
        _ link: URL, captured: CapturedLink?, pageTitle: String?, choices: ShareChoices
    ) -> NewEntry {
        let siteName = link.host()?.replacingOccurrences(of: "www.", with: "") ?? ""
        return NewEntry(
            title: firstFilled(captured?.title, pageTitle, siteName, link.absoluteString),
            description: firstFilled(choices.note, captured?.description),
            kind: captured?.kind ?? "link",
            sourceName: choices.origin == .mine ? "" : firstFilled(captured?.sourceName, siteName),
            sourceUrl: captured?.sourceUrl ?? link.absoluteString,
            media: captured?.media ?? [],
            occurredAt: captured?.occurredAt,
            visibility: choices.visibility
        )
    }

    /// The note's text arrives in choices.note (the sheet shows it for editing).
    static func entryForNote(choices: ShareChoices) -> NewEntry {
        let body = choices.note.trimmingCharacters(in: .whitespacesAndNewlines)
        return NewEntry(
            title: firstFilled(choices.title, Date.now.formatted(date: .long, time: .omitted)),
            description: body,
            kind: "note",
            sourceName: "",
            sourceUrl: "",
            media: [],
            occurredAt: nil,
            visibility: choices.visibility
        )
    }

    static func entryForMedia(_ uploaded: [UploadedMedia], choices: ShareChoices) -> NewEntry {
        let takenAt = uploaded.compactMap(\.takenAt).min()
        let onlyVideos = uploaded.allSatisfy { $0.item.type == "video" }
        return NewEntry(
            // Photos have no title of their own; the date stands in until one is written on /studio.
            title: (takenAt ?? .now).formatted(date: .long, time: .omitted),
            description: choices.note.trimmingCharacters(in: .whitespacesAndNewlines),
            kind: onlyVideos ? "video" : "photo",
            sourceName: "",
            sourceUrl: "",
            media: uploaded.map(\.item),
            occurredAt: takenAt.map { ISO8601DateFormatter().string(from: $0) },
            visibility: choices.visibility
        )
    }

    private static func firstFilled(_ candidates: String?...) -> String {
        candidates
            .compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }
            .first { !$0.isEmpty } ?? ""
    }
}
