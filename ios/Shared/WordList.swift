/**
 * WordList: a line of words that wraps onto the next line when it runs out of
 * room, with an even gap between words. The phone's `.word-list`; every line
 * of words (boards, choices, actions) sits in one.
 *
 * Used by SectionLine, ShareForm and SetupView.
 */

import SwiftUI

struct WordList: Layout {
    var gap = StudioStyle.wordGap
    var lineGap = StudioStyle.leading

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let placed = place(subviews, within: proposal.width ?? .infinity)
        let width = placed.map(\.maxX).max() ?? 0
        let height = placed.map(\.maxY).max() ?? 0
        return CGSize(width: width, height: height)
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        for (index, frame) in place(subviews, within: bounds.width).enumerated() {
            subviews[index].place(
                at: CGPoint(x: bounds.minX + frame.minX, y: bounds.minY + frame.minY),
                proposal: ProposedViewSize(frame.size)
            )
        }
    }

    /// Left to right, starting a new line whenever the next word wouldn't fit.
    private func place(_ subviews: Subviews, within width: CGFloat) -> [CGRect] {
        var frames: [CGRect] = []
        var x: CGFloat = 0
        var y: CGFloat = 0
        var lineHeight: CGFloat = 0
        for subview in subviews {
            var size = subview.sizeThatFits(ProposedViewSize(width: width, height: nil))
            size.width = min(size.width, width)
            if x > 0 && x + size.width > width {
                x = 0
                y += lineHeight + lineGap
                lineHeight = 0
            }
            frames.append(CGRect(origin: CGPoint(x: x, y: y), size: size))
            x += size.width + gap
            lineHeight = max(lineHeight, size.height)
        }
        return frames
    }
}
