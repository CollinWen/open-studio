/**
 * WordChoice: a row of plain words where you tap one to choose it, inside a
 * WordList so it wraps. The chosen word is in full ink, underlined in the
 * accent; the rest are soft ink. The phone's components/WordChoice.tsx.
 *
 * Used by ShareForm for "made by me / inspiration" and the visibility choice.
 */

import SwiftUI

struct WordChoice<Option: Hashable>: View {
    let options: [Option]
    @Binding var selected: Option
    let label: (Option) -> String

    var body: some View {
        WordList {
            ForEach(options, id: \.self) { option in
                let isPicked = option == selected
                Button(label(option)) { selected = option }
                    .foregroundStyle(isPicked ? StudioStyle.ink : StudioStyle.inkSoft)
                    .underline(isPicked, color: StudioStyle.accent)
                    .accessibilityAddTraits(isPicked ? .isSelected : [])
            }
        }
        .animation(StudioStyle.quick, value: selected)
    }
}
