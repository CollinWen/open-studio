/**
 * SectionLine: a line of larger words naming the spaces you can be in, with
 * the current one in the accent and underlined. The phone's
 * components/SectionLine.tsx; anything passed as `below` sits under the words
 * (a board's agents).
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
        LabelRow(label: label, rule: .single) {
            WordList {
                ForEach(sections) { section in
                    let isCurrent = section.id == current
                    Button(section.label) { onPick(section.id) }
                        .font(StudioStyle.largeFont)
                        .foregroundStyle(isCurrent ? StudioStyle.accent : StudioStyle.inkSoft)
                        .underline(isCurrent, color: StudioStyle.accent)
                        .accessibilityAddTraits(isCurrent ? .isSelected : [])
                }
            }
            .animation(StudioStyle.quick, value: current)
            below()
        }
    }
}
