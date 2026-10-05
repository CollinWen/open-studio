/**
 * SharedKeychain: reads and writes small secret strings in the iOS keychain,
 * in a spot both the app and the share extension can reach (the app group).
 *
 * Used only by StudioSettings.
 */

import Foundation
import Security

enum SharedKeychain {
    private static let service = "open-studio"

    /// The app group from Info.plist (set in project.yml), so both targets read the same items.
    private static var accessGroup: String? {
        Bundle.main.object(forInfoDictionaryKey: "AppGroupID") as? String
    }

    static func read(_ key: String) -> String? {
        var query = baseQuery(for: key)
        query[kSecReturnData as String] = true
        query[kSecMatchLimit as String] = kSecMatchLimitOne
        var result: AnyObject?
        guard SecItemCopyMatching(query as CFDictionary, &result) == errSecSuccess,
              let data = result as? Data
        else { return nil }
        return String(data: data, encoding: .utf8)
    }

    static func write(_ key: String, _ value: String) {
        let query = baseQuery(for: key)
        SecItemDelete(query as CFDictionary)
        var item = query
        item[kSecValueData as String] = Data(value.utf8)
        // Readable after the phone's first unlock, so sharing works while the phone is in use.
        item[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlock
        SecItemAdd(item as CFDictionary, nil)
    }

    private static func baseQuery(for key: String) -> [String: Any] {
        var query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key,
        ]
        if let accessGroup { query[kSecAttrAccessGroup as String] = accessGroup }
        return query
    }
}
