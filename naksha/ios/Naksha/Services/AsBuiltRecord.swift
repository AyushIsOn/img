import Foundation
import SwiftUI
import UniformTypeIdentifiers

/// The map that stays with the house.
///
/// This is the output the owner keeps, and arguably the most durable thing the
/// product creates. The electrician confirms each run as it is laid, before
/// plastering, and what is left is a record of where every cable actually
/// went, rather than where it was once intended to go.
///
/// Without this, renovation is guesswork and drilling into a wall is a gamble.

struct AsBuiltRecord: Codable {
    var planName: String
    var createdAt: Date
    var updatedAt: Date
    /// Point ids the electrician has confirmed on site.
    var confirmedPoints: Set<String>
    /// Circuit ids confirmed as fully laid.
    var confirmedCircuits: Set<String>
    /// Free text against a point, for example "moved 200 mm left, beam".
    var notes: [String: String]
    /// The design this record was built from, so the file is self contained.
    var design: DesignSnapshot

    struct DesignSnapshot: Codable {
        var rooms: [RoomSnapshot]
        var points: [PointSnapshot]
        var circuits: [CircuitSnapshot]
        var board: [Double]
    }

    struct RoomSnapshot: Codable {
        var name: String
        var kind: String
        var polygon: [[Double]]
    }

    struct PointSnapshot: Codable {
        var id: String
        var kind: String
        var room: String
        var xy: [Double]
        var height: Double
        var label: String
    }

    struct CircuitSnapshot: Codable {
        var id: String
        var kind: String
        var mcbAmps: Double
        var cableMM2: Double
        var routeEdges: [[[Double]]]
    }

    init(design: Design) {
        planName = design.plan.name
        createdAt = Date()
        updatedAt = Date()
        confirmedPoints = []
        confirmedCircuits = []
        notes = [:]
        self.design = DesignSnapshot(
            rooms: design.plan.rooms.map {
                RoomSnapshot(name: $0.name, kind: $0.kind, polygon: $0.polygon)
            },
            points: design.points.map {
                PointSnapshot(id: $0.id, kind: $0.kind.rawValue,
                              room: $0.room, xy: $0.xy, height: $0.height,
                              label: $0.label)
            },
            circuits: design.circuits.map {
                CircuitSnapshot(id: $0.id, kind: $0.kind.rawValue,
                                mcbAmps: $0.mcbAmps, cableMM2: $0.cableMM2,
                                routeEdges: $0.routeEdges)
            },
            board: design.board)
    }

    var completion: Double {
        guard !design.points.isEmpty else { return 0 }
        return Double(confirmedPoints.count) / Double(design.points.count)
    }
}

// MARK: - Store

@MainActor
final class AsBuiltStore: ObservableObject {
    @Published var record: AsBuiltRecord?

    private var fileURL: URL? {
        guard let name = record?.planName else { return nil }
        let safe = name.replacingOccurrences(of: " ", with: "-")
        return FileManager.default
            .urls(for: .documentDirectory, in: .userDomainMask).first?
            .appendingPathComponent("asbuilt-\(safe).json")
    }

    func begin(from design: Design) {
        if record == nil { record = AsBuiltRecord(design: design) }
    }

    func toggle(point id: String) {
        guard var r = record else { return }
        if r.confirmedPoints.contains(id) { r.confirmedPoints.remove(id) }
        else { r.confirmedPoints.insert(id) }
        r.updatedAt = Date()
        record = r
        save()
    }

    func toggle(circuit id: String, pointIDs: [String]) {
        guard var r = record else { return }
        if r.confirmedCircuits.contains(id) {
            r.confirmedCircuits.remove(id)
            pointIDs.forEach { r.confirmedPoints.remove($0) }
        } else {
            r.confirmedCircuits.insert(id)
            pointIDs.forEach { r.confirmedPoints.insert($0) }
        }
        r.updatedAt = Date()
        record = r
        save()
    }

    func note(_ text: String, for pointID: String) {
        guard var r = record else { return }
        if text.isEmpty { r.notes.removeValue(forKey: pointID) }
        else { r.notes[pointID] = text }
        r.updatedAt = Date()
        record = r
        save()
    }

    /// Persist quietly so a site visit is never lost to a backgrounded app.
    func save() {
        guard let record, let url = fileURL else { return }
        do {
            let encoder = JSONEncoder()
            encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
            encoder.dateEncodingStrategy = .iso8601
            try encoder.encode(record).write(to: url, options: .atomic)
        } catch {
            // A failed autosave must not interrupt the user mid scan.
            print("as-built save failed: \(error.localizedDescription)")
        }
    }

