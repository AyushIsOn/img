import PDFKit
import PhotosUI
import SwiftUI
import UIKit
import UniformTypeIdentifiers

/// Import the architect's drawing and trace the rooms over it.
///
/// Automatic vectorisation of an Indian residential plan is not reliable. They
/// arrive as phone photographs of printouts, scanned faxes, hand marked
/// revisions and occasionally a PDF. Rather than pretend to read them, the app
/// asks the user for two things it cannot infer: a scale, and the room
/// outlines. Both take seconds and neither can be silently wrong.
struct PlanImportView: View {
    @EnvironmentObject private var store: DesignStore

    @State private var image: UIImage?
    @State private var photoItem: PhotosPickerItem?
    @State private var showingFileImporter = false
    @State private var stage: Stage = .pickSource
    @State private var calibration = Calibration()
    @State private var tracedRooms: [TracedRoom] = []
    @State private var current: [CGPoint] = []
    @State private var roomName = ""
    @State private var roomKind = "bedroom"
    @State private var showNaming = false

    private let kinds = ["living", "bedroom", "kitchen", "bath",
                         "dining", "study", "utility", "passage"]

    enum Stage {
        case pickSource, calibrate, trace, done
    }

    var body: some View {
        VStack(spacing: 0) {
            if let image {
                TraceCanvas(image: image,
                            stage: stage,
                            calibration: $calibration,
                            current: $current,
                            traced: tracedRooms)
                    .background(Color(white: 0.92))
                instructions
            } else {
                sourcePicker
            }
        }
        .navigationTitle("Architect's plan")
        .navigationBarTitleDisplayMode(.inline)
        .photosPicker(isPresented: .constant(false), selection: $photoItem)
        .fileImporter(isPresented: $showingFileImporter,
                      allowedContentTypes: [.pdf, .image]) { result in
            if case .success(let url) = result { load(url: url) }
        }
        .sheet(isPresented: $showNaming) { namingSheet }
    }

    // MARK: - Source

    private var sourcePicker: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                Text("Bring in the plan your architect gave you. A photograph "
                     + "of a printout is fine.")
                    .font(.footnote).foregroundColor(Theme.muted)

                PhotosPicker(selection: $photoItem, matching: .images) {
                    Card(icon: "photo", title: "Choose a photo",
                         detail: "From your camera roll.")
                }
                .buttonStyle(.plain)

                Button { showingFileImporter = true } label: {
                    Card(icon: "doc", title: "Choose a PDF or file",
                         detail: "The first page is used.")
                }
                .buttonStyle(.plain)
            }
            .padding(20)
        }
        .background(Color(white: 0.97).ignoresSafeArea())
        .onChange(of: photoItem) { _, item in
            guard let item else { return }
            Task {
                if let data = try? await item.loadTransferable(type: Data.self),
                   let ui = UIImage(data: data) {
                    await MainActor.run {
                        image = ui
                        stage = .calibrate
                    }
                }
            }
        }
    }

    private func load(url: URL) {
        if let ui = UIImage(contentsOfFile: url.path) {
            image = ui
            stage = .calibrate
            return
        }
        // PDF: rasterise the first page
        guard let doc = PDFDocument(url: url), let page = doc.page(at: 0)
        else { return }
        let bounds = page.bounds(for: .mediaBox)
        let scale: CGFloat = 2
        let renderer = UIGraphicsImageRenderer(
            size: CGSize(width: bounds.width * scale,
                         height: bounds.height * scale))
        image = renderer.image { ctx in
            UIColor.white.setFill()
            ctx.fill(CGRect(origin: .zero, size: renderer.format.bounds.size))
            ctx.cgContext.translateBy(x: 0, y: bounds.height * scale)
            ctx.cgContext.scaleBy(x: scale, y: -scale)
            page.draw(with: .mediaBox, to: ctx.cgContext)
        }
        stage = .calibrate
    }

    // MARK: - Instructions and actions

    @ViewBuilder private var instructions: some View {
        VStack(spacing: 10) {
            switch stage {
            case .pickSource:
                EmptyView()

            case .calibrate:
                Text(calibration.a == nil
                     ? "Tap one end of a dimension you know."
                     : calibration.b == nil
                       ? "Now tap the other end."
                       : "Enter how long that really is.")
                    .font(.footnote.weight(.medium))
                if calibration.a != nil && calibration.b != nil {
                    HStack {
                        TextField("Length in metres", value: $calibration.metres,
                                  format: .number)
                            .textFieldStyle(.roundedBorder)
                            .keyboardType(.decimalPad)
                        Button("Set scale") {
                            if calibration.isUsable { stage = .trace }
                        }
                        .buttonStyle(.borderedProminent)
                        .disabled(!(calibration.metres > 0))
                    }
                    Button("Start over") { calibration = Calibration() }
                        .font(.caption)
                }

            case .trace:
                Text(String(format:
                    "Scale set, %.3f m per point. Tap the corners of a room, "
                    + "then name it.", calibration.metresPerPoint))
                    .font(.caption).foregroundColor(Theme.muted)
                HStack(spacing: 10) {
                    Button("Undo point") {
                        if !current.isEmpty { current.removeLast() }
                    }
                    .buttonStyle(.bordered)
                    .disabled(current.isEmpty)

                    Button("Close room") { showNaming = true }
                        .buttonStyle(.borderedProminent)
                        .disabled(current.count < 3)
                }
                if !tracedRooms.isEmpty {
                    Text("\(tracedRooms.count) room(s) traced")
                        .font(.caption2).foregroundColor(Theme.accent)
                    NavigationLink {
                        RequirementsView(rooms: store.scannedRooms)
                    } label: {
                        Label("Next, what goes in each room",
                              systemImage: "arrow.right")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                }

            case .done:
                EmptyView()
            }
        }
        .padding(14)
        .background(Color.white)
    }

    private var namingSheet: some View {
        NavigationStack {
            Form {
                Section("Room") {
                    TextField("Name", text: $roomName)
                    Picker("Type", selection: $roomKind) {
                        ForEach(kinds, id: \.self) {
                            Text($0.capitalized).tag($0)
                        }
                    }
                }
                Section {
                    let area = TracedRoom(points: current,
                                          name: "", kind: "")
                        .areaM2(calibration.metresPerPoint)
                    Text(String(format: "About %.1f m\u{00B2}", area))
                        .font(.caption).foregroundColor(Theme.muted)
                }
            }
            .navigationTitle("Name this room")
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Add") { commitRoom() }
                }
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { showNaming = false }
                }
            }
        }
    }

    private func commitRoom() {
        let name = roomName.isEmpty
            ? "Room \(tracedRooms.count + 1)" : roomName
        let traced = TracedRoom(points: current, name: name, kind: roomKind)
        tracedRooms.append(traced)
        store.scannedRooms.append(
            traced.asScannedRoom(metresPerPoint: calibration.metresPerPoint))
        current = []
        roomName = ""
        showNaming = false
    }
}

