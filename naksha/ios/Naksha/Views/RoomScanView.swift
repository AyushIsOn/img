import RoomPlan
import simd
import SwiftUI
import UIKit

/// LiDAR room capture.
///
/// RoomPlan gives back a parametric room: walls, doors, windows and openings
/// with real dimensions. That is the single biggest shortcut in this project,
/// because it removes the need to reconstruct geometry ourselves.
///
/// Known constraint, and it shapes the flow: RoomPlan scans one room at a time.
/// A whole floor is therefore several captures which have to be stitched, so
/// the user scans room by room and names each one as they go.
struct RoomScanView: View {
    @EnvironmentObject private var store: DesignStore
    @Environment(\.dismiss) private var dismiss

    @State private var capturing = false
    @State private var stopRequested = false
    @State private var processing = false
    // Holds the wrapper, not the bare room. The wrapper carries the identity
    // the sheet is keyed on, so it has to be created once when the room
    // arrives rather than rebuilt while the view is being evaluated.
    @State private var pendingRoom: IdentifiedRoom?
    @State private var roomName = ""
    @State private var roomKind = "bedroom"

    private let kinds = ["living", "bedroom", "kitchen", "bath",
                         "dining", "study", "utility", "passage"]

    var body: some View {
        VStack(spacing: 0) {
            if capturing {
                ZStack(alignment: .bottom) {
                    RoomCaptureContainer(
                        stopRequested: $stopRequested,
                        onProcessing: { processing = true },
                        onFinish: { room in
                            pendingRoom = IdentifiedRoom(room: room)
                            endCapture()
                        },
                        onFailure: { endCapture() })
                    .ignoresSafeArea(edges: .bottom)

                    captureControls
                }
            } else {
                list
            }
        }
        .navigationTitle(capturing ? "Scanning" : "Scan rooms")
        // Leaving mid capture would abandon the session with no result, so the
        // way out is the explicit Cancel button below.
        .navigationBarBackButtonHidden(capturing)
        // Bound straight to the stored wrapper. The previous version built a
        // new IdentifiedRoom inside the binding's getter, so a fresh UUID was
        // minted on every body evaluation. sheet(item:) treats a changed id as
        // a different item, so it dismissed and represented the sheet on every
        // render, which read as the card flickering open and closed.
        .sheet(item: $pendingRoom) { wrapper in
            nameSheet(for: wrapper.room)
        }
    }

    private func endCapture() {
        capturing = false
        stopRequested = false
        processing = false
    }

