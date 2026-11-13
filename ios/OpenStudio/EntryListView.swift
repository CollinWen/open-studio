/**
 * EntryListView: the app's studio, built like the site's studio page for a
 * phone: the site name with a plus (add) and "setup", then the boards as a
 * section line (each with its count), one shaded control band (search, and
 * who sees it behind the caret), then your entries, newest first (EntryRow).
 *
 * Tap an entry to edit it (EntryEditView); swipe it left to delete; pull down
 * to reload. The plus opens the add form (AddEntryView) as a sheet.
 */

import SwiftUI

struct EntryListView: View {
    let openSetup: () -> Void
    @State private var model = EntryListModel()
    @State private var path: [String] = []
    @State private var isAdding = false
    @State private var isFilterOpen = false
    @State private var pendingDelete: StudioEntry?
    /// Counts saves and deletes, for the haptic tap that confirms each.
    @State private var changedCount = 0
    @FocusState private var isSearching: Bool

    var body: some View {
        NavigationStack(path: $path) {
            List {
                Group {
                    header
                    boardLine
                    band
                    stateLine
                }
                .plainListRow()

                ForEach(model.showing) { entry in
                    Button { path.append(entry.id) } label: {
                        EntryRow(entry: entry, boardName: model.boardName(entry.board), api: model.api)
                    }
                    .plainListRow()
                    .swipeActions(edge: .trailing) {
                        Button("delete") { pendingDelete = entry }.tint(StudioStyle.accent)
                    }
                }
            }
            .listStyle(.plain)
            .scrollContentBackground(.hidden)
            .scrollDismissesKeyboard(.immediately)
            .environment(\.defaultMinListRowHeight, 0)
            .animation(StudioStyle.arrive, value: model.showing)
            .refreshable { await model.load() }
            .studioPage()
            .navigationTitle("entries")
            .toolbar(.hidden, for: .navigationBar)
            .navigationDestination(for: String.self) { id in
                if let entry = model.entry(withId: id) {
                    EntryEditView(
                        entry: entry,
                        boards: model.boards,
                        api: model.api,
                        onSaved: { model.replace($0) },
                        onDelete: { await model.delete(entry) }
                    )
                }
            }
        }
        .task { await model.load() }
        .sheet(isPresented: $isAdding, onDismiss: { Task { await model.load() } }) {
            AddEntryView(onDone: { saved in
                isAdding = false
                if saved { changedCount += 1 }
            })
        }
        .confirmationDialog(
            "Delete “\(pendingDelete?.title ?? "")”?",
            isPresented: Binding(get: { pendingDelete != nil }, set: { if !$0 { pendingDelete = nil } }),
            titleVisibility: .visible,
            presenting: pendingDelete
        ) { entry in
            Button("Delete", role: .destructive) {
                Task {
                    await model.delete(entry)
                    changedCount += 1
                }
            }
        } message: { _ in
            Text("It's removed from the studio for good.")
        }
        .sensoryFeedback(.success, trigger: changedCount)
    }

    private var header: some View {
        LabelRow {
            HStack(alignment: .center, spacing: StudioStyle.wordGap) {
                Text("Open Studio").font(StudioStyle.siteNameFont)
                Spacer()
                Button("setup", action: openSetup).foregroundStyle(StudioStyle.inkSoft)
                Button { isAdding = true } label: { PlusIcon() }
            }
        }
        .padding(.top, StudioStyle.line / 2)
    }

    private var boardLine: some View {
        let words = [SectionWord(id: EntryListModel.allBoards, label: "all \(model.count(onBoard: EntryListModel.allBoards))")]
            + model.boards.map { SectionWord(id: $0.slug, label: "\($0.name.lowercased()) \(model.count(onBoard: $0.slug))") }
        return SectionLine(label: "", rule: .double, sections: words, current: model.board, onPick: { model.board = $0 }) {
            EmptyView()
        }
        .padding(.bottom, StudioStyle.line / 2)
    }

    private var band: some View {
        ControlBand(moreLabel: "who sees it", picks: model.visibility.map(Self.audience) ?? "", isOpen: $isFilterOpen) {
            TextField("search titles, notes and tags", text: $model.query)
                .focused($isSearching)
                .submitLabel(.search)
                .autocorrectionDisabled()
                .textInputAutocapitalization(.never)
                .ruledField(isFocused: isSearching)
        } more: {
            WordChoice(
                options: [nil] + Visibility.allCases.map { Optional($0) },
                selected: $model.visibility,
                label: { $0.map(Self.audience) ?? "all" }
            )
        }
    }

    /// Loading, a problem, or nothing to show: one quiet line under the band.
    @ViewBuilder private var stateLine: some View {
        if let problem = model.problem {
            LabelRow { Text(problem).foregroundStyle(StudioStyle.inkSoft) }
                .padding(.vertical, StudioStyle.line / 2)
        } else if model.isLoading && model.entries.isEmpty {
            LabelRow { LoadingWord(text: "loading entries") }
                .padding(.vertical, StudioStyle.line / 2)
        } else if model.showing.isEmpty {
            LabelRow {
                Text(model.entries.isEmpty ? "Nothing here yet. The plus adds an entry." : "No entries match.")
                    .foregroundStyle(StudioStyle.inkSoft)
            }
            .padding(.vertical, StudioStyle.line / 2)
        }
    }

    /// The site's words for who sees an entry.
    static func audience(_ visibility: Visibility) -> String {
        visibility == .public ? "everyone" : visibility.rawValue
    }
}

extension View {
    /// A list row with no system insets, separator or background: the page draws its own.
    func plainListRow() -> some View {
        self
            .listRowInsets(EdgeInsets())
            .listRowSeparator(.hidden)
            .listRowBackground(Color.clear)
    }
}