// MARK: - Model

struct Calibration {
    var a: CGPoint?
    var b: CGPoint?
    var metres: Double = 0

    var pixelLength: CGFloat {
        guard let a, let b else { return 0 }
        return hypot(a.x - b.x, a.y - b.y)
    }

    var metresPerPoint: Double {
        guard pixelLength > 0, metres > 0 else { return 0 }
        return metres / Double(pixelLength)
    }

    var isUsable: Bool { metresPerPoint > 0 }
}

struct TracedRoom: Identifiable {
    let id = UUID()
    var points: [CGPoint]
    var name: String
    var kind: String

    func areaM2(_ metresPerPoint: Double) -> Double {
        guard points.count > 2, metresPerPoint > 0 else { return 0 }
        var sum = 0.0
        for i in points.indices {
            let p = points[i]
            let q = points[(i + 1) % points.count]
            sum += Double(p.x * q.y - q.x * p.y)
        }
        return abs(sum) / 2 * metresPerPoint * metresPerPoint
    }

    /// Converts traced view points into solver metres. View y grows downward,
    /// plan y grows upward, so the vertical axis is inverted here.
    func asScannedRoom(metresPerPoint m: Double) -> ScannedRoom {
        let polygon = points.map { [Double($0.x) * m, -Double($0.y) * m] }
        let doorway = points.count >= 2
            ? [[(polygon[0][0] + polygon[1][0]) / 2,
                (polygon[0][1] + polygon[1][1]) / 2]]
            : []
        return ScannedRoom(name: name, kind: kind,
                           polygon: polygon, doorways: doorway)
    }
}

// MARK: - Canvas

private struct TraceCanvas: View {
    let image: UIImage
    let stage: PlanImportView.Stage
    @Binding var calibration: Calibration
    @Binding var current: [CGPoint]
    let traced: [TracedRoom]

    var body: some View {
        GeometryReader { geo in
            ZStack {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFit()
                Canvas { ctx, _ in
                    // calibration line
                    if let a = calibration.a {
                        mark(&ctx, a, Theme.warn)
                        if let b = calibration.b {
                            mark(&ctx, b, Theme.warn)
                            var line = Path()
                            line.move(to: a)
                            line.addLine(to: b)
                            ctx.stroke(line, with: .color(Theme.warn),
                                       style: StrokeStyle(lineWidth: 2,
                                                          dash: [4, 3]))
                        }
                    }
                    // rooms already traced
                    for room in traced {
                        var path = Path()
                        guard let first = room.points.first else { continue }
                        path.move(to: first)
                        for p in room.points.dropFirst() { path.addLine(to: p) }
                        path.closeSubpath()
                        ctx.fill(path, with: .color(Theme.accent.opacity(0.18)))
                        ctx.stroke(path, with: .color(Theme.accent),
                                   lineWidth: 2)
                    }
                    // room being traced
                    if !current.isEmpty {
                        var path = Path()
                        path.move(to: current[0])
                        for p in current.dropFirst() { path.addLine(to: p) }
                        ctx.stroke(path, with: .color(Theme.ink), lineWidth: 2)
                        for p in current { mark(&ctx, p, Theme.ink) }
                    }
                }
                .contentShape(Rectangle())
                .onTapGesture { location in
                    handleTap(location)
                }
            }
        }
    }

    private func mark(_ ctx: inout GraphicsContext, _ p: CGPoint,
                      _ colour: Color) {
        let r: CGFloat = 5
        let rect = CGRect(x: p.x - r, y: p.y - r, width: r * 2, height: r * 2)
        ctx.fill(Path(ellipseIn: rect), with: .color(.white))
        ctx.stroke(Path(ellipseIn: rect), with: .color(colour), lineWidth: 2)
    }

    private func handleTap(_ location: CGPoint) {
        switch stage {
        case .calibrate:
            if calibration.a == nil { calibration.a = location }
            else if calibration.b == nil { calibration.b = location }
        case .trace:
            current.append(location)
        default:
            break
        }
    }
}
