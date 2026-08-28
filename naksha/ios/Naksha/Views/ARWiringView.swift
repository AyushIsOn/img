import ARKit
import RealityKit
import simd
import SwiftUI
import UIKit

/// Projects the design onto the real room.
///
/// The plan is authored in metres on a floor plane, so placing it in the world
/// needs exactly three things from the user: an origin, a heading, and the
/// ceiling height. Everything else follows from the model.
///
/// Registration is deliberately manual and visible. Automatic alignment
/// against a scan drifts on a live building site, and a wrong overlay that
/// looks confident is worse than one the user positioned themselves.
struct ARWiringView: View {

    let design: Design

    @State private var placement = Placement()
    @State private var isPlaced = false
    @State private var visibleCircuit: String? = nil
    /// Controls collapse to a single pill, so the overlay can be filmed clean.
    @State private var showControls = true

    private var rooms: [Room] { design.plan.rooms }

    /// Plan distance between the two chosen corners, for the accuracy readout.
    private var planSpan: Double {
        guard let room = rooms.first(where: { $0.name == placement.anchorRoom })
                ?? rooms.first else { return 0 }
        let a = placement.cornerA.planPoint(in: room)
        let b = placement.cornerB.planPoint(in: room)
        return Double(hypot(b.x - a.x, b.y - a.y))
    }

