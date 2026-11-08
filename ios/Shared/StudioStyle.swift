/**
 * StudioStyle: the site's look for the phone, copied from the tokens at the top
 * of frontend/src/styles/global.css: dark ink on warm off-white paper (light ink
 * on warm near-black when the phone is in dark mode, the site's "auto"), the
 * Swiss red accent and the shaded paper kept for controls, Inter in a few
 * sizes, one line of body text as the unit of space, the solid square that
 * marks a pick, and the quiet motion curves.
 *
 * Change the phone's look here, never in a view. Every view in the app and the
 * share extension uses it. The Inter files are in Shared/Fonts, listed under
 * UIAppFonts in project.yml.
 */

import SwiftUI
import UIKit

enum StudioStyle {
    // MARK: - Color: ink, paper, and the controls' two accents

    // Each is (light, dark), as :root and :root[data-theme="dark"] on the site.
    static let paper = color(light: 0xF3F1EC, dark: 0x151412)
    static let ink = color(light: 0x141414, dark: 0xEBE8E1)
    static let inkSoft = color(light: 0x141414, dark: 0xEBE8E1, lightOpacity: 0.52, darkOpacity: 0.55)
    static let inkFaint = color(light: 0x141414, dark: 0xEBE8E1, lightOpacity: 0.18, darkOpacity: 0.2)
    /// The space you're in: its word sits on a square of this.
    static let accent = color(light: 0xC43A22, dark: 0xE2593D)
    /// Under the control band.
    static let paperShade = color(light: 0xEBE8E1, dark: 0x1F1D1A)

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
    /// Around a word on a pick square (the site's --square-padding, 0.4em).
    static let squarePadding: CGFloat = 6

    // MARK: - Motion: arrive decelerating, leave accelerating, no overshoot

    static let arrive = Animation.timingCurve(0.2, 0, 0, 1, duration: 0.35)
    static let quick = Animation.timingCurve(0.2, 0, 0, 1, duration: 0.2)
    static let leave = Animation.timingCurve(0.3, 0, 1, 1, duration: 0.25)

    /// A color that follows the phone's light or dark setting.
    private static func color(light: UInt32, dark: UInt32, lightOpacity: CGFloat = 1, darkOpacity: CGFloat = 1) -> Color {
        Color(uiColor: UIColor { traits in
            traits.userInterfaceStyle == .dark ? rgb(dark, opacity: darkOpacity) : rgb(light, opacity: lightOpacity)
        })
    }

    private static func rgb(_ hex: UInt32, opacity: CGFloat) -> UIColor {
        UIColor(
            red: CGFloat((hex >> 16) & 0xFF) / 255,
            green: CGFloat((hex >> 8) & 0xFF) / 255,
            blue: CGFloat(hex & 0xFF) / 255,
            alpha: opacity
        )
    }
}

extension View {
    /// Paper, ink and body type for a whole screen. Light or dark with the phone.
    func studioPage() -> some View {
        self
            .font(StudioStyle.bodyFont)
            .lineSpacing(StudioStyle.leading)
            .foregroundStyle(StudioStyle.ink)
            .tint(StudioStyle.ink)
            .buttonStyle(.plain)
            .background(StudioStyle.paper)
    }

    /// A word on a square, the site's `.square`: picked, it sits on a solid
    /// square of `fill` (ink for a mode or the main button, the accent for the
    /// space you're in) in paper-colored type; unpicked, it's soft ink.
    func pickSquare(isPicked: Bool, fill: Color = StudioStyle.ink) -> some View {
        self
            .foregroundStyle(isPicked ? StudioStyle.paper : StudioStyle.inkSoft)
            .padding(.horizontal, StudioStyle.squarePadding)
            .background(isPicked ? fill : Color.clear)
            .padding(.horizontal, -StudioStyle.squarePadding)
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