    /// RoomPlan draws the live model and the coaching prompts, but it does not
    /// supply a way to finish. Stopping the session is what makes it hand back
    /// the processed room, so the Done button is what actually produces output.
    private var captureControls: some View {
        VStack(spacing: 12) {
            if processing {
                HStack(spacing: 10) {
                    ProgressView().tint(.white)
                    Text("Finishing the scan")
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.white)
                }
            } else {
                Text("Walk the room slowly until the walls join up, then tap Done.")
                    .font(.footnote)
                    .foregroundColor(.white.opacity(0.9))
                    .multilineTextAlignment(.center)
                    .fixedSize(horizontal: false, vertical: true)

                HStack(spacing: 12) {
                    Button {
                        endCapture()
                    } label: {
                        Text("Cancel")
                            .font(.subheadline.weight(.semibold))
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                            .glassChip()
                            .foregroundColor(Theme.ink)
                    }

                    Button {
                        processing = true
                        stopRequested = true
                    } label: {
                        Label("Done", systemImage: "checkmark")
                            .font(.subheadline.weight(.bold))
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                            .background(Brand.markGradient, in: .capsule)
                            .foregroundColor(.black)
                    }
                }
            }
        }
        .padding(18)
        .background(
            LinearGradient(colors: [.clear, .black.opacity(0.65)],
                           startPoint: .top, endPoint: .bottom)
                .ignoresSafeArea(edges: .bottom))
    }

    private var list: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                Text("Scan each room separately, then name it. RoomPlan "
                     + "measures one room per capture, so a flat is a few "
                     + "short scans.")
                    .font(.footnote).foregroundColor(Theme.muted)

                ForEach(store.scannedRooms) { room in
                    HStack {
                        VStack(alignment: .leading, spacing: 2) {
                            Text(room.name).font(.subheadline.weight(.semibold))
                            Text("\(room.kind.capitalized)  \u{00B7}  "
                                 + String(format: "%.1f m\u{00B2}", room.areaM2))
                                .font(.caption).foregroundColor(Theme.muted)
                        }
                        Spacer()
                        Button {
                            store.scannedRooms.removeAll { $0.id == room.id }
                        } label: {
                            Image(systemName: "trash").foregroundColor(Theme.warn)
                        }
                    }
                    .padding(14)
                    .glassCard(16)
                }

                Button {
                    // Reset first. Tearing down the previous capture calls
                    // finish(), which sets processing, so a stale flag would
                    // otherwise open the next scan stuck on "Finishing".
                    processing = false
                    stopRequested = false
                    capturing = true
                } label: {
                    Label(store.scannedRooms.isEmpty
                          ? "Scan the first room" : "Scan another room",
                          systemImage: "camera.viewfinder")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.vguard)

                if !store.scannedRooms.isEmpty {
                    NavigationLink {
                        RequirementsView(rooms: store.scannedRooms)
                    } label: {
                        Label("Next, what goes in each room",
                              systemImage: "arrow.right")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.vguardGlass)
                }
            }
            .padding(20)
        }
        
    }

    private func nameSheet(for room: CapturedRoom) -> some View {
        NavigationStack {
            Form {
                Section("Room") {
                    TextField("Name, for example Bedroom 1", text: $roomName)
                    Picker("Type", selection: $roomKind) {
                        ForEach(kinds, id: \.self) {
                            Text($0.capitalized).tag($0)
                        }
                    }
                }
                Section {
                    Text("\(room.walls.count) walls, \(room.doors.count) doors, "
                         + "\(room.windows.count) windows detected.")
                        .font(.caption).foregroundColor(Theme.muted)
                }
            }
            .navigationTitle("Name this room")
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Add") {
                        store.scannedRooms.append(
                            RoomConverter.convert(room,
                                                  name: roomName.isEmpty
                                                    ? "Room \(store.scannedRooms.count + 1)"
                                                    : roomName,
                                                  kind: roomKind))
                        roomName = ""
                        pendingRoom = nil
                    }
                }
                ToolbarItem(placement: .cancellationAction) {
                    Button("Discard") { pendingRoom = nil }
                }
            }
        }
    }
}

private struct IdentifiedRoom: Identifiable {
    let id = UUID()
    let room: CapturedRoom
}

// MARK: - RoomPlan bridge

struct RoomCaptureContainer: UIViewRepresentable {
    @Binding var stopRequested: Bool
    let onProcessing: () -> Void
    let onFinish: (CapturedRoom) -> Void
    let onFailure: () -> Void

    func makeCoordinator() -> RoomCaptureCoordinator {
        RoomCaptureCoordinator(onProcessing: onProcessing,
                               onFinish: onFinish,
                               onFailure: onFailure)
    }

    func makeUIView(context: Context) -> RoomCaptureView {
        let view = RoomCaptureView(frame: .zero)
        view.delegate = context.coordinator
        context.coordinator.view = view
        view.captureSession.run(configuration: RoomCaptureSession.Configuration())
        return view
    }

    func updateUIView(_ view: RoomCaptureView, context: Context) {
        // The Done button flips the binding; stopping the session here is what
        // triggers RoomPlan's post processing and the delegate callback.
        if stopRequested { context.coordinator.finish() }
    }

    static func dismantleUIView(_ view: RoomCaptureView,
                                coordinator: RoomCaptureCoordinator) {
        coordinator.abandon()
    }
}

/// Declared at file scope rather than nested inside the representable.
///
/// `RoomCaptureViewDelegate` inherits from `NSCoding`, which is an unusual
/// requirement for a delegate. That forces two things: the class has to satisfy
/// `NSCoding` even though it is never archived, and it has to be a top level
/// type so its Objective-C name is stable. The explicit `@objc` name pins it.
@objc(NakshaRoomCaptureCoordinator)
final class RoomCaptureCoordinator: NSObject, RoomCaptureViewDelegate {

