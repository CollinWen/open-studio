/**
 * AddEntryView: what the plus in the app's studio opens, as a sheet. First
 * what you're adding: a link (paste it, then go), photos or videos (the
 * phone's picker), or a note. Then the same add form as the share sheet
 * (ShareForm: board, made by me / inspiration, who sees it, builds on, why
 * it's here), so adding works one way wherever you start.
 *
 * Shown by EntryListView, which reloads its list when the sheet closes.
 */

import SwiftUI

struct AddEntryView: View {
    /// Closes the sheet; true when an entry was saved.
    let onDone: (Bool) -> Void
    @State private var form: ShareFormModel?
    @State private var linkText = ""
    @State private var isPicking = false
    @FocusState private var isTypingLink: Bool

    var body: some View {
        Group {
            if let form {
                ShareForm(
                    model: form,
                    onSaved: { onDone(true) },
                    onCancel: { onDone(false) }
                )
                .transition(.opacity)
            } else {
                choosing.transition(.opacity)
            }
        }
        .animation(StudioStyle.arrive, value: form == nil)
        .sheet(isPresented: $isPicking) {
            PhotoPicker { picked in
                isPicking = false
                if !picked.isEmpty { start(with: .media(picked, title: "", body: "")) }
            }
            .ignoresSafeArea()
        }
    }

    private var choosing: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                LabelRow {
                    HStack(alignment: .firstTextBaseline) {
                        Text("Add an entry").font(StudioStyle.siteNameFont)
                        Spacer()
                        Button("cancel") { onDone(false) }.foregroundStyle(StudioStyle.inkSoft)
                    }
                }
                .padding(.top, StudioStyle.line)

                LabelRow(label: "A link", rule: .double) {
                    TextField("paste a link", text: $linkText)
                        .keyboardType(.URL)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                        .submitLabel(.go)
                        .focused($isTypingLink)
                        .onSubmit(addLink)
                        .ruledField(isFocused: isTypingLink)
                    if !linkText.isEmpty {
                        if pastedLink == nil {
                            Text("That doesn't look like a link yet.").foregroundStyle(StudioStyle.inkSoft)
                        } else {
                            Button("go", action: addLink)
                        }
                    }
                }

                LabelRow(label: "Photos or videos", rule: .single) {
                    Button("choose from photos") { isPicking = true }
                }

                LabelRow(label: "A note", rule: .single) {
                    Button("write a note") { start(with: .note(title: "", body: "")) }
                }
            }
        }
        .scrollDismissesKeyboard(.interactively)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .studioPage()
    }

    /// The typed link, if it's a web address ("example.com/x" counts, as https).
    private var pastedLink: URL? {
        let typed = linkText.trimmingCharacters(in: .whitespacesAndNewlines)
        let withScheme = typed.contains("://") ? typed : "https://" + typed
        guard let url = URL(string: withScheme), url.scheme == "http" || url.scheme == "https",
              let host = url.host(), host.contains(".")
        else { return nil }
        return url
    }

    private func addLink() {
        guard let link = pastedLink else { return }
        start(with: .link(link, pageTitle: nil))
    }

    private func start(with picked: SharedThing) {
        isTypingLink = false
        let model = ShareFormModel()
        form = model
        Task { await model.load(picked) }
    }
}
