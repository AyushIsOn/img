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

    var body: some View {
        ZStack(alignment: .bottom) {
            ARContainer(design: design,
                        placement: $placement,
                        isPlaced: $isPlaced,
                        visibleCircuit: visibleCircuit)
                .ignoresSafeArea()

            VStack(spacing: 10) {
                if !isPlaced {
                    banner("Point at the floor, then tap to drop the plan origin.")
                } else {
                    controls
                }
            }
            .padding(.horizontal, 16)
            .padding(.bottom, 20)
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

    private var controls: some View {
        VStack(spacing: 12) {
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
                Slider(value: $placement.ceilingHeight, in: 2.4...3.6)
                Text(String(format: "%.2f m", placement.ceilingHeight))
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
            Button {
                isPlaced = false
                placement.origin = nil
            } label: {
                Label("Reposition", systemImage: "arrow.counterclockwise")
                    .font(.caption.weight(.semibold))
            }
            .buttonStyle(.bordered)
            .tint(.white)
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
    /// World transform of the plan origin, set by the first tap.
    var origin: simd_float4x4? = nil
    var headingDegrees: Double = 0
    var ceilingHeight: Double = 3.0
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

            for (i, circuit) in design.circuits.enumerated() {
                if let only = visibleCircuit, only != circuit.id { continue }
                let colour = Palette.uiColor(i)

                for (a, b) in circuit.segments {
                    let pa = SIMD3<Float>(Float(a.x), ceiling, Float(-a.y))
                    let pb = SIMD3<Float>(Float(b.x), ceiling, Float(-b.y))
                    if let run = Self.conduit(from: pa, to: pb, colour: colour) {
                        run.transform.rotation = spin * run.transform.rotation
                        run.position = spin.act(run.position)
                        anchor.addChild(run)
                    }
                }

                let ids = Set(circuit.pointIDs)
                for point in design.points where ids.contains(point.id) {
                    let y = point.kind.isCeilingMounted
                        ? ceiling : Float(point.height)
                    var pos = SIMD3<Float>(Float(point.point.x), y,
                                           Float(-point.point.y))
                    pos = spin.act(pos)
                    let marker = Self.marker(for: point.kind, colour: colour)
                    marker.position = pos
                    anchor.addChild(marker)

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

            // the board itself
            let boardPos = spin.act(SIMD3<Float>(Float(design.boardPoint.x),
                                                 1.5,
                                                 Float(-design.boardPoint.y)))
            let board = ModelEntity(
                mesh: .generateBox(size: [0.30, 0.40, 0.10], cornerRadius: 0.01),
                materials: [SimpleMaterial(color: Palette.accent,
                                           isMetallic: false)])
            board.position = boardPos
            anchor.addChild(board)

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
            let mesh = MeshResource.generateBox(
                size: [0.018, 0.018, length], cornerRadius: 0.008)
            let entity = ModelEntity(
                mesh: mesh,
                materials: [SimpleMaterial(color: colour, isMetallic: false)])
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
                mesh = .generateSphere(radius: 0.055)
            case .fan:
                mesh = .generateSphere(radius: 0.075)
            case .switchboard:
                mesh = .generateBox(size: [0.09, 0.09, 0.02], cornerRadius: 0.004)
            case .socket:
                mesh = .generateBox(size: [0.07, 0.07, 0.02], cornerRadius: 0.004)
            case .appliance:
                mesh = .generateBox(size: [0.11, 0.11, 0.03], cornerRadius: 0.005)
            }
            return ModelEntity(
                mesh: mesh,
                materials: [SimpleMaterial(color: colour, isMetallic: false)])
        }
    }
}

// MARK: - UIKit palette

enum Palette {
    static let accent = UIColor(red: 0.12, green: 0.43, blue: 0.35, alpha: 1)

    private static let cycle: [UIColor] = [
        UIColor(red: 0.12, green: 0.43, blue: 0.35, alpha: 1),
        UIColor(red: 0.72, green: 0.28, blue: 0.16, alpha: 1),
        UIColor(red: 0.18, green: 0.36, blue: 0.54, alpha: 1),
        UIColor(red: 0.54, green: 0.43, blue: 0.12, alpha: 1),
        UIColor(red: 0.42, green: 0.25, blue: 0.54, alpha: 1),
        UIColor(red: 0.25, green: 0.54, blue: 0.49, alpha: 1),
        UIColor(red: 0.66, green: 0.27, blue: 0.25, alpha: 1),
        UIColor(red: 0.29, green: 0.54, blue: 0.18, alpha: 1),
        UIColor(red: 0.54, green: 0.35, blue: 0.18, alpha: 1),
        UIColor(red: 0.18, green: 0.44, blue: 0.54, alpha: 1),
    ]

    static func uiColor(_ index: Int) -> UIColor {
        cycle[index % cycle.count]
    }
}
