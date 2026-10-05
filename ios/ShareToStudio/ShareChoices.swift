/**
 * ShareChoices: what's asked in the share sheet: who made it, who can see it,
 * and a note on why it's here. For a shared note, also its title.
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
    var origin: Origin = .inspiration
    var visibility: Visibility = .private
    var note = ""
    /// Only used for shared notes, where it starts as the note's first line.
    var title = ""
}
