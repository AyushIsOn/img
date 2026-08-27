import SwiftUI

/// The drawing, rendered on device. Same model, same symbols and same circuit
/// colours as the PNG sheets the solver produces, so what the owner sees in the
/// app is what the electrician gets on paper.
struct PlanCanvasView: View {

    let design: Design
    var showCircuits: Bool = true
    var highlighted: String? = nil        // circuit id to emphasise

    private let inset: CGFloat = 18

    var body: some View {
        GeometryReader { geo in
            Canvas { ctx, size in
                let t = transform(for: size)
                drawRooms(&ctx, t)
                if showCircuits { drawRoutes(&ctx, t) }
                drawPoints(&ctx, t)
                drawBoard(&ctx, t)
            }
            .background(Color(white: 0.99))
        }
    }

    // MARK: - Mapping metres to points

    private struct Transform {
        let scale: CGFloat
        let offset: CGSize
        let height: CGFloat

        /// Plan y grows away from the entry; screen y grows downward, so the
        /// vertical axis is flipped here and nowhere else.
        func apply(_ p: CGPoint) -> CGPoint {
            CGPoint(x: p.x * scale + offset.width,
                    y: height - (p.y * scale + offset.height))
        }
    }

    private func transform(for size: CGSize) -> Transform {
        let b = design.plan.bounds
        guard b.width > 0, b.height > 0 else {
            return Transform(scale: 1, offset: .zero, height: size.height)
        }
        let sx = (size.width - inset * 2) / b.width
        let sy = (size.height - inset * 2) / b.height
        let scale = min(sx, sy)
        let drawn = CGSize(width: b.width * scale, height: b.height * scale)
        return Transform(
            scale: scale,
            offset: CGSize(width: (size.width - drawn.width) / 2 - b.minX * scale,
                           height: (size.height - drawn.height) / 2 - b.minY * scale),
            height: size.height)
    }

    // MARK: - Layers

    private func drawRooms(_ ctx: inout GraphicsContext, _ t: Transform) {
        for room in design.plan.rooms {
            var path = Path()
            let pts = room.cgPolygon.map(t.apply)
            guard let first = pts.first else { continue }
            path.move(to: first)
            for p in pts.dropFirst() { path.addLine(to: p) }
            path.closeSubpath()
            ctx.fill(path, with: .color(Theme.roomFill))
            ctx.stroke(path, with: .color(Theme.wall), lineWidth: 2.0)

            let c = t.apply(room.center)
            ctx.draw(Text(room.name.uppercased())
                        .font(.system(size: 8, weight: .bold))
                        .foregroundColor(Theme.ink),
                     at: CGPoint(x: c.x, y: c.y - 7))
            ctx.draw(Text(String(format: "%.1f m\u{00B2}", room.area))
                        .font(.system(size: 7))
                        .foregroundColor(Theme.muted),
                     at: CGPoint(x: c.x, y: c.y + 4))
        }
    }

    private func drawRoutes(_ ctx: inout GraphicsContext, _ t: Transform) {
        for (i, circuit) in design.circuits.enumerated() {
            let dimmed = highlighted != nil && highlighted != circuit.id
            let colour = Theme.circuitColour(i)
                .opacity(dimmed ? 0.12 : 0.85)
            var path = Path()
            for (a, b) in circuit.segments {
                path.move(to: t.apply(a))
                path.addLine(to: t.apply(b))
            }
            ctx.stroke(path, with: .color(colour),
                       style: StrokeStyle(lineWidth: dimmed ? 1.2 : 2.0,
                                          lineCap: .round))
        }
    }

    private func drawPoints(_ ctx: inout GraphicsContext, _ t: Transform) {
        for point in design.points {
            let p = t.apply(point.point)
            let index = design.circuits.firstIndex { $0.pointIDs.contains(point.id) }
            let dimmed = highlighted != nil
                && design.circuit(for: point)?.id != highlighted
            let colour = (index.map { Theme.circuitColour($0) } ?? Theme.ink)
                .opacity(dimmed ? 0.2 : 1.0)
            symbol(&ctx, point.kind, at: p, colour: colour)
        }
    }

