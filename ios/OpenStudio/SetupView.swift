/**
 * SetupView: the app's only screen, laid out like a page on the site. Enter
 * the server address and the owner token (OWNER_TOKEN in backend/.env); both
 * are saved to the shared keychain where the share extension reads them.
 * Saving also checks the server can be reached and lists its boards, so you
 * know sharing will work before you try it.
 */

import SwiftUI

struct SetupView: View {
    @State private var settings = StudioSettings.load()
    @State private var saved = false
    @State private var isChecking = false
    /// What the last check found: the boards, or what went wrong.
    @State private var connection: String?
    @FocusState private var focused: Field?
    private enum Field { case address, token }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                LabelRow {
                    Text("Open Studio").font(StudioStyle.siteNameFont)
                }
                .padding(.top, StudioStyle.line)

                LabelRow(label: "How", rule: .double) {
                    Text("Tap share in any app (Instagram, X, YouTube, TikTok, Pinterest, Safari, Notes, Photos) and choose Open Studio. Pick the board it goes on, and it's there.")
                }

                LabelRow(label: "Server address", rule: .single) {
                    TextField("https://studio.example.com", text: $settings.serverAddress)
                        .keyboardType(.URL)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                        .focused($focused, equals: .address)
                        .ruledField(isFocused: focused == .address)
                    if !settings.serverAddress.isEmpty && settings.serverURL == nil {
                        Text("The address should start with http:// or https://").foregroundStyle(StudioStyle.inkSoft)
                    }
                }

                LabelRow(label: "Owner token", rule: .single) {
                    SecureField("OWNER_TOKEN from backend/.env", text: $settings.ownerToken)
                        .focused($focused, equals: .token)
                        .ruledField(isFocused: focused == .token)
                }

                LabelRow(rule: .single) {
                    WordList {
                        Button(saved ? "saved" : "save") { Task { await saveAndCheck() } }
                            .foregroundStyle(settings.isComplete ? StudioStyle.ink : StudioStyle.inkSoft)
                            .underline(saved, color: StudioStyle.accent)
                            .disabled(!settings.isComplete || isChecking)
                        if isChecking {
                            LoadingWord(text: "checking the server…")
                        } else if let connection {
                            Text(connection).foregroundStyle(StudioStyle.inkSoft)
                        }
                    }
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .studioPage()
        .onChange(of: settings) {
            saved = false
            connection = nil
        }
    }

    private func saveAndCheck() async {
        focused = nil
        settings.save()
        saved = true
        isChecking = true
        defer { isChecking = false }
        do {
            let boards = try await StudioApi(settings: settings).fetchBoards()
            let names = boards.map { $0.name.lowercased() }.joined(separator: ", ")
            connection = "connected · \(boards.count) board\(boards.count == 1 ? "" : "s"): \(names)"
        } catch {
            connection = error.localizedDescription
        }
    }
}
