/**
 * ControlBand: the shaded band of controls under a section line, the phone's
 * components/ControlBand.tsx. Its main controls always show; a caret opens the
 * extra ones (`more`). While closed, what's picked in there still shows beside
 * the caret (`picks`), so nothing is hidden.
 *
 * Used by ShareForm (made by me / inspiration and visibility; "builds on" behind the caret).
 */

import SwiftUI

struct ControlBand<Main: View, More: View>: View {
    let moreLabel: String
    let picks: String
    @Binding var isOpen: Bool
    @ViewBuilder let main: () -> Main
    @ViewBuilder let more: () -> More

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        VStack(alignment: .leading, spacing: StudioStyle.line / 2) {
            main()
            Button {
                withAnimation(reduceMotion ? nil : (isOpen ? StudioStyle.leave : StudioStyle.arrive)) {
                    isOpen.toggle()
                }
            } label: {
                HStack(alignment: .firstTextBaseline, spacing: StudioStyle.wordGap / 2) {
                    Text(moreLabel)
                    CaretIcon(isOpen: isOpen)
                    if !isOpen && !picks.isEmpty {
                        Text(picks).foregroundStyle(StudioStyle.inkSoft).lineLimit(1)
                    }
                }
                .contentShape(Rectangle())
            }
            .accessibilityHint(isOpen ? "closes \(moreLabel)" : "opens \(moreLabel)")
            if isOpen {
                more().transition(reduceMotion ? AnyTransition.opacity : AnyTransition.opacity.combined(with: .offset(y: -12)))
            }
        }
        .padding(.horizontal, StudioStyle.margin)
        .padding(.vertical, StudioStyle.line / 2)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(StudioStyle.paperShade)
        .overlay(alignment: .top) {
            Rectangle().fill(StudioStyle.inkFaint).frame(height: 1)
        }
        .clipped()
    }
}