    private func symbol(_ ctx: inout GraphicsContext, _ kind: PointKind,
                        at p: CGPoint, colour: Color) {
        let r: CGFloat = 5
        switch kind {
        case .light:
            let rect = CGRect(x: p.x - r, y: p.y - r, width: r * 2, height: r * 2)
            ctx.fill(Path(ellipseIn: rect), with: .color(.white))
            ctx.stroke(Path(ellipseIn: rect), with: .color(colour), lineWidth: 1.1)
            var cross = Path()
            let d = r * 0.7
            cross.move(to: CGPoint(x: p.x - d, y: p.y - d))
            cross.addLine(to: CGPoint(x: p.x + d, y: p.y + d))
            cross.move(to: CGPoint(x: p.x - d, y: p.y + d))
            cross.addLine(to: CGPoint(x: p.x + d, y: p.y - d))
            ctx.stroke(cross, with: .color(colour), lineWidth: 0.9)

        case .fan:
            let rect = CGRect(x: p.x - r - 1, y: p.y - r - 1,
                              width: (r + 1) * 2, height: (r + 1) * 2)
            ctx.fill(Path(ellipseIn: rect), with: .color(.white))
            ctx.stroke(Path(ellipseIn: rect), with: .color(colour), lineWidth: 1.1)
            var blades = Path()
            for (dx, dy) in [(r, 0.0), (0.0, r), (-r, 0.0), (0.0, -r)] {
                blades.move(to: p)
                blades.addLine(to: CGPoint(x: p.x + dx, y: p.y + dy))
            }
            ctx.stroke(blades, with: .color(colour), lineWidth: 1.0)

        case .switchboard:
            let rect = CGRect(x: p.x - 4, y: p.y - 4, width: 8, height: 8)
            ctx.fill(Path(rect), with: .color(colour))

        case .socket:
            var arc = Path()
            arc.addArc(center: p, radius: r, startAngle: .degrees(180),
                       endAngle: .degrees(360), clockwise: false)
            arc.closeSubpath()
            ctx.fill(arc, with: .color(.white))
            ctx.stroke(arc, with: .color(colour), lineWidth: 1.1)

        case .appliance:
            let rect = CGRect(x: p.x - 5, y: p.y - 5, width: 10, height: 10)
            ctx.fill(Path(rect), with: .color(.white))
            ctx.stroke(Path(rect), with: .color(colour), lineWidth: 1.2)
            var slash = Path()
            slash.move(to: CGPoint(x: p.x - 5, y: p.y + 5))
            slash.addLine(to: CGPoint(x: p.x + 5, y: p.y - 5))
            ctx.stroke(slash, with: .color(colour), lineWidth: 0.9)
        }
    }

    private func drawBoard(_ ctx: inout GraphicsContext, _ t: Transform) {
        let p = t.apply(design.boardPoint)
        let rect = CGRect(x: p.x - 12, y: p.y - 8, width: 24, height: 16)
        ctx.fill(Path(roundedRect: rect, cornerRadius: 2),
                 with: .color(Theme.accent))
        ctx.draw(Text("DB").font(.system(size: 8, weight: .bold))
                    .foregroundColor(.white), at: p)
    }
}

// MARK: - Shared palette

enum Theme {
    static let ink = Color(red: 0.11, green: 0.11, blue: 0.11)
    static let muted = Color(white: 0.54)
    static let accent = Color(red: 0.12, green: 0.43, blue: 0.35)
    static let roomFill = Color(red: 0.97, green: 0.965, blue: 0.957)
    static let wall = Color(red: 0.11, green: 0.11, blue: 0.11)
    static let warn = Color(red: 0.72, green: 0.28, blue: 0.16)

    /// Matches the cycle used by the Python drawing module.
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
}
