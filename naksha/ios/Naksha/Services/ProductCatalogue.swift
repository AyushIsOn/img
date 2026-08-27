import Foundation

/// Product suggestions driven by the design.
///
/// The point of this is that nothing is merchandised separately. Every
/// recommendation exists because the design produced a point that needs a
/// product, so the list cannot drift away from what the house actually needs.
///
/// Rates are indicative placeholders. Real catalogue data would come from a
/// price feed rather than being compiled into the app.

struct Product: Identifiable, Hashable {
    let id = UUID()
    let name: String
    let category: String
    let spec: String
    let indicativePrice: Double
    /// What in the design causes this to be recommended.
    let matches: Match

    enum Match: Hashable {
        case pointKind(String)              // e.g. every "light"
        case applianceLabel(String)         // e.g. "Water heater 15 L"
        case cable(Double)                  // a conductor size in the BoQ
        case switchgear                     // MCB, RCCB, board
    }
}

enum ProductCatalogue {

    static let all: [Product] = [
        .init(name: "LED Panel 18 W", category: "Lighting",
              spec: "1800 lm, 4000 K, recess mount",
              indicativePrice: 420, matches: .pointKind("light")),
        .init(name: "BLDC Ceiling Fan", category: "Fans",
              spec: "1200 mm sweep, 28 W, remote",
              indicativePrice: 3100, matches: .pointKind("fan")),
        .init(name: "Modular Switch Plate", category: "Switchgear",
              spec: "Polycarbonate, screwless",
              indicativePrice: 260, matches: .pointKind("switchboard")),
        .init(name: "6 A Socket, 3 pin", category: "Switchgear",
              spec: "Shuttered, with indicator",
              indicativePrice: 95, matches: .pointKind("socket")),
        .init(name: "16 A Socket, 3 pin", category: "Switchgear",
              spec: "For fixed appliance points",
              indicativePrice: 165, matches: .pointKind("appliance")),
        .init(name: "Storage Water Heater 15 L", category: "Water Heaters",
              spec: "2000 W, glass lined, 5 star",
              indicativePrice: 9400,
              matches: .applianceLabel("Water heater 15 L")),
        .init(name: "Storage Water Heater 10 L", category: "Water Heaters",
              spec: "2000 W, glass lined",
              indicativePrice: 8200,
              matches: .applianceLabel("Water heater 10 L")),
        .init(name: "Kitchen Chimney 90 cm", category: "Kitchen Appliances",
              spec: "Auto clean, 1200 m3/h",
              indicativePrice: 16500, matches: .applianceLabel("Chimney")),
        .init(name: "RO Water Purifier", category: "Water Purifiers",
              spec: "7 L, RO plus UV",
              indicativePrice: 12900,
              matches: .applianceLabel("RO purifier")),
        .init(name: "Inverter Split AC 1 T", category: "Air Conditioners",
              spec: "5 star, wide voltage range",
              indicativePrice: 34500,
              matches: .applianceLabel("Air conditioner 1 T")),
        .init(name: "Inverter Split AC 1.5 T", category: "Air Conditioners",
              spec: "5 star, wide voltage range",
              indicativePrice: 41000,
              matches: .applianceLabel("Air conditioner 1.5 T")),
        .init(name: "Self Priming Monobloc Pump", category: "Pumps",
              spec: "0.5 HP, 750 W",
              indicativePrice: 5600, matches: .applianceLabel("Water pump")),
        .init(name: "FR Cable 1.5 sq mm", category: "Wires and Cables",
              spec: "90 m coil, flame retardant",
              indicativePrice: 1260, matches: .cable(1.5)),
        .init(name: "FR Cable 2.5 sq mm", category: "Wires and Cables",
              spec: "90 m coil, flame retardant",
              indicativePrice: 1980, matches: .cable(2.5)),
        .init(name: "FR Cable 4 sq mm", category: "Wires and Cables",
              spec: "90 m coil, flame retardant",
              indicativePrice: 3060, matches: .cable(4.0)),
        .init(name: "Distribution Board with RCCB", category: "Switchgear",
              spec: "SPN, 30 mA RCCB, digital voltage display",
              indicativePrice: 4200, matches: .switchgear),
    ]

    /// A recommendation carries its reason, so the user can see why it is here.
    struct Recommendation: Identifiable {
        let product: Product
        let quantity: Int
        let reason: String
        var id: UUID { product.id }
        var lineTotal: Double { Double(quantity) * product.indicativePrice }
    }

    static func recommendations(for design: Design) -> [Recommendation] {
        var out: [Recommendation] = []

        for product in all {
            switch product.matches {
            case .pointKind(let kind):
                let n = design.points.filter { $0.kind.rawValue == kind }.count
                if n > 0 {
                    out.append(.init(product: product, quantity: n,
                                     reason: "\(n) \(kind) point"
                                            + (n == 1 ? "" : "s")
                                            + " in the design"))
                }

            case .applianceLabel(let label):
                let hits = design.points.filter { $0.label == label }
                if !hits.isEmpty {
                    let rooms = Set(hits.map(\.room)).sorted()
                        .joined(separator: ", ")
                    out.append(.init(product: product, quantity: hits.count,
                                     reason: "You asked for this in \(rooms)"))
                }

            case .cable(let size):
                // one coil per 90 m of the three core requirement
                let metres = design.circuits
                    .filter { $0.cableMM2 == size }
                    .reduce(0.0) { $0 + $1.routeLengthM } * 3 * 1.1
                if metres > 0 {
                    let coils = Int(ceil(metres / 90))
                    out.append(.init(product: product, quantity: coils,
                                     reason: String(format:
                                        "%.0f m needed across %d circuit(s)",
                                        metres,
                                        design.circuits.filter {
                                            $0.cableMM2 == size }.count)))
                }

            case .switchgear:
                out.append(.init(product: product, quantity: 1,
                                 reason: "\(design.circuits.count) ways plus "
                                        + "main protection"))
            }
        }
        return out.sorted { $0.lineTotal > $1.lineTotal }
    }

    static func total(for design: Design) -> Double {
        recommendations(for: design).reduce(0) { $0 + $1.lineTotal }
    }
}
