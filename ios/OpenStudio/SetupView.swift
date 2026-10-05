/**
 * SetupView: the app's only screen. Enter the server address and the owner
 * token (OWNER_TOKEN in backend/.env); both are saved to the shared keychain
 * where the share extension reads them.
 */

import SwiftUI

struct SetupView: View {
    @State private var settings = StudioSettings.load()
    @State private var saved = false

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            Text("Open Studio").font(.title2.weight(.semibold))
            Text("To add something, tap share in any app (Instagram, X, YouTube, Notes, Photos, Safari) and choose Open Studio.")
                .foregroundStyle(.gray)

            TextField("server address, like https://studio.example.com", text: $settings.serverAddress)
                .keyboardType(.URL)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
            SecureField("owner token", text: $settings.ownerToken)

            Button(saved ? "saved" : "save") {
                settings.save()
                saved = true
            }
            .fontWeight(.semibold)
            .disabled(!settings.isComplete)

            if !settings.serverAddress.isEmpty && settings.serverURL == nil {
                Text("The address should start with http:// or https://").foregroundStyle(.gray)
            }
            Spacer()
        }
        .padding(24)
        .buttonStyle(.plain)
        .foregroundStyle(.black)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .background(Color.white)
        .preferredColorScheme(.light)
        .onChange(of: settings) { saved = false }
    }
}
