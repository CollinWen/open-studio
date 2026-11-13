/**
 * EntryRow: one entry in the app's studio list, like a row of the site's
 * studio ledger: the date small above, the title, then its board, who sees
 * it and (for an agent's entry) who added it, with a small square of its
 * cover on the right when it has a picture. A hairline separates the rows.
 *
 * Used by EntryListView.
 */

import SwiftUI

struct EntryRow: View {
    let entry: StudioEntry
    let boardName: String
    let api: StudioApi

    private static let coverSize: CGFloat = 3 * StudioStyle.line

    var body: some View {
        VStack(spacing: 0) {
            Rectangle().fill(StudioStyle.inkFaint).frame(height: 1)
            HStack(alignment: .top, spacing: StudioStyle.wordGap) {
                VStack(alignment: .leading, spacing: 2) {
                    Text(entry.occurredAt.prefix(10))
                        .font(StudioStyle.smallFont)
                        .foregroundStyle(StudioStyle.inkSoft)
                        .monospacedDigit()
                    Text(entry.title.isEmpty ? "untitled" : entry.title)
                        .foregroundStyle(entry.title.isEmpty ? StudioStyle.inkSoft : StudioStyle.ink)
                        .lineLimit(2)
                        .multilineTextAlignment(.leading)
                    Text(details)
                        .font(StudioStyle.smallFont)
                        .foregroundStyle(StudioStyle.inkSoft)
                        .lineLimit(1)
                }
                Spacer(minLength: 0)
                if let cover = entry.media.first.flatMap({ api.pictureURL(of: $0) }) {
                    CoverSquare(url: cover, size: Self.coverSize)
                }
            }
            .padding(.horizontal, StudioStyle.margin)
            .padding(.vertical, StudioStyle.line / 2)
        }
        .contentShape(Rectangle())
        .accessibilityElement(children: .combine)
        .accessibilityHint("opens the entry")
    }

    private var details: String {
        var parts = [boardName, EntryListView.audience(entry.visibility)]
        if entry.addedBy.hasPrefix("agent:") { parts.append("by \(entry.addedBy.dropFirst("agent:".count))") }
        return parts.joined(separator: " · ")
    }
}

/// A picture cropped to a square, fading in as it loads, on the shaded paper until then.
struct CoverSquare: View {
    let url: URL
    let size: CGFloat

    var body: some View {
        AsyncImage(url: url, transaction: Transaction(animation: StudioStyle.arrive)) { phase in
            if let image = phase.image {
                image.resizable().scaledToFill().transition(.opacity)
            } else {
                StudioStyle.paperShade
            }
        }
        .frame(width: size, height: size)
        .clipped()
        .accessibilityHidden(true)
    }
}
