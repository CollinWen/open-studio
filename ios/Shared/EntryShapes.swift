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
struct MediaItem: Codable {
    var type: String
    var url: String
    var thumbnailUrl: String = ""
    var caption: String = ""
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

/// The body of POST /api/entries/{id}/builds-on.
struct BuildsOn: Encodable {
    var buildsOnId: String
    var note: String = ""
}
