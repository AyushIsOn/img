import SwiftUI

/// The V-Guard palette, taken from the brand mark: an amber to gold gradient
/// on black.
///
/// The mark is drawn on black, so the app is dark by default. That is not a
/// stylistic preference, it is what makes the brand colour read as the accent
/// rather than as a warning, and it is the condition under which Liquid Glass
/// looks like glass instead of grey plastic.
enum Brand {

    // MARK: Core

    /// Deepest orange in the mark, used for the trailing edge of gradients.
    static let deep = Color(red: 0.878, green: 0.439, blue: 0.102)      // #E07019
    /// The primary brand amber. This is the accent colour of the app.
    static let amber = Color(red: 0.961, green: 0.608, blue: 0.110)     // #F59B1C
    /// The bright gold highlight in the mark.
    static let gold = Color(red: 1.000, green: 0.769, blue: 0.192)      // #FFC431
    /// Pale gold, for text that needs to sit above the accent.
    static let paleGold = Color(red: 1.000, green: 0.851, blue: 0.447)  // #FFD972

    // MARK: Surfaces

    static let void = Color.black
    /// Not pure black. Keeps glass edges visible where panels overlap.
    static let surface = Color(red: 0.043, green: 0.043, blue: 0.051)
    static let hairline = Color.white.opacity(0.14)

    // MARK: Gradients

    /// The wordmark gradient, deep to gold. Used for emphasis and fills.
    static let markGradient = LinearGradient(
        colors: [deep, amber, gold],
        startPoint: .bottomLeading, endPoint: .topTrailing)

    /// A softer version for large areas, so the amber does not dominate.
    static let veil = LinearGradient(
        colors: [amber.opacity(0.22), gold.opacity(0.08), .clear],
        startPoint: .topLeading, endPoint: .bottomTrailing)

    // MARK: Type

    /// San Francisco, at the weights the brand mark implies. Nothing custom is
    /// bundled: the system face is the correct one and it carries Dynamic Type,
    /// optical sizing and every localisation for free.
    static func display(_ size: CGFloat) -> Font {
        .system(size: size, weight: .bold, design: .default)
    }

    static func numeric(_ style: Font.TextStyle) -> Font {
        .system(style, design: .default).monospacedDigit()
    }
}

/// Semantic colours.
///
/// The names are unchanged from the light build so every call site still
/// compiles, but they now resolve for a dark interface. The drawing keeps its
/// own `paper` set, because a wiring diagram is reproduced on paper by the
/// electrician and has to match the sheets the solver prints.
enum Theme {

    // MARK: Interface, dark

    static let ink = Color(white: 0.96)
    static let muted = Color(white: 0.62)
    static let accent = Brand.amber
    static let warn = Color(red: 1.0, green: 0.545, blue: 0.353)

    // MARK: Drawing, light paper

    static let paperInk = Color(red: 0.11, green: 0.11, blue: 0.11)
    static let paperMuted = Color(white: 0.42)
    static let paper = Color(red: 0.98, green: 0.976, blue: 0.969)
    static let roomFill = Color(red: 0.97, green: 0.965, blue: 0.957)
    static let wall = Color(red: 0.11, green: 0.11, blue: 0.11)

    // MARK: Circuits

    /// Matches the cycle used by the Python drawing module, so the on screen
    /// drawing and the printed sheet colour circuits identically.
    private static let cycle: [Color] = [
        Color(red: 0.12, green: 0.43, blue: 0.35),
        Color(red: 0.72, green: 0.28, blue: 0.16),
        Color(red: 0.18, green: 0.36, blue: 0.54),
        Color(red: 0.54, green: 0.43, blue: 0.12),
        Color(red: 0.42, green: 0.25, blue: 0.54),
        Color(red: 0.25, green: 0.54, blue: 0.49),
        Color(red: 0.66, green: 0.27, blue: 0.25),
        Color(red: 0.29, green: 0.54, blue: 0.18),
        Color(red: 0.54, green: 0.35, blue: 0.18),
        Color(red: 0.18, green: 0.44, blue: 0.54),
    ]

    static func circuitColour(_ index: Int) -> Color {
        cycle[index % cycle.count]
    }

    /// Circuit colours brightened for use as interface accents on black. The
    /// print cycle is tuned for white paper and goes muddy on a dark surface,
    /// so it is mixed towards white for on screen chips and labels.
    static func circuitAccent(_ index: Int) -> Color {
        circuitColour(index).mix(with: .white, by: 0.34, in: .perceptual)
    }
}
