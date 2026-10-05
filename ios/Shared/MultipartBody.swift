/**
 * MultipartBody: wraps a file in the "multipart/form-data" format a file
 * upload needs, written to a temporary file so large videos are never held
 * in memory (share extensions are killed if they use too much).
 *
 * Used by StudioApi.uploadMedia.
 */

import Foundation
import UniformTypeIdentifiers

enum MultipartBody {
    /// Writes the upload body for `file` (sent as the form field "file") and returns where it is.
    static func write(fileAt file: URL, boundary: String) throws -> URL {
        let body = FileManager.default.temporaryDirectory.appending(path: "upload-\(UUID().uuidString)")
        FileManager.default.createFile(atPath: body.path(), contents: nil)
        let output = try FileHandle(forWritingTo: body)
        defer { try? output.close() }

        let contentType = UTType(filenameExtension: file.pathExtension)?.preferredMIMEType ?? "application/octet-stream"
        let head = "--\(boundary)\r\n"
            + "Content-Disposition: form-data; name=\"file\"; filename=\"\(file.lastPathComponent)\"\r\n"
            + "Content-Type: \(contentType)\r\n\r\n"
        try output.write(contentsOf: Data(head.utf8))

        let input = try FileHandle(forReadingFrom: file)
        defer { try? input.close() }
        while let chunk = try input.read(upToCount: 1 << 20), !chunk.isEmpty {
            try output.write(contentsOf: chunk)
        }

        try output.write(contentsOf: Data("\r\n--\(boundary)--\r\n".utf8))
        return body
    }
}
