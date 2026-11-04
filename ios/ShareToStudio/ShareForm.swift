/**
 * ShareForm: what you see after choosing "Open Studio" in the share sheet,
 * built the same way as a page on the site: the site name with cancel and
 * save, a double rule, what's being added (its picture and title), the board
 * it goes on as a section line (with the agents signed on to it), one shaded
 * control band (made by me / inspiration, private / unlisted / public, and
 * "builds on" behind the caret), then a note on why it's here.
 * Notes and photos show an editable title instead of a fixed one.
 *
 * The look comes from StudioStyle; the work is in ShareFormModel.
 */

import SwiftUI

struct ShareForm: View {
    @Bindable var model: ShareFormModel
    let onSaved: () -> Void
    let onCancel: () -> Void

    @State private var showBuildsOn = false
    @FocusState private var focused: Field?
    private enum Field { case title, note }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                header
                adding
                space
                controls
                note
                if let message = model.message {
                    LabelRow {
                        if model.isWaiting { LoadingWord(text: message) } else {
                            Text(message).foregroundStyle(StudioStyle.inkSoft)
                        }
                    }
                    .padding(.top, StudioStyle.line)
                }
            }
            .padding(.bottom, 2 * StudioStyle.line)
        }
        .scrollDismissesKeyboard(.interactively)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .studioPage()
    }

    private var header: some View {
        LabelRow {
            HStack(alignment: .firstTextBaseline, spacing: StudioStyle.wordGap) {
                Text("Open Studio").font(StudioStyle.siteNameFont)
                Spacer()
                Button("cancel", action: onCancel).foregroundStyle(StudioStyle.inkSoft)
                Button("save") {
                    focused = nil
                    Task { if await model.save() { onSaved() } }
                }
                .foregroundStyle(model.canSave ? StudioStyle.ink : StudioStyle.inkSoft)
                .disabled(!model.canSave)
            }
        }
        .padding(.top, StudioStyle.line)
    }

    private var adding: some View {
        LabelRow(label: "Adding", rule: .double) {
            if let cover = model.cover {
                AsyncImage(url: cover, transaction: Transaction(animation: StudioStyle.arrive)) { phase in
                    if let image = phase.image {
                        image.resizable().scaledToFit().transition(.opacity)
                    }
                }
                .frame(maxWidth: .infinity, maxHeight: 220, alignment: .leading)
            }
            if model.hasEditableTitle {
                TextField("title", text: $model.choices.title, axis: .vertical)
                    .font(StudioStyle.titleFont)
                    .focused($focused, equals: .title)
                    .ruledField(isFocused: focused == .title)
            } else {
                Text(model.summary).font(StudioStyle.titleFont).lineLimit(3)
            }
            let detail = model.hasEditableTitle ? model.summary : model.sourceLine
            if !detail.isEmpty {
                Text(detail).foregroundStyle(StudioStyle.inkSoft)
            }
        }
    }

    private var space: some View {
        SectionLine(
            label: "Space",
            sections: model.boards.map { SectionWord(id: $0.slug, label: $0.name.lowercased()) },
            current: model.choices.board,
            onPick: { slug in Task { await model.pickBoard(slug) } }
        ) {
            if let problem = model.boardsProblem {
                Text(problem).foregroundStyle(StudioStyle.inkSoft)
            } else if model.boards.isEmpty {
                LoadingWord(text: "loading boards")
            } else if let agents = model.pickedBoard?.agents, !agents.isEmpty {
                Text("with " + agents.joined(separator: ", ")).foregroundStyle(StudioStyle.inkSoft)
            }
        }
        .padding(.bottom, StudioStyle.line / 2)
    }

    private var controls: some View {
        ControlBand(moreLabel: "builds on", picks: model.buildsOnTitle ?? "nothing", isOpen: $showBuildsOn) {
            WordChoice(options: Origin.allCases, selected: $model.choices.origin, label: \.label)
            WordChoice(options: Visibility.allCases, selected: $model.choices.visibility, label: \.rawValue)
        } more: {
            buildsOnList
        }
    }

    /// The board's newest entries; tap one to say this builds on it, tap again to undo.
    private var buildsOnList: some View {
        VStack(alignment: .leading, spacing: StudioStyle.leading) {
            if model.newestEntries.isEmpty {
                Text("nothing on this board yet").foregroundStyle(StudioStyle.inkSoft)
            }
            ForEach(model.newestEntries) { entry in
                let isPicked = entry.id == model.choices.buildsOn
                Button {
                    model.choices.buildsOn = isPicked ? nil : entry.id
                } label: {
                    HStack(alignment: .firstTextBaseline) {
                        Text(entry.title).lineLimit(1).underline(isPicked, color: StudioStyle.accent)
                        Spacer(minLength: StudioStyle.wordGap)
                        Text(entry.occurredAt.prefix(7)).font(StudioStyle.smallFont)
                    }
                    .contentShape(Rectangle())
                }
                .foregroundStyle(isPicked ? StudioStyle.ink : StudioStyle.inkSoft)
                .accessibilityAddTraits(isPicked ? .isSelected : [])
            }
        }
        .animation(StudioStyle.quick, value: model.choices.buildsOn)
    }

    private var note: some View {
        LabelRow(label: model.isNote ? "The note" : "Why it's here", rule: .single) {
            TextField("", text: $model.choices.note, axis: .vertical)
                .lineLimit(3...(model.isNote ? 16 : 10))
                .focused($focused, equals: .note)
                .accessibilityLabel(model.isNote ? "the note" : "why it's here")
                .ruledField(isFocused: focused == .note)
        }
    }
}
