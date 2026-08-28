import SwiftUI

// MARK: - Liquid Glass surfaces

/// Liquid Glass wrappers.
///
/// Every use of the iOS 26 glass API is funnelled through this file so there is
/// exactly one place to change if the deployment target moves. Each call is
/// guarded by an availability check with a material fallback, so the app still
/// builds and still looks deliberate on iOS 18 to 25 rather than losing its
/// backgrounds entirely.
extension View {

    /// A raised panel: cards, sheets, list rows.
    @ViewBuilder
    func glassCard(_ radius: CGFloat = 22, tinted: Bool = false) -> some View {
        if #available(iOS 26.0, *) {
            glassEffect(
                tinted
                    ? .regular.tint(Brand.amber.opacity(0.20)).interactive()
                    : .regular.interactive(),
                in: .rect(cornerRadius: radius))
        } else {
            background(
                RoundedRectangle(cornerRadius: radius, style: .continuous)
                    .fill(.ultraThinMaterial))
            .overlay(
                RoundedRectangle(cornerRadius: radius, style: .continuous)
                    .strokeBorder(tinted ? Brand.amber.opacity(0.35)
                                         : Brand.hairline,
                                  lineWidth: 0.8))
        }
    }

    /// A small pill: chips, tags, counters.
    @ViewBuilder
    func glassChip(tint: Color? = nil) -> some View {
        if #available(iOS 26.0, *) {
            glassEffect(tint.map { .regular.tint($0.opacity(0.28)) } ?? .regular,
                        in: .capsule)
        } else {
            background(Capsule().fill(.ultraThinMaterial))
                .overlay(Capsule().strokeBorder(
                    tint?.opacity(0.45) ?? Brand.hairline, lineWidth: 0.8))
        }
    }

    /// Floating controls laid over the camera, where the background is live
    /// video and a solid panel would block the thing being looked at.
    @ViewBuilder
    func glassOverlay(_ radius: CGFloat = 26) -> some View {
        if #available(iOS 26.0, *) {
            glassEffect(.clear.interactive(), in: .rect(cornerRadius: radius))
        } else {
            background(
                RoundedRectangle(cornerRadius: radius, style: .continuous)
                    .fill(.ultraThinMaterial.opacity(0.9)))
        }
    }
}

/// Groups sibling glass views so their edges merge instead of stacking, which
/// is the whole point of the effect. Falls back to a plain layout.
struct GlassGroup<Content: View>: View {
    var spacing: CGFloat = 12
    @ViewBuilder var content: Content

    var body: some View {
        if #available(iOS 26.0, *) {
            GlassEffectContainer(spacing: spacing) {
                VStack(spacing: spacing) { content }
            }
        } else {
            VStack(spacing: spacing) { content }
        }
    }
}

// MARK: - Buttons

/// The primary action. Brand gradient, because on glass a flat fill reads as
/// disabled.
struct VGuardProminentButton: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.subheadline.weight(.bold))
            .foregroundStyle(Color.black)
            .padding(.vertical, 15)
            .padding(.horizontal, 20)
            .frame(maxWidth: .infinity)
            .background(Brand.markGradient, in: .capsule)
            .overlay(Capsule().strokeBorder(Brand.paleGold.opacity(0.5),
                                            lineWidth: 0.7))
            .shadow(color: Brand.amber.opacity(0.35), radius: 14, y: 5)
            .scaleEffect(configuration.isPressed ? 0.97 : 1)
            .opacity(configuration.isPressed ? 0.9 : 1)
            .animation(.spring(response: 0.3, dampingFraction: 0.7),
                       value: configuration.isPressed)
    }
}

/// The secondary action, on glass.
struct VGuardGlassButton: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.subheadline.weight(.semibold))
            .foregroundStyle(Theme.ink)
            .padding(.vertical, 14)
            .padding(.horizontal, 20)
            .frame(maxWidth: .infinity)
            .glassChip()
            .scaleEffect(configuration.isPressed ? 0.97 : 1)
            .animation(.spring(response: 0.3, dampingFraction: 0.7),
                       value: configuration.isPressed)
    }
}