    var body: some View {
        ZStack(alignment: .bottom) {
            ARContainer(design: design,
                        placement: $placement,
                        isPlaced: $isPlaced,
                        visibleCircuit: visibleCircuit)
                .ignoresSafeArea()

            VStack(spacing: 10) {
                if !isPlaced {
                    alignment
                } else if showControls {
                    controls
                        .transition(.move(edge: .bottom)
                            .combined(with: .opacity))
                } else {
                    Button { showControls = true } label: {
                        Label("Controls", systemImage: "slider.horizontal.3")
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(Theme.ink)
                            .padding(.vertical, 9)
                            .padding(.horizontal, 14)
                            .glassChip()
                    }
                    .buttonStyle(.plain)
                    .transition(.opacity)
                }
            }
            .padding(.horizontal, 16)
            .padding(.bottom, 20)
            .animation(.spring(response: 0.38, dampingFraction: 0.85),
                       value: showControls)
        }
        .navigationTitle("AR overlay")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            // Seeded from the design. A hardcoded 3.0 m put this room's 12 foot
            // ceiling a metre out, and every drop hanging off it with it.
            placement.ceilingHeight = design.plan.ceilingHeight
            if placement.anchorRoom == nil {
                placement.anchorRoom = design.plan.rooms.first?.name
            }
        }
    }

    private func banner(_ text: String) -> some View {
        Text(text)
            .font(.footnote.weight(.medium))
            .foregroundColor(.white)
            .padding(.vertical, 10)
            .padding(.horizontal, 14)
            .glassChip()
    }

    /// Two corners, in order. Each is chosen and then tapped on the floor,
    /// which is enough to fix position and rotation exactly.
    private var alignment: some View {
        VStack(spacing: 12) {
            if design.plan.rooms.count > 1 {
                banner("Which room are you standing in?")
                roomPicker
            }

            let first = placement.worldA == nil
            banner(first
                   ? "Point at the FIRST floor corner and tap"
                   : "Now the SECOND corner, along one wall")

            HStack(spacing: 8) {
                Text(first ? "Corner 1" : "Corner 2")
                    .font(.caption2.weight(.bold))
                    .foregroundColor(.white.opacity(0.75))
                ForEach(RoomCorner.allCases) { corner in
                    let selected = first ? placement.cornerA : placement.cornerB
                    chip(corner.label, active: selected == corner,
                         tint: Brand.amber) {
                        if first { placement.cornerA = corner }
                        else { placement.cornerB = corner }
                    }
                }
            }

            if !first {
                Button {
                    placement.restart()
                } label: {
                    Label("Start over", systemImage: "arrow.counterclockwise")
                        .font(.caption.weight(.semibold))
                }
                .buttonStyle(.bordered)
                .tint(.white)
            }
        }
        .padding(14)
        .glassOverlay(22)
    }

    /// Chosen before the tap, because it decides what the tap means.
    private var roomPicker: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(rooms) { room in
                    chip(room.name,
                         active: (placement.anchorRoom ?? rooms.first?.name)
                                 == room.name,
                         tint: Brand.amber) {
                        placement.anchorRoom = room.name
                    }
                }
            }
            .padding(.horizontal, 2)
        }
    }

    private var controls: some View {
        VStack(spacing: 12) {
            HStack {
                Text("Standing in")
                    .font(.caption).foregroundStyle(.white.opacity(0.8))
                Spacer()
                Text(placement.anchorRoom ?? rooms.first?.name ?? "?")
                    .font(.caption.weight(.bold)).foregroundStyle(Brand.gold)
                Toggle("", isOn: $placement.onlyAnchorRoom)
                    .labelsHidden()
                    .tint(Brand.amber)
                Text(placement.onlyAnchorRoom ? "this room" : "whole floor")
                    .font(.caption2).foregroundStyle(.white.opacity(0.7))
                    .frame(width: 68, alignment: .leading)
            }
            // Rotation is solved from the two corners, so there is nothing to
            // set here. What is worth showing is how well the tapped span
            // agrees with the plan, which is a direct read on accuracy.
            if let measured = placement.measuredSpan {
                HStack(spacing: 6) {
                    Image(systemName: "ruler")
                        .font(.system(size: 10, weight: .bold))
                    Text(String(format: "measured %.2f m", measured))
                        .font(.caption.monospacedDigit())
                    Text(String(format: "· plan %.2f m", planSpan))
                        .font(.caption2.monospacedDigit())
                        .foregroundColor(.white.opacity(0.6))
                    Spacer()
                    Text(String(format: "%+.1f%%",
                                planSpan > 0
                                ? (Double(measured) - planSpan) / planSpan * 100
                                : 0))
                        .font(.caption2.monospacedDigit().weight(.bold))
                        .foregroundColor(Brand.gold)
                }
                .foregroundColor(.white.opacity(0.85))
            }
            HStack {
                Text("Ceiling")
                    .font(.caption).foregroundColor(.white.opacity(0.8))
                Slider(value: $placement.ceilingHeight, in: 2.0...4.5)
                Text(String(format: "%.2f m", placement.ceilingHeight))
                    .font(.caption.monospacedDigit())
                    .foregroundColor(.white)
                    .frame(width: 52, alignment: .trailing)
            }
            // A tap lands where ARKit thinks the floor is, and the room centre
            // is only as good as the scan, so the overlay will sit a little
            // off. These slide it onto the conduit and boxes actually on the
            // wall instead of pretending the registration is exact.
            HStack {
                Text("Slide X")
                    .font(.caption).foregroundColor(.white.opacity(0.8))
                Slider(value: $placement.nudgeX, in: -3...3)
                Text(String(format: "%+.2f", placement.nudgeX))
                    .font(.caption.monospacedDigit())
                    .foregroundColor(.white)
                    .frame(width: 52, alignment: .trailing)
            }
            HStack {
                Text("Slide Z")
                    .font(.caption).foregroundColor(.white.opacity(0.8))
                Slider(value: $placement.nudgeZ, in: -3...3)
                Text(String(format: "%+.2f", placement.nudgeZ))
                    .font(.caption.monospacedDigit())
                    .foregroundColor(.white)
                    .frame(width: 52, alignment: .trailing)
            }
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    chip("All", active: visibleCircuit == nil) {
                        visibleCircuit = nil
                    }
                    ForEach(Array(design.circuits.enumerated()), id: \.1.id) { i, c in
                        chip(c.id, active: visibleCircuit == c.id,
                             tint: Theme.circuitAccent(i)) {
                            visibleCircuit = (visibleCircuit == c.id) ? nil : c.id
                        }
                    }
                }
            }
            HStack(spacing: 10) {
                Button {
                    isPlaced = false
                    placement.restart()
                } label: {
                    Label("Reposition", systemImage: "arrow.counterclockwise")
                        .font(.caption.weight(.semibold))
                }
                .buttonStyle(.bordered)
                .tint(.white)

                // Everything is aligned by the time it is being filmed, so the
                // panel gets out of the way.
                Button { showControls = false } label: {
                    Label("Hide", systemImage: "chevron.down")
                        .font(.caption.weight(.semibold))
                }
                .buttonStyle(.bordered)
                .tint(.white)
            }
        }
        .padding(14)
        .glassOverlay(24)
    }

    private func chip(_ title: String, active: Bool,
                      tint: Color = .white,
                      action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title)
                .font(.caption2.weight(.semibold))
                .padding(.vertical, 7).padding(.horizontal, 12)
                .background(Capsule().fill(active ? tint : .clear))
                .glassChip(tint: active ? tint : nil)
                .foregroundColor(active ? .black : Theme.ink)
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Placement

