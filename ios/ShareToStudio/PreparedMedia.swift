/**
 * PreparedMedia: turns one shared photo or video into a file ready to upload,
 * plus the date it was taken.
 *
 * Files are sent untouched when browsers can show them (JPEG, PNG, GIF, WebP, MP4).
 * Two exceptions, because browsers can't show the iPhone's own formats:
 *   - HEIC photos become JPEG (date and location kept)
 *   - .mov videos are moved into an .mp4 wrapper (same video and sound, not re-encoded)
 */

import AVFoundation
import ImageIO
import UniformTypeIdentifiers

struct PreparedMedia {
    let file: URL  // a temporary copy; delete it after uploading
    let isVideo: Bool
    let takenAt: Date?

    static func prepare(_ provider: NSItemProvider) async throws -> PreparedMedia {
        if provider.hasItemConformingToTypeIdentifier(UTType.movie.identifier) {
            return try await prepareVideo(provider)
        }
        return try await preparePhoto(provider)
    }

    // MARK: - Photos

    private static let browserImageTypes: [UTType] = [.jpeg, .png, .gif, .webP]

    private static func preparePhoto(_ provider: NSItemProvider) async throws -> PreparedMedia {
        let original = firstRegisteredType(of: provider, conformingTo: .image)
        let file: URL
        if let original, browserImageTypes.contains(where: { original.conforms(to: $0) }) {
            file = try await copyFile(from: provider, as: original)
        } else if provider.hasItemConformingToTypeIdentifier(UTType.jpeg.identifier) {
            // The sharing app can hand over a JPEG itself (Photos does for HEIC).
            file = try await copyFile(from: provider, as: .jpeg)
        } else {
            file = try await convertToJpeg(from: provider, as: original ?? .image)
        }
        return PreparedMedia(file: file, isVideo: false, takenAt: PhotoDate.read(from: file))
    }

    private static func convertToJpeg(from provider: NSItemProvider, as type: UTType) async throws -> URL {
        try await withSharedFile(from: provider, as: type) { shared in
            let output = temporaryFile(extension: "jpg")
            guard let source = CGImageSourceCreateWithURL(shared as CFURL, nil),
                  let destination = CGImageDestinationCreateWithURL(
                      output as CFURL, UTType.jpeg.identifier as CFString, 1, nil)
            else { throw StudioError("Couldn't read this photo.") }
            let options = [kCGImageDestinationLossyCompressionQuality: 0.95] as CFDictionary
            CGImageDestinationAddImageFromSource(destination, source, 0, options)  // keeps metadata
            guard CGImageDestinationFinalize(destination) else { throw StudioError("Couldn't convert this photo.") }
            return output
        }
    }

    // MARK: - Videos

    private static func prepareVideo(_ provider: NSItemProvider) async throws -> PreparedMedia {
        let original = firstRegisteredType(of: provider, conformingTo: .movie) ?? .movie
        let copy = try await copyFile(from: provider, as: original)
        let asset = AVURLAsset(url: copy)
        let takenAt = try? await asset.load(.creationDate)?.load(.dateValue)
        if original.conforms(to: .mpeg4Movie) {
            return PreparedMedia(file: copy, isVideo: true, takenAt: takenAt)
        }

        let mp4 = temporaryFile(extension: "mp4")
        guard let export = AVAssetExportSession(asset: asset, presetName: AVAssetExportPresetPassthrough) else {
            throw StudioError("Couldn't prepare this video.")
        }
        try await export.export(to: mp4, as: .mp4)
        try? FileManager.default.removeItem(at: copy)
        return PreparedMedia(file: mp4, isVideo: true, takenAt: takenAt)
    }

    // MARK: - Files

    private static func firstRegisteredType(of provider: NSItemProvider, conformingTo kind: UTType) -> UTType? {
        provider.registeredTypeIdentifiers.compactMap { UTType($0) }.first { $0.conforms(to: kind) }
    }

    private static func copyFile(from provider: NSItemProvider, as type: UTType) async throws -> URL {
        try await withSharedFile(from: provider, as: type) { shared in
            let copy = temporaryFile(extension: type.preferredFilenameExtension ?? shared.pathExtension)
            try FileManager.default.copyItem(at: shared, to: copy)
            return copy
        }
    }

    /// iOS deletes the shared file as soon as `use` returns, so `use` must copy or convert it.
    private static func withSharedFile(
        from provider: NSItemProvider, as type: UTType, use: @escaping (URL) throws -> URL
    ) async throws -> URL {
        try await withCheckedThrowingContinuation { continuation in
            _ = provider.loadFileRepresentation(forTypeIdentifier: type.identifier) { shared, error in
                guard let shared else {
                    continuation.resume(throwing: error ?? StudioError("Couldn't read a shared file."))
                    return
                }
                continuation.resume(with: Result { try use(shared) })
            }
        }
    }

    private static func temporaryFile(extension pathExtension: String) -> URL {
        FileManager.default.temporaryDirectory
            .appending(path: UUID().uuidString)
            .appendingPathExtension(pathExtension)
    }
}
