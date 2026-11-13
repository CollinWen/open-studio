/**
 * StudioSettings: where the site's backend lives (server address), where the
 * website itself lives (site address, which the app shows), the owner token
 * that proves it's you, and the board the last entry went to. Saved in the
 * shared keychain.
 *
 * The app's SetupView writes the addresses and token; the app's StudioWebView
 * opens the site address; the share extension reads the server address and
 * token, and remembers the board so the next share starts there.
 */

import Foundation

struct StudioSettings: Equatable {
    var serverAddress: String
    var siteAddress: String
    var ownerToken: String

    /// Enough for the share extension: a backend to send to and the token.
    var isComplete: Bool { serverURL != nil && !ownerToken.isEmpty }

    /// Enough for the app to open the website, signed in.
    var canOpenSite: Bool { siteURL != nil && !ownerToken.isEmpty }

    /// The server address as a URL, or nil if it isn't a usable http(s) address.
    var serverURL: URL? { Self.webAddress(serverAddress) }

    /// The website's address as a URL, or nil if it isn't a usable http(s) address.
    var siteURL: URL? { Self.webAddress(siteAddress) }

    private static func webAddress(_ address: String) -> URL? {
        let trimmed = address.trimmingCharacters(in: .whitespacesAndNewlines)
        guard let url = URL(string: trimmed),
              url.scheme == "http" || url.scheme == "https",
              url.host() != nil
        else { return nil }
        return url
    }

    static func load() -> StudioSettings {
        StudioSettings(
            serverAddress: SharedKeychain.read("serverAddress") ?? "",
            siteAddress: SharedKeychain.read("siteAddress") ?? "",
            ownerToken: SharedKeychain.read("ownerToken") ?? ""
        )
    }

    /// The board the last shared entry went to, so the share sheet starts there.
    static var lastBoard: String? { SharedKeychain.read("lastBoard") }

    static func rememberBoard(_ slug: String) {
        SharedKeychain.write("lastBoard", slug)
    }

    func save() {
        SharedKeychain.write("serverAddress", serverAddress.trimmingCharacters(in: .whitespacesAndNewlines))
        SharedKeychain.write("siteAddress", siteAddress.trimmingCharacters(in: .whitespacesAndNewlines))
        SharedKeychain.write("ownerToken", ownerToken.trimmingCharacters(in: .whitespacesAndNewlines))
    }
}