    func load(planName: String) {
        guard let dir = FileManager.default
            .urls(for: .documentDirectory, in: .userDomainMask).first else {
            return
        }
        let safe = planName.replacingOccurrences(of: " ", with: "-")
        let url = dir.appendingPathComponent("asbuilt-\(safe).json")
        guard let data = try? Data(contentsOf: url) else { return }
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        record = try? decoder.decode(AsBuiltRecord.self, from: data)
    }

    /// A file the owner can keep, mail to themselves, or hand to the next
    /// electrician years later.
    func exportFile() -> URL? {
        guard let record else { return nil }
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        encoder.dateEncodingStrategy = .iso8601
        guard let data = try? encoder.encode(record) else { return nil }
        let safe = record.planName.replacingOccurrences(of: " ", with: "-")
        let url = FileManager.default.temporaryDirectory
            .appendingPathComponent("NAKSHA-as-built-\(safe).json")
        try? data.write(to: url, options: .atomic)
        return url
    }
}

// MARK: - As-built screen

struct AsBuiltView: View {
    let design: Design
    @StateObject private var store = AsBuiltStore()
    @State private var editingNote: String?
    @State private var noteText = ""

    var body: some View {
        List {
            Section {
                if let r = store.record {
                    VStack(alignment: .leading, spacing: 8) {
                        ProgressView(value: r.completion).tint(Theme.accent)
                        Text("\(r.confirmedPoints.count) of "
                             + "\(design.points.count) points confirmed")
                            .font(.caption).foregroundColor(Theme.muted)
                        if let url = store.exportFile() {
                            ShareLink(item: url) {
                                Label("Export the as-built map",
                                      systemImage: "square.and.arrow.up")
                            }
                            .font(.subheadline.weight(.semibold))
                        }
                    }
                }
            } header: { Text("Progress") }
              footer: { Text("Confirm each run as it is laid, before "
                             + "plastering. The exported file is the record "
                             + "of where the cables actually went.") }

            ForEach(Array(design.circuits.enumerated()), id: \.1.id) { i, c in
                Section {
                    ForEach(design.points.filter { c.pointIDs.contains($0.id) }) { p in
                        pointRow(p)
                    }
                } header: {
                    HStack {
                        Circle().fill(Theme.circuitAccent(i))
                            .frame(width: 8, height: 8)
                        Text("\(c.id)  \(c.kind.displayName)")
                        Spacer()
                        Button(store.record?.confirmedCircuits.contains(c.id) == true
                               ? "Undo" : "Confirm all") {
                            store.toggle(circuit: c.id, pointIDs: c.pointIDs)
                        }
                        .font(.caption2.weight(.semibold))
                    }
                }
            }
        }
        .scrollContentBackground(.hidden)
        .navigationTitle("As-built record")
        .onAppear {
            store.load(planName: design.plan.name)
            store.begin(from: design)
        }
        .alert("Note", isPresented: Binding(
            get: { editingNote != nil },
            set: { if !$0 { editingNote = nil } })) {
            TextField("For example, moved 200 mm, beam in the way",
                      text: $noteText)
            Button("Save") {
                if let id = editingNote { store.note(noteText, for: id) }
                editingNote = nil
                noteText = ""
            }
            Button("Cancel", role: .cancel) { editingNote = nil }
        }
    }

    private func pointRow(_ p: DevicePoint) -> some View {
        let confirmed = store.record?.confirmedPoints.contains(p.id) == true
        let note = store.record?.notes[p.id]
        return HStack(spacing: 10) {
            Button {
                store.toggle(point: p.id)
            } label: {
                Image(systemName: confirmed
                      ? "checkmark.circle.fill" : "circle")
                    .foregroundColor(confirmed ? Theme.accent : Theme.muted)
            }
            .buttonStyle(.plain)

            VStack(alignment: .leading, spacing: 1) {
                Text("\(p.id)  \(p.label)").font(.subheadline)
                Text(p.room).font(.caption2).foregroundColor(Theme.muted)
                if let note, !note.isEmpty {
                    Text(note).font(.caption2).foregroundColor(Theme.warn)
                }
            }
            Spacer()
            Button {
                editingNote = p.id
                noteText = note ?? ""
            } label: {
                Image(systemName: "square.and.pencil")
                    .foregroundColor(Theme.muted)
            }
            .buttonStyle(.plain)
        }
    }
}
