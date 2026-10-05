/**
 * StudioSettings: where the site's backend lives (server address) and the
 * owner token that proves it's you. Saved in the shared keychain.
 *
 * The app's SetupView writes these; the share extension only reads them.
 */

import Foundation

struct StudioSettings: Equatable {
    var serverAddress: String
    var ownerToken: String

    var isComplete: Bool { serverURL != nil && !ownerToken.isEmpty }

    /// The server address as a URL, or nil if it isn't a usable http(s) address.
    var serverURL: URL? {
        let trimmed = serverAddress.trimmingCharacters(in: .whitespacesAndNewlines)
        guard let url = URL(string: trimmed),
              url.scheme == "http" || url.scheme == "https",
              url.host() != nil
        else { return nil }
        return url
    }

    static func load() -> StudioSettings {
        StudioSettings(
            serverAddress: SharedKeychain.read("serverAddress") ?? "",
            ownerToken: SharedKeychain.read("ownerToken") ?? ""
        )
    }

    func save() {
        SharedKeychain.write("serverAddress", serverAddress.trimmingCharacters(in: .whitespacesAndNewlines))
        SharedKeychain.write("ownerToken", ownerToken.trimmingCharacters(in: .whitespacesAndNewlines))
    }
}
