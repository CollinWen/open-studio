/**
 * StudioSiteView: what the app shows once it's set up: the website, opening
 * on the studio page (StudioWebView), with one quiet line of words under it:
 * back, studio (return to the studio page) and setup (the address and token
 * screen). A page that can't load says so above that line.
 *
 * Shown by OpenStudioApp.
 */

import SwiftUI

struct StudioSiteView: View {
    let settings: StudioSettings
    let openSetup: () -> Void
    @State private var command = WebCommand()
    @State private var problem: String?

    var body: some View {
        VStack(spacing: 0) {
            if let site = settings.siteURL {
                StudioWebView(site: site, ownerToken: settings.ownerToken, command: command) { problem = $0 }
            }
            if let problem {
                Text(problem)
                    .foregroundStyle(StudioStyle.inkSoft)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, StudioStyle.margin)
                    .padding(.vertical, StudioStyle.leading)
            }
            Rectangle().fill(StudioStyle.inkFaint).frame(height: 1)
            WordList {
                Button("back") { command.send(.back) }
                Button("studio") { command.send(.studio) }
                Button("setup", action: openSetup)
            }
            .font(StudioStyle.smallFont)
            .foregroundStyle(StudioStyle.inkSoft)
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(.horizontal, StudioStyle.margin)
            .padding(.vertical, StudioStyle.leading * 2)
        }
        .studioPage()
    }
}