    private let onProcessing: () -> Void
    private let onFinish: (CapturedRoom) -> Void
    private let onFailure: () -> Void
    private var stopped = false
    weak var view: RoomCaptureView?

    init(onProcessing: @escaping () -> Void,
         onFinish: @escaping (CapturedRoom) -> Void,
         onFailure: @escaping () -> Void) {
        self.onProcessing = onProcessing
        self.onFinish = onFinish
        self.onFailure = onFailure
        super.init()
    }

    // Required by NSCoding via RoomCaptureViewDelegate. The delegate is never
    // encoded or decoded, so these are deliberate no-ops.
    required init?(coder: NSCoder) {
        self.onProcessing = {}
        self.onFinish = { _ in }
        self.onFailure = {}
        super.init()
    }

    func encode(with coder: NSCoder) {}

    /// Ends the capture and expects a room back, which is the Done button.
    func finish() { stop(reportingProgress: true) }

    /// Ends the capture without expecting a result, which is view teardown
    /// after Cancel. Reporting progress here would set the processing flag on
    /// the way out and leave the next capture opening on a spinner.
    func abandon() { stop(reportingProgress: false) }

    /// Idempotent, because Done and teardown can both arrive and stopping an
    /// already stopped session throws.
    private func stop(reportingProgress: Bool) {
        guard !stopped else { return }
        stopped = true
        if reportingProgress { onProcessing() }
        view?.captureSession.stop()
    }

    // MARK: RoomCaptureViewDelegate

    /// Let RoomPlan post-process the raw scan into the parametric model.
    func captureView(shouldPresent roomDataForProcessing: CapturedRoomData,
                     error: Error?) -> Bool {
        if error != nil {
            DispatchQueue.main.async { self.onFailure() }
            return false
        }
        return true
    }

    func captureView(didPresent processedResult: CapturedRoom,
                     error: Error?) {
        // Without this the scan would appear to hang after Done, with no room
        // handed back and no explanation.
        guard error == nil else {
            DispatchQueue.main.async { self.onFailure() }
            return
        }
        DispatchQueue.main.async { self.onFinish(processedResult) }
    }
}

// MARK: - CapturedRoom to solver geometry

enum RoomConverter {

    /// Reduces a captured room to the floor polygon and doorway positions the
    /// solver needs. Wall transforms are projected onto the floor plane and
    /// their footprints combined into an axis aligned outline, which is
    /// adequate for the rectilinear rooms this is aimed at and honest about
    /// not handling curved or slanted walls.
    static func convert(_ room: CapturedRoom, name: String,
                        kind: String) -> ScannedRoom {
        var xs: [Float] = []
        var zs: [Float] = []
        for wall in room.walls {
            let t = wall.transform
            let centre = SIMD3<Float>(t.columns.3.x, t.columns.3.y,
                                      t.columns.3.z)
            let half = wall.dimensions.x / 2
            let axis = SIMD3<Float>(t.columns.0.x, 0, t.columns.0.z)
            let unit = simd_length(axis) > 0 ? simd_normalize(axis)
                                             : SIMD3<Float>(1, 0, 0)
            let a = centre - unit * half
            let b = centre + unit * half
            xs.append(contentsOf: [a.x, b.x])
            zs.append(contentsOf: [a.z, b.z])
        }
        guard let minX = xs.min(), let maxX = xs.max(),
              let minZ = zs.min(), let maxZ = zs.max() else {
            return ScannedRoom(name: name, kind: kind,
                               polygon: [], doorways: [])
        }
        // plan y runs opposite to ARKit z
        let polygon: [[Double]] = [
            [Double(minX), Double(-maxZ)],
            [Double(maxX), Double(-maxZ)],
            [Double(maxX), Double(-minZ)],
            [Double(minX), Double(-minZ)],
        ]
        let doorways: [[Double]] = room.doors.map { door in
            let t = door.transform
            return [Double(t.columns.3.x), Double(-t.columns.3.z)]
        }
        return ScannedRoom(name: name, kind: kind,
                           polygon: polygon, doorways: doorways)
    }
}