/// Which corner of the room is being pointed at.
///
/// A corner is the only unambiguous landmark in a room: you can see exactly
/// where two walls meet the floor. The centre of a room cannot be pointed at
/// accurately, and in a furnished room it is usually under something.
enum RoomCorner: String, CaseIterable, Identifiable {
    case w4w3, w3w2, w2w1, w1w4

    var id: String { rawValue }

    var label: String {
        switch self {
        case .w4w3: return "W4 · W3"
        case .w3w2: return "W3 · W2"
        case .w2w1: return "W2 · W1"
        case .w1w4: return "W1 · W4"
        }
    }

    /// Wall 1 is the far wall, 2 the right, 3 the near wall, 4 the left, which
    /// is how the room was surveyed.
    func planPoint(in room: Room) -> CGPoint {
        let xs = room.cgPolygon.map(\.x), ys = room.cgPolygon.map(\.y)
        guard let x0 = xs.min(), let x1 = xs.max(),
              let y0 = ys.min(), let y1 = ys.max() else { return .zero }
        switch self {
        case .w4w3: return CGPoint(x: x0, y: y0)
        case .w3w2: return CGPoint(x: x1, y: y0)
        case .w2w1: return CGPoint(x: x1, y: y1)
        case .w1w4: return CGPoint(x: x0, y: y1)
        }
    }
}

/// How the plan is fixed to the room.
///
/// Two corner correspondences determine a rigid transform in the floor plane
/// exactly: the first fixes position, the pair fixes rotation. That replaces a
/// single tap in the middle of the floor plus a heading slider, neither of which
/// could be got right by eye, and rotation error grew with distance from the
/// anchor.
struct Placement {
    var anchorRoom: String?
    var onlyAnchorRoom: Bool = true

    /// Defaulted from the design rather than assumed. A hardcoded 3.0 m put a
    /// 12 foot ceiling a metre out, and every drop with it.
    var ceilingHeight: Double = 3.0

    /// Residual nudge, once aligned. Should rarely be needed now.
    var nudgeX: Double = 0
    var nudgeZ: Double = 0

    var cornerA: RoomCorner = .w1w4
    var cornerB: RoomCorner = .w2w1
    var worldA: SIMD3<Float>?
    var worldB: SIMD3<Float>?

    var isAligned: Bool { worldA != nil && worldB != nil }

    /// Which corner the next tap records.
    var awaiting: RoomCorner? {
        if worldA == nil { return cornerA }
        if worldB == nil { return cornerB }
        return nil
    }

    mutating func record(_ world: SIMD3<Float>) {
        if worldA == nil { worldA = world }
        else if worldB == nil { worldB = world }
    }

    mutating func restart() {
        worldA = nil
        worldB = nil
        nudgeX = 0
        nudgeZ = 0
    }

    /// Distance between the two tapped corners, for comparison with the plan.
    var measuredSpan: Float? {
        guard let a = worldA, let b = worldB else { return nil }
        return simd_length(SIMD2(b.x - a.x, b.z - a.z))
    }
}

/// The plan to world map, solved from the two corners.
///
/// Plan y runs away from the near wall and ARKit z runs towards the camera, so
/// the plan is first mirrored in y and then rotated. Held as a struct so the
/// solve happens once per render rather than per point.
struct PlanTransform {
    let originXZ: SIMD2<Float>
    let floorY: Float
    let planAnchor: SIMD2<Float>
    let cos: Float
    let sin: Float
    let nudge: SIMD2<Float>

