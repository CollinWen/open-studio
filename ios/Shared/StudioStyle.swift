/**
 * StudioStyle: the site's look for the phone, copied from the tokens at the top
 * of frontend/src/styles/global.css: dark ink on warm off-white paper, the Swiss
 * red accent and the shaded paper kept for controls, Inter in a few sizes, one
 * line of body text as the unit of space, and the quiet motion curves.
 *
 * Change the phone's look here, never in a view. Every view in the app and the
 * share extension uses it. The Inter files are in Shared/Fonts, listed under
 * UIAppFonts in project.yml.
 */

import SwiftUI

enum StudioStyle {
    // MARK: - Color: ink, paper, and the controls' two accents

    static let paper = rgb(0xF3F1EC)
    static let ink = rgb(0x141414)
    static let inkSoft = rgb(0x141414, opacity: 0.52)
    static let inkFaint = rgb(0x141414, opacity: 0.18)
    /// The space you're in, and the underline of picked modes.
    static let accent = rgb(0xC43A22)
    /// Under the control band.
    static let paperShade = rgb(0xEBE8E1)

    // MARK: - Type: one typeface, few sizes (they still follow the phone's text size setting)

    static let smallFont = Font.custom("Inter-Regular", size: 12, relativeTo: .caption)
    static let bodyFont = Font.custom("Inter-Regular", size: 15, relativeTo: .body)
    static let largeFont = Font.custom("Inter-Regular", size: 20, relativeTo: .title3)
    static let titleFont = Font.custom("Inter-Medium", size: 20, relativeTo: .title3)
    static let siteNameFont = Font.custom("Inter-SemiBold", size: 20, relativeTo: .title3)

    // MARK: - Space: the phone sizes of the page grid

    /// One line of body text: the unit for all vertical space.
    static let line: CGFloat = 22
    /// The space between body lines that makes 15pt text sit on a 22pt line.
    static let leading: CGFloat = 4
    static let margin: CGFloat = 16
    /// Between words in a line of words (the site's 1em).
    static let wordGap: CGFloat = 15

    // MARK: - Motion: arrive decelerating, leave accelerating, no overshoot

    static let arrive = Animation.timingCurve(0.2, 0, 0, 1, duration: 0.35)
    static let quick = Animation.timingCurve(0.2, 0, 0, 1, duration: 0.2)
    static let leave = Animation.timingCurve(0.3, 0, 1, 1, duration: 0.25)
    static let breathe = Animation.easeInOut(duration: 1.6).repeatForever(autoreverses: true)

    private static func rgb(_ hex: UInt32, opacity: Double = 1) -> Color {
        Color(
            red: Double((hex >> 16) & 0xFF) / 255,
            green: Double((hex >> 8) & 0xFF) / 255,
            blue: Double(hex & 0xFF) / 255,
            opacity: opacity
        )
    }
}

extension View {
    /// Paper, ink and body type for a whole screen. Always light, like the site.
    func studioPage() -> some View {
        self
            .font(StudioStyle.bodyFont)
            .lineSpacing(StudioStyle.leading)
            .foregroundStyle(StudioStyle.ink)
            .tint(StudioStyle.ink)
            .buttonStyle(.plain)
            .background(StudioStyle.paper)
            .preferredColorScheme(.light)
    }

    /// A text field with no box: just a faint rule under it, full ink while typing.
    func ruledField(isFocused: Bool = false) -> some View {
        self
            .padding(.bottom, 4)
            .overlay(alignment: .bottom) {
                Rectangle()
                    .fill(isFocused ? StudioStyle.ink : StudioStyle.inkFaint)
                    .frame(height: 1)
            }
            .animation(StudioStyle.quick, value: isFocused)
    }
}
