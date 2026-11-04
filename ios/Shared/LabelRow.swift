/**
 * LabelRow: one row of the page, as on the site's phone layout: a quiet small
 * label ("board", "why it's here") above whatever the row holds.
 *
 * `rule` starts a new section with a line above the row that runs the full
 * width of the screen: `.double` for major breaks (under the header), `.single`
 * for minor ones. The phone's version of frontend/src/components/LabelRow.tsx.
 */

import SwiftUI

struct LabelRow<Content: View>: View {
    enum Rule { case none, single, double }

    var label = ""
    var rule = Rule.none
    @ViewBuilder let content: () -> Content

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            switch rule {
            case .none: EmptyView()
            case .single: hairline
            // Two 1pt lines, 1pt apart, like the site's double rule.
            case .double: VStack(spacing: 1) { hairline; hairline }
            }
            VStack(alignment: .leading, spacing: StudioStyle.line / 4) {
                if !label.isEmpty {
                    Text(label).font(StudioStyle.smallFont).foregroundStyle(StudioStyle.inkSoft)
                }
                content()
            }
            .padding(.horizontal, StudioStyle.margin)
            .padding(.top, rule == .none ? 0 : StudioStyle.line / 2)
        }
        .padding(.top, rule == .none ? 0 : StudioStyle.line)
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private var hairline: some View {
        Rectangle().fill(StudioStyle.ink).frame(height: 1)
    }
}