    init?(placement: Placement, room: Room) {
        guard let a = placement.worldA, let b = placement.worldB else {
            return nil
        }
        let planA = placement.cornerA.planPoint(in: room)
        let planB = placement.cornerB.planPoint(in: room)

        // Mirror y so plan and world agree on handedness before rotating.
        let uA = SIMD2<Float>(Float(planA.x), Float(-planA.y))
        let uB = SIMD2<Float>(Float(planB.x), Float(-planB.y))
        let planVec = uB - uA
        let worldVec = SIMD2<Float>(b.x - a.x, b.z - a.z)
        guard simd_length(planVec) > 0.05, simd_length(worldVec) > 0.05 else {
            return nil
        }

        // A rotation of theta about +Y reduces the angle in the xz plane by
        // theta, so theta is the plan angle less the world angle.
        let theta = atan2(planVec.y, planVec.x) - atan2(worldVec.y, worldVec.x)
        cos = Foundation.cos(theta)
        sin = Foundation.sin(theta)
        originXZ = SIMD2(a.x, a.z)
        floorY = a.y
        planAnchor = uA
        nudge = SIMD2(Float(placement.nudgeX), Float(placement.nudgeZ))
    }

    /// A plan point at `height` above the floor, in world space.
    func world(_ p: CGPoint, _ height: Float) -> SIMD3<Float> {
        let d = SIMD2<Float>(Float(p.x), Float(-p.y)) - planAnchor
        let x = d.x * cos + d.y * sin
        let z = -d.x * sin + d.y * cos
        return SIMD3(originXZ.x + x + nudge.x,
                     floorY + height,
                     originXZ.y + z + nudge.y)
    }
}

// MARK: - ARView bridge

struct ARContainer: UIViewRepresentable {

    let design: Design
    @Binding var placement: Placement
    @Binding var isPlaced: Bool
    let visibleCircuit: String?

    func makeCoordinator() -> Coordinator {
        Coordinator(design: design,
                    onTapFloor: { world in
                        placement.record(world)
                        isPlaced = placement.isAligned
                    })
    }

