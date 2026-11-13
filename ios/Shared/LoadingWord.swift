/**
 * LoadingWord: the sign that something is on its way ("reading…", "saving,
 * suggesting tags…"): the studio mark sweeping beside a soft word, like the
 * site's components/LoadingWord.tsx. With reduced motion the mark holds still.
 *
 * Used by ShareForm, SetupView and the studio screens. The mark itself is StudioMark.
 */

import SwiftUI

struct LoadingWord: View {
    let text: String

    var body: some View {
        HStack(spacing: StudioStyle.wordGap * 0.45) {
            StudioMark(isPlaying: true)
            Text(text).foregroundStyle(StudioStyle.inkSoft)
        }
    }
}
