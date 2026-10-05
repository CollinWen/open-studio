/**
 * StudioApi: every call the phone makes to the Open Studio backend.
 *
 *   POST /api/capture/link   a link -> prefilled entry draft
 *   POST /api/media          upload one photo or video -> its URL
 *   POST /api/entries        save a new entry
 *
 * Every call carries the owner token. Nothing else on the phone talks to the network.
 */

import Foundation

struct StudioApi {
    let settings: StudioSettings

    func captureLink(_ link: URL) async throws -> CapturedLink {
        var request = try makeRequest("api/capture/link")
        request.httpBody = try Self.encoder.encode(["url": link.absoluteString])
        let data = try await send(request)
        return try Self.decoder.decode(CapturedLink.self, from: data)
    }

    /// Uploads the file untouched and returns the URL the site serves it from.
    func uploadMedia(fileAt file: URL) async throws -> String {
        let boundary = "open-studio-\(UUID().uuidString)"
        let body = try MultipartBody.write(fileAt: file, boundary: boundary)
        defer { try? FileManager.default.removeItem(at: body) }

        var request = try makeRequest("api/media")
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        let (data, response) = try await URLSession.shared.upload(for: request, fromFile: body)
        try Self.check(response, data)
        guard let url = try Self.decoder.decode([String: String].self, from: data)["url"] else {
            throw StudioError("The server didn't say where it saved the file.")
        }
        return url
    }

    func createEntry(_ entry: NewEntry) async throws {
        var request = try makeRequest("api/entries")
        request.httpBody = try Self.encoder.encode(entry)
        _ = try await send(request)
    }

    // MARK: - Plumbing

    private static let encoder: JSONEncoder = {
        let encoder = JSONEncoder()
        encoder.keyEncodingStrategy = .convertToSnakeCase
        return encoder
    }()

    private static let decoder: JSONDecoder = {
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        return decoder
    }()

    private func makeRequest(_ path: String) throws -> URLRequest {
        guard settings.isComplete, let server = settings.serverURL else {
            throw StudioError("Open the Open Studio app and enter the server address and owner token first.")
        }
        var request = URLRequest(url: server.appending(path: path))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(settings.ownerToken)", forHTTPHeaderField: "Authorization")
        return request
    }

    private func send(_ request: URLRequest) async throws -> Data {
        let (data, response) = try await URLSession.shared.data(for: request)
        try Self.check(response, data)
        return data
    }

    private static func check(_ response: URLResponse, _ data: Data) throws {
        let status = (response as? HTTPURLResponse)?.statusCode ?? 0
        if (200..<300).contains(status) { return }
        if status == 401 {
            throw StudioError("The owner token wasn't accepted. Fix it in the Open Studio app.")
        }
        // FastAPI errors look like {"detail": "..."}.
        let detail = (try? JSONDecoder().decode([String: String].self, from: data))?["detail"]
        throw StudioError(detail ?? "The server said no (status \(status)).")
    }
}

/// An error with a plain-English message that can be shown as-is.
struct StudioError: LocalizedError {
    let message: String
    init(_ message: String) { self.message = message }
    var errorDescription: String? { message }
}
