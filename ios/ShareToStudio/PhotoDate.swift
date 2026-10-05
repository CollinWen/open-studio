/**
 * PhotoDate: when a photo was taken, read from its EXIF data, so a photo
 * shared today lands on the site at the date it was actually taken.
 *
 * Used by PreparedMedia. (Videos get their date from AVFoundation there.)
 */

import Foundation
import ImageIO

enum PhotoDate {
    static func read(from file: URL) -> Date? {
        guard let source = CGImageSourceCreateWithURL(file as CFURL, nil),
              let properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [CFString: Any],
              let exif = properties[kCGImagePropertyExifDictionary] as? [CFString: Any],
              let taken = exif[kCGImagePropertyExifDateTimeOriginal] as? String  // "2026:10:03 18:42:07"
        else { return nil }

        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        // Newer photos also record their time zone ("-07:00"); older ones are assumed local.
        if let offset = exif[kCGImagePropertyExifOffsetTimeOriginal] as? String {
            formatter.dateFormat = "yyyy:MM:dd HH:mm:ssxxx"
            return formatter.date(from: taken + offset)
        }
        formatter.dateFormat = "yyyy:MM:dd HH:mm:ss"
        formatter.timeZone = .current
        return formatter.date(from: taken)
    }
}
