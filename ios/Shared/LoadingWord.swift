/**
 * LoadingWord: a word that breathes slowly while something is on its way
 * ("reading…", "saving, suggesting tags…"), the one sign of waiting, like the
 * site's components/LoadingWord.tsx. With reduced motion it simply stays soft.
 *
 * Used by ShareForm and SetupView.
 */

import SwiftUI

struct LoadingWord: View {
    let text: String

    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var faded = false

    var body: some View {
        Text(text)
            .foregroundStyle(StudioStyle.inkSoft)
            .opacity(faded ? 0.35 : 1)
            .onAppear {
                guard !reduceMotion else { return }
                withAnimation(StudioStyle.breathe) { faded = true }
            }
    }
}
