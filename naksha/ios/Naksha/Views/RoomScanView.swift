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
    @State private var pendingRoom: CapturedRoom?
    @State private var roomName = ""
    @State private var roomKind = "bedroom"

    private let kinds = ["living", "bedroom", "kitchen", "bath",
                         "dining", "study", "utility", "passage"]

    var body: some View {
        VStack(spacing: 0) {
            if capturing {
                RoomCaptureContainer { room in
                    pendingRoom = room
                    capturing = false
                }
                .ignoresSafeArea(edges: .bottom)
            } else {
                list
            }
        }
        .navigationTitle("Scan rooms")
        .sheet(item: Binding(
            get: { pendingRoom.map { IdentifiedRoom(room: $0) } },
            set: { if $0 == nil { pendingRoom = nil } })) { wrapper in
            nameSheet(for: wrapper.room)
        }
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
                    .background(RoundedRectangle(cornerRadius: 12)
                        .fill(Color.white))
                }

                Button {
                    capturing = true
                } label: {
                    Label(store.scannedRooms.isEmpty
                          ? "Scan the first room" : "Scan another room",
                          systemImage: "camera.viewfinder")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)

                if !store.scannedRooms.isEmpty {
                    NavigationLink {
                        RequirementsView(rooms: store.scannedRooms)
                    } label: {
                        Label("Next, what goes in each room",
                              systemImage: "arrow.right")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                    .controlSize(.large)
                }
            }
            .padding(20)
        }
        .background(Color(white: 0.97).ignoresSafeArea())
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
    let onFinish: (CapturedRoom) -> Void

    func makeCoordinator() -> RoomCaptureCoordinator {
        RoomCaptureCoordinator(onFinish: onFinish)
    }

    func makeUIView(context: Context) -> RoomCaptureView {
        let view = RoomCaptureView(frame: .zero)
        view.delegate = context.coordinator
        context.coordinator.view = view
        view.captureSession.run(configuration: RoomCaptureSession.Configuration())
        return view
    }

    func updateUIView(_ view: RoomCaptureView, context: Context) {}

    static func dismantleUIView(_ view: RoomCaptureView,
                                coordinator: RoomCaptureCoordinator) {
        view.captureSession.stop()
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

    private let onFinish: (CapturedRoom) -> Void
    weak var view: RoomCaptureView?

    init(onFinish: @escaping (CapturedRoom) -> Void) {
        self.onFinish = onFinish
        super.init()
    }

    // Required by NSCoding via RoomCaptureViewDelegate. The delegate is never
    // encoded or decoded, so both are deliberate no-ops.
    required init?(coder: NSCoder) {
        self.onFinish = { _ in }
        super.init()
    }

    func encode(with coder: NSCoder) {}

    // MARK: RoomCaptureViewDelegate

    /// Let RoomPlan post-process the raw scan into the parametric model.
    func captureView(shouldPresent roomDataForProcessing: CapturedRoomData,
                     error: Error?) -> Bool {
        error == nil
    }

    func captureView(didPresent processedResult: CapturedRoom,
                     error: Error?) {
        guard error == nil else { return }
        onFinish(processedResult)
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
