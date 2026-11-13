/**
 * OpenStudioApp: starts the app. Once the site address and owner token are
 * set, it opens the website on the studio page, signed in (StudioSiteView);
 * until then, and whenever you tap "setup", it shows SetupView. The share
 * sheet (ShareToStudio/) works on its own once the server address and token
 * are saved.
 */

import SwiftUI

@main
struct OpenStudioApp: App {
    @State private var settings = StudioSettings.load()
    @State private var isSettingUp = !StudioSettings.load().canOpenSite

    var body: some Scene {
        WindowGroup {
            if isSettingUp || !settings.canOpenSite {
                SetupView(openSite: {
                    settings = StudioSettings.load()
                    isSettingUp = false
                })
            } else {
                StudioSiteView(settings: settings, openSetup: { isSettingUp = true })
                    // A new address or token starts a fresh web view.
                    .id("\(settings.siteAddress)|\(settings.ownerToken)")
            }
        }
    }
}
