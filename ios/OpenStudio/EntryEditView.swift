/**
 * EntryEditView: one entry in the app, to change and publish. Laid out like
 * the add form: its cover large, then the title, the board it's on (a section
 * line), who sees it (the shaded band: private · unlisted · everyone), why
 * it's here, its tags, its pictures (MediaEditor), where it came from, and
 * "delete this entry" at the end.
 *
 * Nothing is saved until "save". While something is changed, the back button
 * gives way to "cancel" (which asks before throwing changes away), so swiping
 * back can't lose them. The work is in EntryEditModel.
 */

import SwiftUI

struct EntryEditView: View {
    let boards: [Board]
    let api: StudioApi
    let onSaved: (StudioEntry) -> Void
    let onDelete: () async -> Void

    @State private var model: EntryEditModel
    @State private var isConfirmingDiscard = false
    @State private var isConfirmingDelete = false
    @State private var savedCount = 0
    @FocusState private var focused: Field?
    @Environment(\.dismiss) private var dismiss
    private enum Field { case title, note, tags }

    init(
        entry: StudioEntry, boards: [Board], api: StudioApi,
        onSaved: @escaping (StudioEntry) -> Void, onDelete: @escaping () async -> Void
    ) {
        self.boards = boards
        self.api = api
        self.onSaved = onSaved
        self.onDelete = onDelete
        _model = State(initialValue: EntryEditModel(entry: entry, api: api))
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                cover
                titleRow
                boardLine
                ControlBand {
                    WordChoice(options: Visibility.allCases, selected: $model.visibility, label: EntryListView.audience)
                }
                noteRow
                tagsRow
                LabelRow(label: "Pictures", rule: .single) { MediaEditor(model: model, api: api) }
                sourceRow
                deleteRow
            }
            .padding(.bottom, 2 * StudioStyle.line)
        }
        .scrollDismissesKeyboard(.interactively)
        .studioPage()
        .navigationTitle("")
        .navigationBarTitleDisplayMode(.inline)
        .toolbarBackground(StudioStyle.paper, for: .navigationBar)
        .navigationBarBackButtonHidden(model.hasChanges)
        .toolbar { toolbarWords }
        .sensoryFeedback(.success, trigger: savedCount)
        .confirmationDialog("Throw away your changes?", isPresented: $isConfirmingDiscard, titleVisibility: .visible) {
            Button("Throw away changes", role: .destructive) {
                model.discardChanges()
                dismiss()
            }
            Button("Keep editing", role: .cancel) {}
        }
        .confirmationDialog(
            "Delete “\(model.saved.title)”?", isPresented: $isConfirmingDelete, titleVisibility: .visible
        ) {
            Button("Delete", role: .destructive) {
                Task {
                    await onDelete()
                    dismiss()
                }
            }
        } message: {
            Text("It's removed from the studio for good.")
        }
    }

    @ToolbarContentBuilder private var toolbarWords: some ToolbarContent {
        ToolbarItem(placement: .topBarLeading) {
            if model.hasChanges {
                Button("cancel") { isConfirmingDiscard = true }
                    .font(StudioStyle.bodyFont)
                    .foregroundStyle(StudioStyle.inkSoft)
            }
        }
        ToolbarItem(placement: .topBarTrailing) {
            if model.isSaving {
                LoadingWord(text: "saving")
            } else {
                Button("save") {
                    focused = nil
                    Task {
                        if let updated = await model.save() {
                            onSaved(updated)
                            savedCount += 1
                        }
                    }
                }
                .font(StudioStyle.bodyFont)
                .foregroundStyle(model.canSave ? StudioStyle.ink : StudioStyle.inkFaint)
                .disabled(!model.canSave)
            }
        }
    }

    @ViewBuilder private var cover: some View {
        if let picture = model.media.first.flatMap({ api.pictureURL(of: $0) }) {
            AsyncImage(url: picture, transaction: Transaction(animation: StudioStyle.arrive)) { phase in
                if let image = phase.image {
                    image.resizable().scaledToFit().transition(.opacity)
                } else {
                    StudioStyle.paperShade.frame(height: 12 * StudioStyle.line)
                }
            }
            .frame(maxWidth: .infinity, maxHeight: 16 * StudioStyle.line)
            .accessibilityHidden(true)
        }
    }

    private var titleRow: some View {
        LabelRow(label: facts, rule: .double) {
            TextField("title", text: $model.title, axis: .vertical)
                .font(StudioStyle.titleFont)
                .focused($focused, equals: .title)
                .ruledField(isFocused: focused == .title)
            if let message = model.message, !model.isUploading {
                Text(message).foregroundStyle(StudioStyle.accent)
            }
        }
    }

    /// Kind · date · who added it, the entry page's facts in one quiet line.
    private var facts: String {
        var parts = [model.saved.kind, String(model.saved.occurredAt.prefix(10))]
        if model.saved.addedBy.hasPrefix("agent:") {
            parts.append("by \(model.saved.addedBy.dropFirst("agent:".count))")
        }
        return parts.joined(separator: " · ")
    }

    private var boardLine: some View {
        SectionLine(
            label: "Board",
            sections: boards.map { SectionWord(id: $0.slug, label: $0.name.lowercased()) },
            current: model.board,
            onPick: { model.board = $0 }
        ) {
            EmptyView()
        }
        .padding(.bottom, StudioStyle.line / 2)
    }

    private var noteRow: some View {
        LabelRow(label: "Why it's here", rule: .none) {
            TextField("", text: $model.note, axis: .vertical)
                .lineLimit(3...14)
                .focused($focused, equals: .note)
                .accessibilityLabel("why it's here")
                .ruledField(isFocused: focused == .note)
        }
        .padding(.top, StudioStyle.line)
    }

    private var tagsRow: some View {
        LabelRow(label: "Tags, separated by commas", rule: .none) {
            TextField("", text: $model.tagsText, axis: .vertical)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
                .focused($focused, equals: .tags)
                .accessibilityLabel("tags")
                .ruledField(isFocused: focused == .tags)
        }
        .padding(.top, StudioStyle.line)
    }

    @ViewBuilder private var sourceRow: some View {
        if let link = URL(string: model.saved.sourceUrl), link.scheme?.hasPrefix("http") == true {
            LabelRow(label: "Source", rule: .single) {
                Link(destination: link) {
                    Text(model.saved.sourceName.isEmpty ? (link.host() ?? link.absoluteString) : model.saved.sourceName)
                        .underline(color: StudioStyle.inkFaint)
                }
            }
        }
    }

    private var deleteRow: some View {
        LabelRow(rule: .single) {
            Button("delete this entry") { isConfirmingDelete = true }
                .foregroundStyle(StudioStyle.inkSoft)
                .disabled(model.isSaving || model.isUploading)
        }
    }
}
