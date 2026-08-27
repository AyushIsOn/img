import Foundation

/// The conversational stage.
///
/// This is the only part of the product where a language model belongs, and
/// even here its job is narrow: ask a sensible next question, and turn a
/// free-text answer into a structured entry. It never sizes a cable.
///
/// The engine below is deliberately deterministic so the app works offline and
/// so the question flow is testable. `LLMQuestionSource` is the seam where a
/// model can take over phrasing and follow-ups without touching anything
/// downstream.

// MARK: - Structured result

struct ApplianceEntry: Codable, Identifiable, Hashable {
    var id = UUID()
    var name: String
    var watts: Double
    var room: String
    var kind: String
    var dedicated: Bool
    var vguardCategory: String?
}

struct RoomAnswers: Codable, Hashable {
    var lights: Int?
    var fan: Bool?
    var sockets: Int?
}

struct RequirementSet: Codable {
    var appliances: [ApplianceEntry] = []
    var perRoom: [String: RoomAnswers] = [:]
    var sanctionedLoadW: Double = 5000

    var totalConnectedW: Double {
        appliances.reduce(0) { $0 + $1.watts }
    }
}

// MARK: - Catalogue

/// Typical loads, so the user picks a thing rather than typing a wattage.
/// Categories map to the V-Guard ranges the app can then recommend.
struct ApplianceOption: Identifiable, Hashable {
    let id = UUID()
    let name: String
    let watts: Double
    let kind: String
    let dedicated: Bool
    let vguardCategory: String?
    let suitableRooms: Set<String>

    static let catalogue: [ApplianceOption] = [
        .init(name: "Air conditioner 1 T", watts: 1500, kind: "ac",
              dedicated: true, vguardCategory: "Air Conditioners",
              suitableRooms: ["bedroom", "living", "study"]),
        .init(name: "Air conditioner 1.5 T", watts: 1800, kind: "ac",
              dedicated: true, vguardCategory: "Air Conditioners",
              suitableRooms: ["bedroom", "living", "dining"]),
        .init(name: "Water heater 15 L", watts: 2000, kind: "geyser",
              dedicated: true, vguardCategory: "Water Heaters",
              suitableRooms: ["bath"]),
        .init(name: "Water heater 10 L", watts: 2000, kind: "geyser",
              dedicated: true, vguardCategory: "Water Heaters",
              suitableRooms: ["bath"]),
        .init(name: "Chimney", watts: 250, kind: "chimney",
              dedicated: false, vguardCategory: "Kitchen Appliances",
              suitableRooms: ["kitchen"]),
        .init(name: "RO purifier", watts: 60, kind: "ro",
              dedicated: false, vguardCategory: "Water Purifiers",
              suitableRooms: ["kitchen", "utility"]),
        .init(name: "Refrigerator", watts: 200, kind: "fridge",
              dedicated: false, vguardCategory: nil,
              suitableRooms: ["kitchen", "dining"]),
        .init(name: "Induction cooktop", watts: 2000, kind: "stove",
              dedicated: true, vguardCategory: "Kitchen Appliances",
              suitableRooms: ["kitchen"]),
        .init(name: "Washing machine", watts: 500, kind: "other",
              dedicated: false, vguardCategory: nil,
              suitableRooms: ["utility", "bath"]),
        .init(name: "Water pump", watts: 750, kind: "pump",
              dedicated: false, vguardCategory: "Pumps",
              suitableRooms: ["utility"]),
        .init(name: "Television", watts: 150, kind: "other",
              dedicated: false, vguardCategory: nil,
              suitableRooms: ["living", "bedroom"]),
        .init(name: "EV charger 3.3 kW", watts: 3300, kind: "ev",
              dedicated: true, vguardCategory: nil,
              suitableRooms: ["utility", "passage"]),
    ]

    static func options(forRoomKind kind: String) -> [ApplianceOption] {
        catalogue.filter { $0.suitableRooms.contains(kind) }
    }
}

// MARK: - Questions

enum QuestionKind: Equatable {
    case appliances(room: String, kind: String)
    case fan(room: String)
    case socketCount(room: String, suggested: Int)
    case sanctionedLoad(suggested: Double)
    case confirmDemand(demand: Double, sanction: Double)
}

struct Question: Identifiable, Equatable {
    let id = UUID()
    let prompt: String
    let helper: String?
    let kind: QuestionKind

    static func == (a: Question, b: Question) -> Bool { a.kind == b.kind }
}

/// Produces the next question from what is already known.
/// Adaptive in the sense that matters: it only asks what is still missing, and
/// it reacts to earlier answers.
struct QuestionEngine {

    let rooms: [ScannedRoom]

