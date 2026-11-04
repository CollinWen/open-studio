/**
 * CaretIcon: the thin-stroke caret that opens and closes a control band,
 * drawn the weight of a rule in the ink color, like components/Icon.tsx.
 * Points down when closed, up when open.
 *
 * Used by ControlBand.
 */

import SwiftUI

struct CaretIcon: View {
    let isOpen: Bool

    var body: some View {
        Caret()
            .stroke(StudioStyle.ink, style: StrokeStyle(lineWidth: 1, lineCap: .square))
            .frame(width: 9, height: 5)
            .rotationEffect(.degrees(isOpen ? 180 : 0))
            .padding(.bottom, 1)
            .accessibilityHidden(true)
    }

    private struct Caret: Shape {
        func path(in rect: CGRect) -> Path {
            var path = Path()
            path.move(to: CGPoint(x: rect.minX, y: rect.minY))
            path.addLine(to: CGPoint(x: rect.midX, y: rect.maxY))
            path.addLine(to: CGPoint(x: rect.maxX, y: rect.minY))
            return path
        }
    }
}