    func makeUIView(context: Context) -> ARView {
        let view = ARView(frame: .zero, cameraMode: .ar,
                          automaticallyConfigureSession: false)
        let config = ARWorldTrackingConfiguration()
        config.planeDetection = [.horizontal, .vertical]
        config.environmentTexturing = .automatic
        if ARWorldTrackingConfiguration.supportsSceneReconstruction(.mesh) {
            config.sceneReconstruction = .mesh
        }
        if type(of: config).supportsFrameSemantics(.sceneDepth) {
            config.frameSemantics.insert(.sceneDepth)
        }
        view.session.run(config)
        view.environment.sceneUnderstanding.options.insert(.occlusion)

        let tap = UITapGestureRecognizer(
            target: context.coordinator,
            action: #selector(Coordinator.handleTap(_:)))
        view.addGestureRecognizer(tap)
        context.coordinator.arView = view
        return view
    }

    func updateUIView(_ view: ARView, context: Context) {
        context.coordinator.render(placement: placement,
                                   visibleCircuit: visibleCircuit)
    }

    // MARK: Coordinator

    final class Coordinator: NSObject {
        let design: Design
        let onTapFloor: (SIMD3<Float>) -> Void
        weak var arView: ARView?
        private var root: AnchorEntity?

        init(design: Design,
             onTapFloor: @escaping (SIMD3<Float>) -> Void) {
            self.design = design
            self.onTapFloor = onTapFloor
        }

        @objc func handleTap(_ gesture: UITapGestureRecognizer) {
            guard let view = arView else { return }
            let location = gesture.location(in: view)
            let hits = view.raycast(from: location,
                                    allowing: .estimatedPlane,
                                    alignment: .horizontal)
            guard let hit = hits.first else { return }
            let t = hit.worldTransform.columns.3
            onTapFloor(SIMD3(t.x, t.y, t.z))
        }

        /// Rebuilds the overlay. Cheap enough at house scale to redraw wholesale
        /// rather than diff, which keeps the state handling simple.
        func render(placement: Placement, visibleCircuit: String?) {
            guard let view = arView else { return }
            root?.removeFromParent()
            root = nil

            let room = design.plan.rooms.first {
                $0.name == placement.anchorRoom
            } ?? design.plan.rooms.first
            guard let room,
                  let map = PlanTransform(placement: placement, room: room)
            else { return }

            let anchor = AnchorEntity(world: .zero)
            let ceiling = Float(placement.ceilingHeight)
            let onlyHere = placement.onlyAnchorRoom

            // The room outline itself, at the ceiling line. Gives the overlay
            // something to read against, and makes any misalignment obvious
            // rather than leaving the runs floating unexplained.
            let corners = room.cgPolygon
            for i in corners.indices {
                let a = corners[i], b = corners[(i + 1) % corners.count]
                if let edge = Self.conduit(from: map.world(a, ceiling),
                                           to: map.world(b, ceiling),
                                           colour: Palette.outline,
                                           thickness: 0.016) {
                    anchor.addChild(edge)
                }
            }

            for (i, circuit) in design.circuits.enumerated() {
                if let only = visibleCircuit, only != circuit.id { continue }
                let colour = Palette.uiColor(i)

                for (a, b) in circuit.segments {
                    if onlyHere {
                        let mid = CGPoint(x: (a.x + b.x) / 2,
                                          y: (a.y + b.y) / 2)
                        if !room.contains(mid) { continue }
                    }
                    if let run = Self.conduit(from: map.world(a, ceiling),
                                              to: map.world(b, ceiling),
                                              colour: colour) {
                        anchor.addChild(run)
                    }
                }

                let ids = Set(circuit.pointIDs)
                for point in design.points where ids.contains(point.id) {
                    if onlyHere, point.room != room.name { continue }
                    let y = point.kind.isCeilingMounted
                        ? ceiling : Float(point.height)
                    let pos = map.world(point.point, y)
                    let marker = Self.marker(for: point.kind, colour: colour)
                    marker.position = pos
                    anchor.addChild(marker)

                    let caption = point.watts > 0
                        ? "\(point.label)  \(Int(point.watts))W"
                        : point.label
                    if let tag = Self.caption(caption, colour: colour) {
                        tag.position = pos + SIMD3<Float>(0, 0.10, 0)
                        anchor.addChild(tag)
                    }

                    if !point.kind.isCeilingMounted {
                        let top = SIMD3<Float>(pos.x, map.floorY + ceiling,
                                               pos.z)
                        if let drop = Self.conduit(from: top, to: pos,
                                                   colour: colour) {
                            anchor.addChild(drop)
                        }
                    }
                }
            }

            let boardHere = room.contains(design.boardPoint)
            if !onlyHere || boardHere {
                let board = ModelEntity(
                    mesh: .generateBox(size: [0.30, 0.40, 0.10],
                                       cornerRadius: 0.01),
                    materials: [Self.glow(Palette.accent)])
                let pos = map.world(design.boardPoint, 1.5)
                board.position = pos
                anchor.addChild(board)
                if let tag = Self.caption(
                    "DB  \(design.circuits.count) ways",
                    colour: Palette.accent) {
                    tag.position = pos + SIMD3<Float>(0, 0.30, 0)
                    anchor.addChild(tag)
                }
            }

            view.scene.addAnchor(anchor)
            root = anchor
        }

        // MARK: Geometry helpers

        /// A conduit run drawn as a thin box between two points.
        static func conduit(from a: SIMD3<Float>, to b: SIMD3<Float>,
                            colour: UIColor,
                            thickness: Float = 0.040) -> ModelEntity? {
            let delta = b - a
            let length = simd_length(delta)
            guard length > 0.01 else { return nil }
            // Real conduit is about 20 mm, but at that size against a lit
            // white ceiling it disappears on camera. This is a guidance
            // overlay, not a scale model, so it is drawn thicker.
            let mesh = MeshResource.generateBox(
                size: [thickness, thickness, length],
                cornerRadius: thickness * 0.45)
            let entity = ModelEntity(
                mesh: mesh,
                materials: [Self.glow(colour)])
            entity.position = (a + b) / 2
            // point the box's z axis along the run
            let dir = simd_normalize(delta)
            let reference = SIMD3<Float>(0, 0, 1)
            let dot = simd_dot(reference, dir)
            if dot > 0.9999 {
                entity.transform.rotation = simd_quatf(angle: 0, axis: [0, 1, 0])
            } else if dot < -0.9999 {
                entity.transform.rotation = simd_quatf(angle: .pi, axis: [0, 1, 0])
            } else {
                let axis = simd_normalize(simd_cross(reference, dir))
                entity.transform.rotation = simd_quatf(angle: acos(dot), axis: axis)
            }
            return entity
        }

        static func marker(for kind: PointKind,
                           colour: UIColor) -> ModelEntity {
            let mesh: MeshResource
            switch kind {
            case .light:
                mesh = .generateSphere(radius: 0.075)
            case .fan:
                mesh = .generateSphere(radius: 0.105)
            case .switchboard:
                mesh = .generateBox(size: [0.13, 0.13, 0.035], cornerRadius: 0.008)
            case .socket:
                mesh = .generateBox(size: [0.11, 0.11, 0.035], cornerRadius: 0.008)
            case .appliance:
                mesh = .generateBox(size: [0.15, 0.15, 0.045], cornerRadius: 0.010)
            }
            return ModelEntity(mesh: mesh, materials: [Self.glow(colour)])
        }

        /// A caption floating beside a fitting.
        ///
        /// Text meshes are laid out from a baseline at the left, so the entity
        /// is recentred on its own bounds. Without that every label sits
        /// progressively further right the longer it is.
        static func caption(_ text: String, colour: UIColor) -> ModelEntity? {
            guard !text.isEmpty else { return nil }
            let mesh = MeshResource.generateText(
                text,
                extrusionDepth: 0.0008,
                font: .systemFont(ofSize: 0.022, weight: .semibold),
                containerFrame: .zero,
                alignment: .center,
                lineBreakMode: .byTruncatingTail)
            let glyphs = ModelEntity(mesh: mesh, materials: [glow(colour)])
            // Text meshes are laid out from a baseline at the left, so without
            // this every caption drifts further right the longer it is. Bounds
            // are read from the mesh rather than from the entity's visualBounds,
            // which takes an optional reference entity and needs annotating.
            glyphs.position = -mesh.bounds.center
            // The offset lives on the child, so the caller can position and
            // rotate the holder without undoing the centring.
            let holder = ModelEntity()
            holder.addChild(glyphs)
            return holder
        }

        /// Unlit, so the overlay reads at full strength regardless of the room.
        ///
        /// SimpleMaterial is shaded by the scene, and the circuit palette is
        /// tuned for white paper, so runs came out as dark grey lines on a
        /// bright ceiling and were effectively invisible. Unlit keeps the
        /// colour exactly as specified.
        static func glow(_ colour: UIColor) -> UnlitMaterial {
            UnlitMaterial(color: colour)
        }
    }
}

// MARK: - UIKit palette

enum Palette {
    static let accent = UIColor(red: 1.00, green: 0.62, blue: 0.10, alpha: 1)
    /// The room outline, deliberately quiet so it frames rather than competes.
    static let outline = UIColor(white: 1.0, alpha: 0.55)