    func nextQuestion(given set: RequirementSet) -> Question? {
        // 1. What fixed appliances go in each room, biggest rooms first.
        for room in rooms.sorted(by: { $0.areaM2 > $1.areaM2 }) {
            let answered = set.perRoom[room.name] != nil
            let hasAppliances = set.appliances.contains { $0.room == room.name }
            let optionsExist = !ApplianceOption
                .options(forRoomKind: room.kind).isEmpty
            if optionsExist && !hasAppliances && !answered {
                return Question(
                    prompt: "What will you put in \(room.name)?",
                    helper: "\(room.kind.capitalized), "
                          + String(format: "%.1f m\u{00B2}", room.areaM2),
                    kind: .appliances(room: room.name, kind: room.kind))
            }
        }

        // 2. Fans, only for rooms where a fan is plausible.
        for room in rooms where ["living", "bedroom", "dining", "study"]
            .contains(room.kind) {
            if set.perRoom[room.name]?.fan == nil {
                return Question(
                    prompt: "Do you want a ceiling fan in \(room.name)?",
                    helper: "Most Indian homes fit one per habitable room.",
                    kind: .fan(room: room.name))
            }
        }

        // 3. Socket counts, pre-filled with the rule of thumb.
        for room in rooms {
            if set.perRoom[room.name]?.sockets == nil {
                let suggested = Self.suggestedSockets(for: room)
                return Question(
                    prompt: "How many general sockets in \(room.name)?",
                    helper: "Suggested \(suggested) for this size and use. "
                          + "Appliance points are counted separately.",
                    kind: .socketCount(room: room.name,
                                       suggested: suggested))
            }
        }

        // 4. The supply the house is actually getting.
        if set.sanctionedLoadW <= 0 {
            return Question(
                prompt: "What is your sanctioned load?",
                helper: "It is on your electricity bill. Most Indian homes "
                      + "start at 3 to 5 kW.",
                kind: .sanctionedLoad(suggested: 5000))
        }

        // 5. If demand looks like it will exceed the sanction, say so now,
        //    while the walls are still open.
        let demand = Self.estimateDemand(set)
        if demand > set.sanctionedLoadW {
            return Question(
                prompt: "Your likely demand is about "
                      + "\(Int(demand)) W, above your "
                      + "\(Int(set.sanctionedLoadW)) W sanction.",
                helper: "You can raise the sanction, or let the design "
                      + "stagger the heavy loads.",
                kind: .confirmDemand(demand: demand,
                                     sanction: set.sanctionedLoadW))
        }
        return nil
    }

    var totalQuestionEstimate: Int {
        let applianceRooms = rooms.filter {
            !ApplianceOption.options(forRoomKind: $0.kind).isEmpty
        }.count
        let fanRooms = rooms.filter {
            ["living", "bedroom", "dining", "study"].contains($0.kind)
        }.count
        return applianceRooms + fanRooms + rooms.count + 1
    }

    // MARK: - Heuristics, mirrored from the solver

    static func suggestedSockets(for room: ScannedRoom) -> Int {
        let rule: (Double, Int, Int)
        switch room.kind {
        case "living":  rule = (6, 3, 8)
        case "bedroom": rule = (7, 3, 6)
        case "kitchen": rule = (4, 3, 8)
        case "study":   rule = (5, 3, 6)
        case "dining":  rule = (8, 2, 4)
        case "utility": rule = (8, 1, 3)
        default:        rule = (0, 1, 1)
        }
        if rule.0 == 0 { return rule.1 }
        let raw = Int(room.areaM2 / rule.0)
        return min(max(raw, rule.1), rule.2)
    }

    /// A rough diversity calculation so the warning can be raised during the
    /// conversation. The authoritative figure comes back from the solver.
    static func estimateDemand(_ set: RequirementSet) -> Double {
        var byKind: [String: [Double]] = [:]
        for a in set.appliances {
            byKind[a.kind, default: []].append(a.watts)
        }
        let factors: [String: Double] = [
            "ac": 0.75, "geyser": 0.5, "ev": 1.0, "stove": 0.75,
        ]
        var total = 0.0
        for (kind, watts) in byKind {
            let sorted = watts.sorted(by: >)
            let f = factors[kind] ?? 0.6
            total += sorted[0] + sorted.dropFirst().reduce(0) { $0 + $1 * f }
        }
        // lighting, fans and general sockets, allowed for in bulk
        let sockets = set.perRoom.values.compactMap { $0.sockets }
            .reduce(0, +)
        total += Double(sockets) * 200 * 0.4
        total += 350
        return total.rounded()
    }
}

/// The seam for a model-driven flow. Swapping this in changes how questions
/// are phrased and ordered. It cannot change how the installation is designed.
protocol LLMQuestionSource {
    func followUp(after answered: [Question],
                  known: RequirementSet) async throws -> Question?
}
