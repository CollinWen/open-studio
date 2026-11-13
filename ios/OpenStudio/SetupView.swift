/**
 * SetupView: the app's setup screen, laid out like a page on the site. Enter
 * the server address and the owner token (OWNER_TOKEN in backend/.env); both
 * are saved to the shared keychain, where the studio and the share extension
 * read them. Saving also checks the server can be reached and lists its
 * boards, so you know it works before you try it; then "open the studio".
 *
 * Shown by OpenStudioApp until both are saved, and again from the studio's
 * "setup" word.
 */

import SwiftUI

struct SetupView: View {
    let openStudio: () -> Void
    @State private var settings = StudioSettings.load()
    /// Already saved from an earlier visit, until something is changed.
    @State private var saved = StudioSettings.load().isComplete
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
                    Text("Tap share in any app (Instagram, X, YouTube, TikTok, Pinterest, Safari, Notes, Photos) and choose Open Studio. Pick the board it goes on, and it's there. Here in the app: add, edit, publish and delete entries.")
                }

                LabelRow(label: "Server address", rule: .single) {
                    TextField("https://api.example.com", text: $settings.serverAddress)
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
                        if saved && settings.isComplete && !isChecking {
                            Button("open the studio", action: openStudio)
                        }
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
