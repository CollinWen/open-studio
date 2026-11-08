/**
 * StudioMark: the studio's logo for the phone, the same panel of squares as
 * the site's components/StudioMark.tsx and drawn from the same pattern (change
 * both together). Each lit cell is a whole square, so neighbours meet edge to
 * edge or at a corner. Still, every square is lit; playing, the squares light
 * up in a sweep from the top-left corner and fade again, like a panel refreshing.
 * With reduced motion it holds still.
 *
 * Used by LoadingWord.
 */

import SwiftUI

struct StudioMark: View {
    var isPlaying = false
    /// The mark's height; the width follows the pattern.
    var height: CGFloat = StudioStyle.line * 0.6

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    // "O" is a lit square, "_" an empty place, as on the site.
    static let pattern = ["_OO_OO_", "O__O__O", "O__O__O", "O__O__O", "_OO_OO_"]

    private static let squares: [(x: Int, y: Int)] = pattern.enumerated().flatMap { y, row in
        row.enumerated().compactMap { x, cell -> (x: Int, y: Int)? in cell == "O" ? (x: x, y: y) : nil }
    }
    private static let columns = CGFloat(pattern[0].count)
    private static let rows = CGFloat(pattern.count)
    /// One sweep across the panel, the site's --motion-ambient.
    private static let period: Double = 1.6
    private static let restOpacity: Double = 0.18

    var body: some View {
        Group {
            if isPlaying && !reduceMotion {
                TimelineView(.animation) { timeline in
                    panel(at: timeline.date.timeIntervalSinceReferenceDate)
                }
            } else {
                panel(at: nil)
            }
        }
        .frame(width: height * Self.columns / Self.rows, height: height)
        .accessibilityHidden(true)
    }

    private func panel(at time: Double?) -> some View {
        Canvas { context, size in
            let cell = size.height / Self.rows
            for square in Self.squares {
                // A hair over one cell, so squares that share an edge show no seam.
                let rect = CGRect(x: CGFloat(square.x) * cell, y: CGFloat(square.y) * cell, width: cell + 0.5, height: cell + 0.5)
                let opacity = time.map { Self.opacity(order: square.x + square.y, time: $0) } ?? 1
                context.fill(Path(rect), with: .color(StudioStyle.ink.opacity(opacity)))
            }
        }
    }

    /// Where a square is in its sweep: it lights decelerating over the first fifth
    /// of the period, fades accelerating until three fifths, then rests faint,
    /// each square a twentieth of the period after the one before (as the site's
    /// mark-light keyframes).
    private static func opacity(order: Int, time: Double) -> Double {
        var phase = (time / period - Double(order) / 20).truncatingRemainder(dividingBy: 1)
        if phase < 0 { phase += 1 }
        let lit: Double
        if phase < 0.2 {
            let progress = phase / 0.2
            lit = 1 - pow(1 - progress, 3)
        } else if phase < 0.6 {
            let progress = (phase - 0.2) / 0.4
            lit = 1 - pow(progress, 3)
        } else {
            lit = 0
        }
        return restOpacity + (1 - restOpacity) * lit
    }
}
