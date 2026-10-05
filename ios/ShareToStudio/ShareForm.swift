/**
 * ShareForm: what you see after choosing "Open Studio" in the share sheet.
 * What's being added, then three quick choices: made by me / inspiration,
 * private / unlisted / public, and a note on why it's here. Then "save".
 * A shared note shows its title and text instead, both editable.
 *
 * Same look as the site: plain words, black on white, no buttons or boxes.
 */

import SwiftUI

struct ShareForm: View {
    @Bindable var model: ShareFormModel
    let onSaved: () -> Void
    let onCancel: () -> Void
    @FocusState private var writingNote: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            HStack {
                Button("cancel", action: onCancel)
                Spacer()
                Button("save") {
                    Task { if await model.save() { onSaved() } }
                }
                .fontWeight(.semibold)
                .disabled(!model.canSave)
            }

            VStack(alignment: .leading, spacing: 4) {
                if model.isNote {
                    TextField("title", text: $model.choices.title).font(.headline)
                } else {
                    Text(model.summary).font(.headline).lineLimit(3)
                }
                if !model.sourceLine.isEmpty {
                    Text(model.sourceLine).foregroundStyle(.gray)
                }
            }

            WordChoice(options: Origin.allCases, selected: $model.choices.origin, label: \.label)
            WordChoice(options: Visibility.allCases, selected: $model.choices.visibility, label: \.rawValue)

            TextField(model.isNote ? "the note" : "why it's here", text: $model.choices.note, axis: .vertical)
                .lineLimit(3...(model.isNote ? 16 : 10))
                .focused($writingNote)

            if let message = model.message {
                Text(message).foregroundStyle(.gray)
            }
            Spacer()
        }
        .padding(20)
        .buttonStyle(.plain)
        .foregroundStyle(.black)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .background(Color.white)
        .preferredColorScheme(.light)
        .onAppear { writingNote = true }
    }
}
