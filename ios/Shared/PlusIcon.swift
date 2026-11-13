/**
 * PlusIcon: the thin-stroke plus that adds, drawn the weight of a rule in the
 * ink color, like the site's plus in components/Icon.tsx.
 *
 * Used by the app's EntryListView, beside the site name.
 */

import SwiftUI

struct PlusIcon: View {
    var body: some View {
        Plus()
            .stroke(StudioStyle.ink, style: StrokeStyle(lineWidth: 1, lineCap: .square))
            .frame(width: 14, height: 14)
            .padding(6)
            .contentShape(Rectangle())
            .accessibilityLabel("add an entry")
    }

    private struct Plus: Shape {
        func path(in rect: CGRect) -> Path {
            var path = Path()
            path.move(to: CGPoint(x: rect.midX, y: rect.minY))
            path.addLine(to: CGPoint(x: rect.midX, y: rect.maxY))
            path.move(to: CGPoint(x: rect.minX, y: rect.midY))
            path.addLine(to: CGPoint(x: rect.maxX, y: rect.midY))
            return path
        }
    }
}
