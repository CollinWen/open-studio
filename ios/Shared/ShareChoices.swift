/**
 * ShareChoices: what's asked in the share sheet: which board it goes on, who
 * made it, who can see it, what it builds on, and a note on why it's here.
 * For shared notes and photos, also a title.
 *
 * Filled in by ShareForm, turned into an entry by EntryBuilder.
 */

/// Not stored as its own field: "made by me" means the entry has no source
/// name, which is how the site already marks the owner's own work.
enum Origin: CaseIterable {
    case mine, inspiration

    var label: String { self == .mine ? "made by me" : "inspiration" }
}

struct ShareChoices {
    /// A board's slug. Starts on the board the last entry went to.
    var board = "home"
    var origin: Origin = .inspiration
    var visibility: Visibility = .private
    /// The id of an earlier entry on the same board this one builds on, if any.
    var buildsOn: String?
    var note = ""
    /// For shared notes and photos, where it starts as the text's first line. Links take their title from capture.
    var title = ""
}
