/**
 * SharedItems: works out what another app handed to the share sheet:
 *   - a web link (Instagram, X, YouTube, TikTok, Pinterest, Spotify, Safari, ...)
 *   - photos and videos (Photos, Files, screenshots), with any text shared
 *     alongside them (a post's caption) as their title and note
 *   - written text (a note from Notes, Messages): first line is the title, the rest the body
 *
 * In that order. Some apps share links as plain text, so text that is little more
 * than a link counts as a link; anything longer is a note. Used by ShareFormModel.
 */

import Foundation
import UniformTypeIdentifiers

enum SharedThing {
    case link(URL, pageTitle: String?)
    case note(title: String, body: String)
    /// Photos and videos, with the title and body of any text shared alongside (often empty).
    case media([NSItemProvider], title: String, body: String)
    case nothingUsable
}

enum SharedItems {
    /// Text with at most this many characters around a link is treated as just the link.
    private static let linkOnlyAllowance = 40

    static func read(from context: NSExtensionContext?) async -> SharedThing {
        let items = context?.inputItems.compactMap { $0 as? NSExtensionItem } ?? []
        let providers = items.flatMap { $0.attachments ?? [] }
        let contentText = items.compactMap { $0.attributedContentText?.string }.first { !$0.isEmpty }

        if let link = await firstWebLink(in: providers) {
            return .link(link, pageTitle: contentText)
        }
        let text = await firstText(in: providers) ?? contentText
        if let text, let link = linkOnly(in: text) {
            return .link(link, pageTitle: nil)
        }
        let media = providers.filter {
            $0.hasItemConformingToTypeIdentifier(UTType.image.identifier)
                || $0.hasItemConformingToTypeIdentifier(UTType.movie.identifier)
        }
        let (title, body) = split(text ?? "")
        if !media.isEmpty { return .media(media, title: title, body: body) }
        if !title.isEmpty || !body.isEmpty { return .note(title: title, body: body) }
        return .nothingUsable
    }

    // MARK: - Links

    private static func firstWebLink(in providers: [NSItemProvider]) async -> URL? {
        for provider in providers where provider.hasItemConformingToTypeIdentifier(UTType.url.identifier) {
            // Photos also shares file:// URLs; only http(s) links count.
            if let url = try? await loadItem(from: provider, as: .url) as? URL, isWebLink(url) {
                return url
            }
        }
        return nil
    }

    /// The link, if the text is a link with at most a few words around it.
    private static func linkOnly(in text: String) -> URL? {
        let detector = try? NSDataDetector(types: NSTextCheckingResult.CheckingType.link.rawValue)
        let range = NSRange(text.startIndex..., in: text)
        guard let match = detector?.matches(in: text, range: range).first(where: { $0.url.map(isWebLink) ?? false }),
              let url = match.url
        else { return nil }
        let leftover = (text as NSString).length - match.range.length
        return leftover <= linkOnlyAllowance ? url : nil
    }

    private static func isWebLink(_ url: URL) -> Bool {
        url.scheme == "http" || url.scheme == "https"
    }

    // MARK: - Notes

    private static func firstText(in providers: [NSItemProvider]) async -> String? {
        for provider in providers where provider.hasItemConformingToTypeIdentifier(UTType.plainText.identifier) {
            if let text = try? await loadItem(from: provider, as: .plainText) as? String,
               !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                return text
            }
        }
        return nil
    }

    /// Notes puts the title on the first line; everything after it is the body.
    private static func split(_ text: String) -> (title: String, body: String) {
        let lines = text.trimmingCharacters(in: .whitespacesAndNewlines).components(separatedBy: .newlines)
        let title = lines.first?.trimmingCharacters(in: .whitespaces) ?? ""
        let body = lines.dropFirst().joined(separator: "\n").trimmingCharacters(in: .whitespacesAndNewlines)
        return (title, body)
    }

    private static func loadItem(from provider: NSItemProvider, as type: UTType) async throws -> NSSecureCoding? {
        try await withCheckedThrowingContinuation { continuation in
            provider.loadItem(forTypeIdentifier: type.identifier, options: nil) { item, error in
                if let error { continuation.resume(throwing: error) } else { continuation.resume(returning: item) }
            }
        }
    }
}
