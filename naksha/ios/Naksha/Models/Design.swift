import Foundation
import CoreGraphics

/// Decodes the JSON emitted by the Python design engine.
/// The field names deliberately mirror `run.py: export_json` so the reference
/// implementation and the client can never drift apart silently.

struct Design: Codable {
    let plan: Plan
    let board: [Double]
    let points: [DevicePoint]
    let circuits: [Circuit]
    let summary: Summary
    let checks: [String]
    let billOfQuantities: BillOfQuantities

    enum CodingKeys: String, CodingKey {
        case plan, board, points, circuits, summary, checks
        case billOfQuantities = "bill_of_quantities"
    }

    var boardPoint: CGPoint { CGPoint(x: board[0], y: board[1]) }

    func circuit(for point: DevicePoint) -> Circuit? {
        circuits.first { $0.pointIDs.contains(point.id) }
    }
}

// MARK: - Geometry

struct Plan: Codable {
    let name: String
    let ceilingHeight: Double
    let rooms: [Room]
    let doors: [Door]

    enum CodingKeys: String, CodingKey {
        case name, rooms, doors
        case ceilingHeight = "ceiling_height"
    }

    /// Bounding box of the whole floor, used to fit the drawing to a view.
    var bounds: CGRect {
        let pts = rooms.flatMap { $0.cgPolygon }
        guard let first = pts.first else { return .zero }
        var minX = first.x, maxX = first.x, minY = first.y, maxY = first.y
        for p in pts {
            minX = min(minX, p.x); maxX = max(maxX, p.x)
            minY = min(minY, p.y); maxY = max(maxY, p.y)
        }
        return CGRect(x: minX, y: minY, width: maxX - minX, height: maxY - minY)
    }
}

struct Room: Codable, Identifiable {
    let name: String
    let kind: String
    let polygon: [[Double]]
    let area: Double

    var id: String { name }
    var cgPolygon: [CGPoint] { polygon.map { CGPoint(x: $0[0], y: $0[1]) } }

    /// Even-odd point in polygon. Used to decide which conduit runs belong to
    /// a room when the AR overlay is showing only one.
    func contains(_ p: CGPoint) -> Bool {
        let pts = cgPolygon
        guard pts.count > 2 else { return false }
        var inside = false
        var j = pts.count - 1
        for i in pts.indices {
            let a = pts[i], b = pts[j]
            if (a.y > p.y) != (b.y > p.y),
               p.x < (b.x - a.x) * (p.y - a.y) / (b.y - a.y) + a.x {
                inside.toggle()
            }
            j = i
        }
        return inside
    }

    var center: CGPoint {
        let pts = cgPolygon
        guard !pts.isEmpty else { return .zero }
        let sx = pts.reduce(0) { $0 + $1.x }
        let sy = pts.reduce(0) { $0 + $1.y }
        return CGPoint(x: sx / CGFloat(pts.count), y: sy / CGFloat(pts.count))
    }
}

struct Door: Codable {
    let position: [Double]
    let roomA: String
    let roomB: String?
    let width: Double
    let isEntry: Bool

    enum CodingKeys: String, CodingKey {
        case position, width
        case roomA = "room_a"
        case roomB = "room_b"
        case isEntry = "is_entry"
    }

    var point: CGPoint { CGPoint(x: position[0], y: position[1]) }
}

// MARK: - Electrical

enum PointKind: String, Codable {
    case light, fan, switchboard, socket, appliance

    var symbolName: String {
        switch self {
        case .light:       return "lightbulb"
        case .fan:         return "fan"
        case .switchboard: return "switch.2"
        case .socket:      return "powerplug"
        case .appliance:   return "poweroutlet.type.b"
        }
    }

    var displayName: String {
        switch self {
        case .light:       return "Lighting point"
        case .fan:         return "Fan point"
        case .switchboard: return "Switch plate"
        case .socket:      return "Socket"
        case .appliance:   return "Appliance point"
        }
    }

    /// Ceiling devices are drawn and anchored differently from wall devices.
    var isCeilingMounted: Bool { self == .light || self == .fan }
}

struct DevicePoint: Codable, Identifiable {
    let id: String
    let kind: PointKind
    let room: String
    let xy: [Double]
    let height: Double
    let watts: Double
    let label: String
    let vguardCategory: String?

    enum CodingKeys: String, CodingKey {
        case id, kind, room, xy, height, watts, label
        case vguardCategory = "vguard_category"
    }

    var point: CGPoint { CGPoint(x: xy[0], y: xy[1]) }
}

enum CircuitKind: String, Codable {
    case lighting, power, dedicated

    var displayName: String {
        switch self {
        case .lighting:  return "Lighting"
        case .power:     return "Power"
        case .dedicated: return "Dedicated"
        }
    }
}

struct Circuit: Codable, Identifiable {
    let id: String
    let kind: CircuitKind
    let mcbAmps: Double
    let cableMM2: Double
    let connectedWatts: Double
    let routeLengthM: Double
    let vdropPercent: Double
    let pointIDs: [String]
    let routeEdges: [[[Double]]]

    enum CodingKeys: String, CodingKey {
        case id, kind
        case mcbAmps = "mcb_amps"
        case cableMM2 = "cable_mm2"
        case connectedWatts = "connected_watts"
        case routeLengthM = "route_length_m"
        case vdropPercent = "vdrop_percent"
        case pointIDs = "point_ids"
        case routeEdges = "route_edges"
    }

    /// Conduit runs as pairs of floor-plane points.
    var segments: [(CGPoint, CGPoint)] {
        routeEdges.compactMap { edge in
            guard edge.count == 2, edge[0].count == 2, edge[1].count == 2
            else { return nil }
            return (CGPoint(x: edge[0][0], y: edge[0][1]),
                    CGPoint(x: edge[1][0], y: edge[1][1]))
        }
    }
}

// MARK: - Outputs

struct Summary: Codable {
    let floorAreaM2: Double
    let connectedLoadW: Double
    let maximumDemandW: Double
    let sanctionedLoadW: Double
    let conduitM: Double

    enum CodingKeys: String, CodingKey {
        case floorAreaM2 = "floor_area_m2"
        case connectedLoadW = "connected_load_w"
        case maximumDemandW = "maximum_demand_w"
        case sanctionedLoadW = "sanctioned_load_w"
        case conduitM = "conduit_m"
    }

    var demandExceedsSanction: Bool { maximumDemandW > sanctionedLoadW }
}

struct BillOfQuantities: Codable {
    let lines: [BoQLine]
    let total: Double
    let conduitM: Double

    enum CodingKeys: String, CodingKey {
        case lines, total
        case conduitM = "conduit_m"
    }
}

struct BoQLine: Codable, Identifiable {
    let item: String
    let qty: Double
    let unit: String
    let rate: Double
    let amount: Double

    var id: String { item }
}
