/**
 * StudioApi: every call the phone makes to the Open Studio backend.
 *
 *   GET  /api/boards                    the boards, home first, with their agents
 *   GET  /api/entries/page?board=       a board's newest entries (to pick one to build on)
 *   POST /api/capture/link              a link -> prefilled entry draft
 *   POST /api/media                     upload one photo or video -> its URL
 *   POST /api/entries                   save a new entry on a board
 *   POST /api/entries/{id}/builds-on    say the new entry builds on an earlier one
 *
 * Every call carries the owner token. Nothing else on the phone talks to the network.
 */

import Foundation

struct StudioApi {
    let settings: StudioSettings

    func fetchBoards() async throws -> [Board] {
        let data = try await send(try makeRequest("api/boards", method: "GET"))
        return try Self.decoder.decode([Board].self, from: data)
    }

    func fetchNewestEntries(onBoard board: String, limit: Int) async throws -> [EntrySummary] {
        let query = [URLQueryItem(name: "board", value: board), URLQueryItem(name: "limit", value: String(limit))]
        let data = try await send(try makeRequest("api/entries/page", method: "GET", query: query))
        return try Self.decoder.decode(EntrySummaryPage.self, from: data).entries
    }

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

    func createEntry(_ entry: NewEntry) async throws -> EntrySummary {
        var request = try makeRequest("api/entries")
        request.httpBody = try Self.encoder.encode(entry)
        let data = try await send(request)
        return try Self.decoder.decode(EntrySummary.self, from: data)
    }

    func addBuildsOn(entryId: String, buildsOnId: String) async throws {
        var request = try makeRequest("api/entries/\(entryId)/builds-on")
        request.httpBody = try Self.encoder.encode(BuildsOn(buildsOnId: buildsOnId))
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

    private func makeRequest(_ path: String, method: String = "POST", query: [URLQueryItem] = []) throws -> URLRequest {
        guard settings.isComplete, let server = settings.serverURL else {
            throw StudioError("Open the Open Studio app and enter the server address and owner token first.")
        }
        var url = server.appending(path: path)
        if !query.isEmpty { url.append(queryItems: query) }
        var request = URLRequest(url: url)
        request.httpMethod = method
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
        // FastAPI errors look like {"detail": "..."}, or {"detail": {"message": "..."}} for a duplicate link.
        let body = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any]
        let detail = (body?["detail"] as? String) ?? ((body?["detail"] as? [String: Any])?["message"] as? String)
        throw StudioError(detail ?? "The server said no (status \(status)).")
    }
}

/// An error with a plain-English message that can be shown as-is.
struct StudioError: LocalizedError {
    let message: String
    init(_ message: String) { self.message = message }
    var errorDescription: String? { message }
}
