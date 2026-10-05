/**
 * ShareViewController: the share extension's entry point. iOS creates it when
 * "Open Studio" is picked in the share sheet (named in Info.plist via project.yml).
 *
 * It only shows ShareForm and closes the sheet afterwards; the work is in ShareFormModel.
 */

import SwiftUI
import UIKit

final class ShareViewController: UIViewController {
    private let model = ShareFormModel()

    override func viewDidLoad() {
        super.viewDidLoad()
        let form = ShareForm(
            model: model,
            onSaved: { [weak self] in self?.extensionContext?.completeRequest(returningItems: nil) },
            onCancel: { [weak self] in self?.extensionContext?.cancelRequest(withError: CocoaError(.userCancelled)) }
        )
        let host = UIHostingController(rootView: form)
        addChild(host)
        host.view.frame = view.bounds
        host.view.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        view.addSubview(host.view)
        host.didMove(toParent: self)

        Task { await model.load(from: extensionContext) }
    }
}
