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
                drawFixtures(&ctx, t)
                drawOpenings(&ctx, t)
                if showCircuits { drawRoutes(&ctx, t) }
                drawPoints(&ctx, t)
                drawBoard(&ctx, t)
            }
            .background(Theme.paper)
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
                        .foregroundColor(Theme.paperInk),
                     at: CGPoint(x: c.x, y: c.y - 7))
            ctx.draw(Text(String(format: "%.1f m\u{00B2}", room.area))
                        .font(.system(size: 7))
                        .foregroundColor(Theme.paperMuted),
                     at: CGPoint(x: c.x, y: c.y + 4))
        }
    }

    /// Built-in joinery, hatched. An electrician needs to see it because a wall
    /// with a fitted wardrobe against it cannot be chased.
    private func drawFixtures(_ ctx: inout GraphicsContext, _ t: Transform) {
        for fixture in design.plan.fixtures {
            let pts = fixture.cgPolygon.map(t.apply)
            guard let first = pts.first else { continue }
            var path = Path()
            path.move(to: first)
            for p in pts.dropFirst() { path.addLine(to: p) }
            path.closeSubpath()
            ctx.fill(path, with: .color(Theme.paperMuted.opacity(0.10)))
            ctx.stroke(path, with: .color(Theme.paperMuted),
                       style: StrokeStyle(lineWidth: 0.9, dash: [3, 2]))

        }
    }

    /// Doors as a swing arc, windows as the conventional triple line.
    ///
    /// Both are drawn by erasing the wall across the opening first, which is
    /// what makes a plan read as a plan rather than as a box with symbols on it.
    private func drawOpenings(_ ctx: inout GraphicsContext, _ t: Transform) {
        for door in design.plan.doors {
            guard let (along, normal) = wallAxes(at: door.point) else { continue }
            let c = t.apply(door.point)
            let half = door.width * t.scale / 2

            // clear the wall through the opening
            var gap = Path()
            gap.move(to: CGPoint(x: c.x - along.dx * half,
                                 y: c.y - along.dy * half))
            gap.addLine(to: CGPoint(x: c.x + along.dx * half,
                                    y: c.y + along.dy * half))
            ctx.stroke(gap, with: .color(Theme.paper),
                       style: StrokeStyle(lineWidth: 3.4, lineCap: .butt))

            // Leaf and swing, drawn into the room. Kept to two thirds of the
            // opening: a true full-width arc is correct on a large-format
            // drawing but dominates the sheet at phone size.
            let reach = half * 1.3
            let hinge = CGPoint(x: c.x - along.dx * half,
                                y: c.y - along.dy * half)
            let leafEnd = CGPoint(x: hinge.x + normal.dx * reach,
                                  y: hinge.y + normal.dy * reach)
            var leaf = Path()
            leaf.move(to: hinge)
            leaf.addLine(to: leafEnd)
            ctx.stroke(leaf, with: .color(Theme.wall), lineWidth: 0.9)

            var arc = Path()
            arc.move(to: leafEnd)
            arc.addQuadCurve(
                to: CGPoint(x: hinge.x + along.dx * reach,
                            y: hinge.y + along.dy * reach),
                control: CGPoint(x: hinge.x + (along.dx + normal.dx) * reach * 0.78,
                                 y: hinge.y + (along.dy + normal.dy) * reach * 0.78))
            ctx.stroke(arc, with: .color(Theme.paperMuted),
                       style: StrokeStyle(lineWidth: 0.6, dash: [2, 2]))
        }

        for window in design.plan.windows {
            guard let (along, normal) = wallAxes(at: window.point) else { continue }
            let c = t.apply(window.point)
            let half = window.width * t.scale / 2

            var gap = Path()
            gap.move(to: CGPoint(x: c.x - along.dx * half,
                                 y: c.y - along.dy * half))
            gap.addLine(to: CGPoint(x: c.x + along.dx * half,
                                    y: c.y + along.dy * half))
            ctx.stroke(gap, with: .color(Theme.paper),
                       style: StrokeStyle(lineWidth: 3.4, lineCap: .butt))

            for offset in [-1.3, 0.0, 1.3] {
                var line = Path()
                line.move(to: CGPoint(
                    x: c.x - along.dx * half + normal.dx * offset,
                    y: c.y - along.dy * half + normal.dy * offset))
                line.addLine(to: CGPoint(
                    x: c.x + along.dx * half + normal.dx * offset,
                    y: c.y + along.dy * half + normal.dy * offset))
                ctx.stroke(line, with: .color(Theme.wall),
                           lineWidth: offset == 0 ? 0.9 : 0.6)
            }
        }
    }

    /// Which way the wall runs at a point on the perimeter, and the normal
    /// pointing into the room, both in screen space.
    ///
    /// Derived from the nearest room edge rather than assuming the wall is axis
    /// aligned, so it holds for a rotated or non rectangular plan. The inward
    /// test is done in plan space, where there is no flipped axis to reason
    /// about, and only the result is converted.
    private func wallAxes(at plan: CGPoint)
        -> (along: Axis, normal: Axis)? {
        var best: (dist: CGFloat, a: CGPoint, b: CGPoint)?
        for room in design.plan.rooms {
            let pts = room.cgPolygon
            guard pts.count > 1 else { continue }
            for i in pts.indices {
                let a = pts[i], b = pts[(i + 1) % pts.count]
                let d = distance(from: plan, toSegment: a, and: b)
                if best == nil || d < best!.dist { best = (d, a, b) }
            }
        }
        guard let edge = best else { return nil }
        let dx = edge.b.x - edge.a.x, dy = edge.b.y - edge.a.y
        let len = hypot(dx, dy)
        guard len > 0 else { return nil }

        // In plan space: the perpendicular has two directions, and the wrong
        // one sends the door swinging out of the building. Take whichever
        // points back towards the middle of the plan.
        var nx = -dy / len, ny = dx / len
        let centre = roomCentroid()
        if nx * (centre.x - plan.x) + ny * (centre.y - plan.y) < 0 {
            nx = -nx; ny = -ny
        }

        // Screen y runs the other way to plan y, so both are negated on the y
        // component and nowhere else.
        return (Axis(dx: dx / len, dy: -dy / len), Axis(dx: nx, dy: -ny))
    }

    private func roomCentroid() -> CGPoint {
        let pts = design.plan.rooms.flatMap { $0.cgPolygon }
        guard !pts.isEmpty else { return .zero }
        return CGPoint(x: pts.reduce(0) { $0 + $1.x } / CGFloat(pts.count),
                       y: pts.reduce(0) { $0 + $1.y } / CGFloat(pts.count))
    }

    private func distance(from p: CGPoint, toSegment a: CGPoint,
                          and b: CGPoint) -> CGFloat {
        let dx = b.x - a.x, dy = b.y - a.y
        let lenSq = dx * dx + dy * dy
        guard lenSq > 0 else { return hypot(p.x - a.x, p.y - a.y) }
        var u = ((p.x - a.x) * dx + (p.y - a.y) * dy) / lenSq
        u = max(0, min(1, u))
        return hypot(p.x - (a.x + u * dx), p.y - (a.y + u * dy))
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
            let colour = (index.map { Theme.circuitColour($0) } ?? Theme.paperInk)
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
                 with: .color(Theme.paperInk))
        ctx.draw(Text("DB").font(.system(size: 8, weight: .bold))
                    .foregroundColor(.white), at: p)
    }
}