extension ButtonStyle where Self == VGuardProminentButton {
    static var vguard: VGuardProminentButton { VGuardProminentButton() }
}

extension ButtonStyle where Self == VGuardGlassButton {
    static var vguardGlass: VGuardGlassButton { VGuardGlassButton() }
}

// MARK: - Animated backdrop

/// The waving gradient behind everything.
///
/// A mesh gradient with the corner control points pinned and the interior ones
/// drifting on slow sine waves, which is what produces the fabric-like motion
/// without any shader work. Amber over black, so it reads as the brand rather
/// than as decoration.
///
/// Motion is disabled under Reduce Motion, and the timeline runs at 20 fps
/// rather than display rate because this is a background and nobody is looking
/// for a crisp 120 Hz on it.
struct VGuardBackdrop: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        ZStack {
            Brand.void

            if reduceMotion {
                mesh(at: 0)
            } else {
                TimelineView(.animation(minimumInterval: 1.0 / 20.0)) { context in
                    mesh(at: context.date.timeIntervalSinceReferenceDate)
                }
            }

            // Sink the corners so foreground glass keeps its contrast.
            RadialGradient(
                colors: [.clear, Brand.void.opacity(0.75)],
                center: .center, startRadius: 120, endRadius: 620)
        }
        .ignoresSafeArea()
    }

    private func mesh(at t: TimeInterval) -> some View {
        MeshGradient(width: 3, height: 3,
                     points: Self.points(at: t),
                     colors: Self.colours,
                     smoothsColors: true)
        .blur(radius: 28)
    }

    /// Corners stay pinned or the gradient tears away from the screen edge.
    /// Edge midpoints slide along their edge, and only the centre moves freely.
    private static func points(at t: TimeInterval) -> [SIMD2<Float>] {
        func wave(_ speed: Double, _ amplitude: Double,
                  _ phase: Double) -> Float {
            Float(sin(t * speed + phase) * amplitude)
        }
        return [
            SIMD2(0, 0),
            SIMD2(0.5 + wave(0.29, 0.17, 0.0), 0),
            SIMD2(1, 0),

            SIMD2(0, 0.5 + wave(0.24, 0.15, 1.4)),
            SIMD2(0.5 + wave(0.37, 0.19, 2.1),
                  0.5 + wave(0.33, 0.17, 0.7)),
            SIMD2(1, 0.5 + wave(0.27, 0.15, 3.0)),

            SIMD2(0, 1),
            SIMD2(0.5 + wave(0.31, 0.17, 4.2), 1),
            SIMD2(1, 1),
        ]
    }

    private static let colours: [Color] = [
        .black, Brand.deep.opacity(0.42), .black,
        Brand.amber.opacity(0.34), Brand.gold.opacity(0.52),
        Brand.deep.opacity(0.38),
        .black, Brand.amber.opacity(0.26), .black,
    ]
}

/// Applies the backdrop and forces dark chrome. Used once per screen root so
/// the gradient is continuous rather than restarting inside every subview.
struct VGuardScreen<Content: View>: View {
    @ViewBuilder var content: Content

    var body: some View {
        content
            .background(VGuardBackdrop())
            .preferredColorScheme(.dark)
            .tint(Brand.amber)
    }
}

// MARK: - Small shared pieces

/// A label whose text is filled with the brand gradient. For headings only:
/// gradient body text is unreadable and fails contrast.
struct BrandText: View {
    let text: String
    var size: CGFloat = 22

    var body: some View {
        Text(text)
            .font(Brand.display(size))
            .foregroundStyle(Brand.markGradient)
    }
}

/// A section heading in the brand's voice.
struct SectionLabel: View {
    let text: String

    var body: some View {
        Text(text.uppercased())
            .font(.system(size: 11, weight: .bold))
            .tracking(1.3)
            .foregroundStyle(Brand.amber.opacity(0.85))
    }
}
