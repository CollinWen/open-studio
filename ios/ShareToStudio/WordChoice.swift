/**
 * WordChoice: a row of plain words where you tap one to choose it.
 * The chosen word is black and underlined; the rest are gray.
 *
 * Used by ShareForm for "made by me / inspiration" and the visibility choice.
 */

import SwiftUI

struct WordChoice<Option: Hashable>: View {
    let options: [Option]
    @Binding var selected: Option
    let label: (Option) -> String

    var body: some View {
        HStack(spacing: 20) {
            ForEach(options, id: \.self) { option in
                Button(label(option)) { selected = option }
                    .foregroundStyle(option == selected ? Color.black : Color.gray)
                    .underline(option == selected)
            }
        }
    }
}