    /// Saturated and light, unlike the print cycle.
    ///
    /// The drawing's colours are chosen for white paper. Overlaid on a camera
    /// feed of a white ceiling they read as dark grey and vanish, so AR gets its
    /// own set at full chroma.
    private static let cycle: [UIColor] = [
        UIColor(red: 1.00, green: 0.62, blue: 0.10, alpha: 1),   // brand amber
        UIColor(red: 0.20, green: 0.90, blue: 0.75, alpha: 1),   // cyan green
        UIColor(red: 0.40, green: 0.70, blue: 1.00, alpha: 1),   // sky
        UIColor(red: 1.00, green: 0.85, blue: 0.25, alpha: 1),   // gold
        UIColor(red: 0.80, green: 0.55, blue: 1.00, alpha: 1),   // violet
        UIColor(red: 0.35, green: 1.00, blue: 0.55, alpha: 1),   // mint
        UIColor(red: 1.00, green: 0.45, blue: 0.45, alpha: 1),   // coral
        UIColor(red: 0.65, green: 1.00, blue: 0.35, alpha: 1),   // lime
        UIColor(red: 1.00, green: 0.70, blue: 0.40, alpha: 1),   // apricot
        UIColor(red: 0.45, green: 0.90, blue: 1.00, alpha: 1),   // ice
    ]

    static func uiColor(_ index: Int) -> UIColor {
        cycle[index % cycle.count]
    }
}
