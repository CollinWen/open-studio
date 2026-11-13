/**
 * EntryListModel: what the app's studio knows: every entry (newest first)
 * and the boards, loaded from the backend, and which of them are showing
 * after the board, who-sees-it and search picks. Deleting an entry, and
 * taking in one that was just edited, happen here too.
 *
 * EntryListView shows it; EntryEditView reports its saves and deletes back.
 */

import Foundation
import Observation

@MainActor @Observable
final class EntryListModel {
    private(set) var entries: [StudioEntry] = []
    private(set) var boards: [Board] = []
    private(set) var isLoading = false
    /// What went wrong with the last load or delete, if anything.
    private(set) var problem: String?

    /// A board's slug, or `allBoards`.
    var board = EntryListModel.allBoards
    /// nil shows every entry.
    var visibility: Visibility?
    var query = ""

    static let allBoards = "all"
    let api = StudioApi(settings: .load())

    /// The entries the picks leave, newest first.
    var showing: [StudioEntry] {
        let words = query.lowercased().split(separator: " ").map(String.init)
        return entries.filter { entry in
            (board == Self.allBoards || entry.board == board)
                && (visibility == nil || entry.visibility == visibility)
                && words.allSatisfy { word in Self.searchText(of: entry).contains(word) }
        }
    }

    func count(onBoard slug: String) -> Int {
        slug == Self.allBoards ? entries.count : entries.filter { $0.board == slug }.count
    }

    func boardName(_ slug: String) -> String {
        boards.first { $0.slug == slug }?.name.lowercased() ?? slug
    }

    func load() async {
        isLoading = true
        defer { isLoading = false }
        do {
            async let loadedEntries = api.fetchEntries()
            async let loadedBoards = api.fetchBoards()
            entries = try await loadedEntries.sorted { $0.occurredAt > $1.occurredAt }
            boards = try await loadedBoards
            problem = nil
        } catch {
            problem = error.localizedDescription
        }
    }

    func delete(_ entry: StudioEntry) async {
        do {
            try await api.deleteEntry(id: entry.id)
            entries.removeAll { $0.id == entry.id }
            problem = nil
        } catch {
            problem = "Couldn't delete “\(entry.title)”. \(error.localizedDescription)"
        }
    }

    /// An entry saved on its own screen: show the new version straight away.
    func replace(_ entry: StudioEntry) {
        guard let index = entries.firstIndex(where: { $0.id == entry.id }) else { return }
        entries[index] = entry
        entries.sort { $0.occurredAt > $1.occurredAt }
    }

    func entry(withId id: String) -> StudioEntry? {
        entries.first { $0.id == id }
    }

    private static func searchText(of entry: StudioEntry) -> String {
        ([entry.title, entry.description, entry.sourceName] + entry.tags).joined(separator: " ").lowercased()
    }
}
