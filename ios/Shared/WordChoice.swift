/**
 * WordChoice: a row of plain words where you tap one to choose it, inside a
 * WordList so it wraps. The chosen word sits on a solid ink square in
 * paper-colored type; the rest are soft ink. The phone's
 * components/WordChoice.tsx (its "square" look).
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
                    .pickSquare(isPicked: isPicked)
                    .accessibilityAddTraits(isPicked ? .isSelected : [])
            }
        }
        .animation(StudioStyle.quick, value: selected)
    }
}
