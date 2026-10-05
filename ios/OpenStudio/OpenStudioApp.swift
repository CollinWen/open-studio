/**
 * OpenStudioApp: the app you open once, to tell the share extension where
 * your site is and give it the owner token. Day to day you use the share
 * sheet instead (see ShareToStudio/).
 */

import SwiftUI

@main
struct OpenStudioApp: App {
    var body: some Scene {
        WindowGroup {
            SetupView()
        }
    }
}
