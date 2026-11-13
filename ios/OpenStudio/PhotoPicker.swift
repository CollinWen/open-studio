/**
 * PhotoPicker: the phone's own photo library picker, for choosing photos and
 * videos to add. Hands back each pick as the original file (never a
 * re-encoded copy), ready for PreparedMedia, the same way the share sheet
 * receives photos. Needs no permission: the picker runs outside the app.
 *
 * Used by AddEntryView and EntryEditView.
 */

import PhotosUI
import SwiftUI

struct PhotoPicker: UIViewControllerRepresentable {
    /// Called with what was picked; empty when the picker was closed without picking.
    let onPicked: ([NSItemProvider]) -> Void

    private static let pickLimit = 20

    func makeUIViewController(context: Context) -> PHPickerViewController {
        var configuration = PHPickerConfiguration()
        configuration.filter = .any(of: [.images, .videos])
        configuration.selectionLimit = Self.pickLimit
        configuration.selection = .ordered
        // The original file: media is never altered (HEIC becomes JPEG in PreparedMedia, keeping its date).
        configuration.preferredAssetRepresentationMode = .current
        let picker = PHPickerViewController(configuration: configuration)
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ picker: PHPickerViewController, context: Context) {}

    func makeCoordinator() -> Coordinator { Coordinator(onPicked: onPicked) }

    final class Coordinator: NSObject, PHPickerViewControllerDelegate {
        let onPicked: ([NSItemProvider]) -> Void

        init(onPicked: @escaping ([NSItemProvider]) -> Void) { self.onPicked = onPicked }

        func picker(_ picker: PHPickerViewController, didFinishPicking results: [PHPickerResult]) {
            onPicked(results.map(\.itemProvider))
        }
    }
}
