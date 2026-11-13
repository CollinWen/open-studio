/**
 * OpenStudioApp: starts the app. Once the server address and owner token are
 * saved, it opens the studio (EntryListView: your entries, to add, edit,
 * publish and delete); until then, and whenever you tap "setup" there, it
 * shows SetupView. The share sheet (ShareToStudio/) uses the same settings.
 */

import SwiftUI

@main
struct OpenStudioApp: App {
    @State private var isSetUp = StudioSettings.load().isComplete
    @State private var isChangingSetup = false

    var body: some Scene {
        WindowGroup {
            if isSetUp && !isChangingSetup {
                EntryListView(openSetup: { isChangingSetup = true })
            } else {
                SetupView(openStudio: {
                    isSetUp = StudioSettings.load().isComplete
                    isChangingSetup = false
                })
            }
        }
    }
}
