/**
 * SectionLine: a line of larger words naming the spaces you can be in, with
 * the current one on a solid accent square in paper-colored type. The phone's
 * components/SectionLine.tsx; anything passed as `below` sits under the words
 * (a board's agents). `label` isn't shown; VoiceOver reads it as the line's name.
 *
 * Used by ShareForm to pick the board an entry goes to.
 */

import SwiftUI

/// One word in a section line: what it's called, and the id passed back when it's picked.
struct SectionWord: Identifiable {
    let id: String
    let label: String
}

struct SectionLine<Below: View>: View {
    var label: String
    let sections: [SectionWord]
    let current: String
    let onPick: (String) -> Void
    @ViewBuilder var below: () -> Below

    var body: some View {
        LabelRow(rule: .single) {
            WordList {
                ForEach(sections) { section in
                    let isCurrent = section.id == current
                    Button(section.label) { onPick(section.id) }
                        .font(StudioStyle.largeFont)
                        .padding(.vertical, StudioStyle.line / 4)
                        .pickSquare(isPicked: isCurrent, fill: StudioStyle.accent)
                        .accessibilityAddTraits(isCurrent ? .isSelected : [])
                }
            }
            .animation(StudioStyle.quick, value: current)
            .accessibilityElement(children: .contain)
            .accessibilityLabel(label)
            below()
        }
    }
}
