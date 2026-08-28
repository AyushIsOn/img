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

    var body: some View {
        ZStack(alignment: .bottom) {
            ARContainer(design: design,
                        placement: $placement,
                        isPlaced: $isPlaced,
                        visibleCircuit: visibleCircuit)
                .ignoresSafeArea()

            VStack(spacing: 10) {
                if !isPlaced {
                    VStack(spacing: 10) {
                        banner("Which room are you standing in?")
                        roomPicker
                        banner("Now point at the floor and tap.")
                    }
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
    }

    private func banner(_ text: String) -> some View {
        Text(text)
            .font(.footnote.weight(.medium))
            .foregroundColor(.white)
            .padding(.vertical, 10)
            .padding(.horizontal, 14)
            .glassChip()
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
            HStack {
                Text("Rotate")
                    .font(.caption).foregroundColor(.white.opacity(0.8))
                Slider(value: $placement.headingDegrees, in: 0...360)
                Text("\(Int(placement.headingDegrees))\u{00B0}")
                    .font(.caption.monospacedDigit())
                    .foregroundColor(.white)
                    .frame(width: 38, alignment: .trailing)
            }
            HStack {
                Text("Ceiling")
                    .font(.caption).foregroundColor(.white.opacity(0.8))
                Slider(value: $placement.ceilingHeight, in: 2.2...3.6)
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
                    placement.origin = nil
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

struct Placement {
    /// World transform of the anchor, set by the first tap.
    var origin: simd_float4x4? = nil
    var headingDegrees: Double = 0
    var ceilingHeight: Double = 3.0

    /// The room the user is standing in.
    ///
    /// This is the fix for the overlay appearing in the wrong place. The plan
    /// is authored in floor coordinates whose origin is a corner of the whole
    /// floor, so anchoring plan (0,0) to the tap put every other room as far
    /// away as it sits on the drawing, frequently through a wall or outside the
    /// building. Anchoring the chosen room's centre instead means the wiring
    /// lands in the room you are actually standing in.
    var anchorRoom: String? = nil

    /// Show only the anchored room. The rest of the house is still correct
    /// relative to it, but on site one room at a time is what you want.
    var onlyAnchorRoom: Bool = true

    /// Manual nudge, in metres, applied after the heading.
    ///
    /// A tap lands where ARKit thinks the floor is and the room centre is only
    /// as good as the scan, so the overlay will sit a little off. Rather than
    /// pretending otherwise, this lets it be slid onto the real conduit and
    /// switch boxes already on the wall.
    var nudgeX: Double = 0
    var nudgeZ: Double = 0
}

// MARK: - ARView bridge

struct ARContainer: UIViewRepresentable {

    let design: Design
    @Binding var placement: Placement
    @Binding var isPlaced: Bool
    let visibleCircuit: String?

    func makeCoordinator() -> Coordinator {
        Coordinator(design: design,
                    onPlaced: { transform in
                        placement.origin = transform
                        isPlaced = true
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
        let onPlaced: (simd_float4x4) -> Void
        weak var arView: ARView?
        private var root: AnchorEntity?

        init(design: Design, onPlaced: @escaping (simd_float4x4) -> Void) {
            self.design = design
            self.onPlaced = onPlaced
        }

        @objc func handleTap(_ gesture: UITapGestureRecognizer) {
            guard let view = arView else { return }
            let location = gesture.location(in: view)
            let hits = view.raycast(from: location,
                                    allowing: .estimatedPlane,
                                    alignment: .horizontal)
            guard let hit = hits.first else { return }
            onPlaced(hit.worldTransform)
        }

        /// Rebuilds the overlay. Cheap enough at house scale to redraw wholesale
        /// rather than diff, which keeps the state handling simple.
        func render(placement: Placement, visibleCircuit: String?) {
            guard let view = arView, let origin = placement.origin else {
                root?.removeFromParent()
                root = nil
                return
            }
            root?.removeFromParent()

            let anchor = AnchorEntity(world: origin)
            let heading = Float(placement.headingDegrees * .pi / 180)
            let spin = simd_quatf(angle: heading, axis: [0, 1, 0])
            let ceiling = Float(placement.ceilingHeight)

            // The room the user says they are standing in. Its centre becomes
            // the tap point, so the overlay lands here rather than wherever the
            // floor plan happens to have its origin.
            let room = design.plan.rooms.first {
                $0.name == placement.anchorRoom
            } ?? design.plan.rooms.first
            let datum = room?.center ?? .zero
            let onlyHere = placement.onlyAnchorRoom && room != nil

            /// Plan metres to anchor-relative world metres. Plan y runs away
            /// from the entry and ARKit z runs towards the camera, so the
            /// vertical axis is negated exactly once, here.
            let nudge = SIMD3<Float>(Float(placement.nudgeX), 0,
                                     Float(placement.nudgeZ))
            func world(_ p: CGPoint, _ y: Float) -> SIMD3<Float> {
                spin.act(SIMD3<Float>(Float(p.x - datum.x), y,
                                      Float(-(p.y - datum.y)))) + nudge
            }

            for (i, circuit) in design.circuits.enumerated() {
                if let only = visibleCircuit, only != circuit.id { continue }
                let colour = Palette.uiColor(i)

                for (a, b) in circuit.segments {
                    // A run crossing into another room is dropped when showing
                    // one room, judged on its midpoint so a run that merely
                    // clips a corner is not lost.
                    if onlyHere, let room {
                        let mid = CGPoint(x: (a.x + b.x) / 2,
                                          y: (a.y + b.y) / 2)
                        if !room.contains(mid) { continue }
                    }
                    if let run = Self.conduit(from: world(a, ceiling),
                                              to: world(b, ceiling),
                                              colour: colour) {
                        anchor.addChild(run)
                    }
                }

                let ids = Set(circuit.pointIDs)
                for point in design.points where ids.contains(point.id) {
                    if onlyHere, point.room != room?.name { continue }
                    let y = point.kind.isCeilingMounted
                        ? ceiling : Float(point.height)
                    let pos = world(point.point, y)
                    let marker = Self.marker(for: point.kind, colour: colour)
                    marker.position = pos
                    anchor.addChild(marker)

                    // A floating caption per fitting. Without these the
                    // overlay is a set of coloured blocks; with them it reads
                    // as a drawing standing in the room.
                    let caption = point.watts > 0
                        ? "\(point.label)  ·  \(Int(point.watts)) W"
                        : point.label
                    if let tag = Self.caption(caption, colour: colour) {
                        tag.position = pos + SIMD3<Float>(0, 0.14, 0)
                        tag.transform.rotation = spin
                        anchor.addChild(tag)
                    }

                    // drop from the ceiling to a wall device, so the run reads
                    // as a real chase rather than a floating line
                    if !point.kind.isCeilingMounted {
                        let top = SIMD3<Float>(pos.x, ceiling, pos.z)
                        if let drop = Self.conduit(from: top, to: pos,
                                                   colour: colour) {
                            anchor.addChild(drop)
                        }
                    }
                }
            }

            // The board, placed through the same transform. Shown only when it
            // is in this room, or when the whole floor is on, otherwise it
            // appears through a wall with nothing connecting it.
            let boardHere = room?.contains(design.boardPoint) ?? true
            if !onlyHere || boardHere {
                let board = ModelEntity(
                    mesh: .generateBox(size: [0.30, 0.40, 0.10],
                                       cornerRadius: 0.01),
                    materials: [Self.glow(Palette.accent)])
                let boardPos = world(design.boardPoint, 1.5)
                board.position = boardPos
                anchor.addChild(board)

                if let tag = Self.caption(
                    "DB  ·  \(design.circuits.count) ways",
                    colour: Palette.accent) {
                    tag.position = boardPos + SIMD3<Float>(0, 0.30, 0)
                    tag.transform.rotation = spin
                    anchor.addChild(tag)
                }
            }

            view.scene.addAnchor(anchor)
            root = anchor
        }

        // MARK: Geometry helpers

        /// A conduit run drawn as a thin box between two points.
        static func conduit(from a: SIMD3<Float>, to b: SIMD3<Float>,
                            colour: UIColor) -> ModelEntity? {
            let delta = b - a
            let length = simd_length(delta)
            guard length > 0.01 else { return nil }
            // Real conduit is about 20 mm, but at that size against a lit
            // white ceiling it disappears on camera. This is a guidance
            // overlay, not a scale model, so it is drawn thicker.
            let mesh = MeshResource.generateBox(
                size: [0.040, 0.040, length], cornerRadius: 0.018)
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
                font: .systemFont(ofSize: 0.052, weight: .semibold),
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
