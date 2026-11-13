/**
 * EntryShapes: the data sent to and received from the backend, matching
 * backend/app/features/entries/schemas.py, boards/schemas.py,
 * entry_links/schemas.py and capture/schemas.py.
 *
 * Field names are camelCase here; StudioApi converts them to the backend's
 * snake_case (sourceUrl <-> source_url).
 */

import Foundation

/// One picture or video in an entry. type is "image", "video" or "embed".
struct MediaItem: Codable, Equatable {
    var type: String
    var url: String
    var thumbnailUrl: String = ""
    var caption: String = ""
    /// An uploaded file's size, shown on the entry page; 0 when unknown.
    var sizeBytes: Int = 0
}

/// What POST /api/capture/link returns: suggested values for a new entry from a link.
struct CapturedLink: Decodable {
    var sourceUrl: String
    var title: String
    var description: String
    var kind: String
    var sourceName: String
    /// Passed back to the backend as-is, so it's never reinterpreted on the phone.
    var occurredAt: String?
    var media: [MediaItem]
}

/// The body of POST /api/entries. Tags are left empty so the backend suggests them.
struct NewEntry: Encodable {
    var title: String
    var description: String
    var kind: String
    var sourceName: String
    var sourceUrl: String
    var media: [MediaItem]
    /// ISO 8601. Left out (nil) means "now".
    var occurredAt: String?
    var visibility: Visibility
    /// The board's slug; every entry is on one board.
    var board: String
    var tags: [String] = []
}

enum Visibility: String, Codable, CaseIterable {
    case `private`, unlisted, `public`
}

/// One board from GET /api/boards: a separate space, and the agents signed on to it.
struct Board: Decodable, Identifiable {
    var slug: String
    var name: String
    var description: String
    var agents: [String]

    var id: String { slug }
}

/// The few fields of an entry the phone needs: to link to it, or offer it as one to build on.
struct EntrySummary: Decodable, Identifiable {
    var id: String
    var title: String
    var occurredAt: String
}

/// What GET /api/entries/page returns.
struct EntrySummaryPage: Decodable {
    var entries: [EntrySummary]
}

/// A whole entry, as GET /api/entries returns it: what the app's studio lists and edits.
struct StudioEntry: Decodable, Identifiable, Equatable {
    var id: String
    var title: String
    var description: String
    var kind: String
    var sourceName: String
    var sourceUrl: String
    var media: [MediaItem]
    /// ISO 8601, e.g. "2026-11-11T09:30:00Z"; its first ten characters are the date.
    var occurredAt: String
    var visibility: Visibility
    var tags: [String]
    /// "owner" or "agent:<name>".
    var addedBy: String
    var board: String
}

/// The body of PATCH /api/entries/{id}: only the fields that are set are changed.
struct EntryChanges: Encodable {
    var title: String?
    var description: String?
    var media: [MediaItem]?
    var visibility: Visibility?
    var tags: [String]?
    var board: String?

    var isEmpty: Bool {
        title == nil && description == nil && media == nil && visibility == nil && tags == nil && board == nil
    }
}

/// The body of POST /api/entries/{id}/builds-on.
struct BuildsOn: Encodable {
    var buildsOnId: String
    var note: String = ""
}
