import Foundation

/// The intake conversation.
///
/// The questions are written by a model running on the solver machine, so no
/// key is ever shipped in the app or held on the phone. The phone posts what it
/// has been told so far and receives the next question. If the model is not
/// reachable the server answers from a scripted sequence instead, and the flow
/// is identical from here.

struct InterviewQuestion: Codable, Identifiable, Equatable {
    let id: String
    let prompt: String
    let helper: String?
    let kind: Kind
    let unit: String?
    let min: Double?
    let max: Double?
    let options: [String]?

    enum Kind: String, Codable {
        case text, number, count, choice, multi
    }

    /// Decoded leniently. A model can invent a `kind` we do not render, and a
    /// free text field is a safe thing to fall back to: the answer still
    /// reaches the profile.
    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = (try? c.decode(String.self, forKey: .id)) ?? UUID().uuidString
        prompt = (try? c.decode(String.self, forKey: .prompt)) ?? ""
        helper = try? c.decodeIfPresent(String.self, forKey: .helper)
        kind = (try? c.decode(Kind.self, forKey: .kind)) ?? .text
        unit = try? c.decodeIfPresent(String.self, forKey: .unit)
        min = try? c.decodeIfPresent(Double.self, forKey: .min)
        max = try? c.decodeIfPresent(Double.self, forKey: .max)
        options = try? c.decodeIfPresent([String].self, forKey: .options)
    }
}

/// An answer is a single value or several, so it encodes as a bare string or a
/// bare array rather than a wrapper the server would have to unpick.
enum AnswerValue: Codable, Equatable {
    case text(String)
    case list([String])

    func encode(to encoder: Encoder) throws {
        var c = encoder.singleValueContainer()
        switch self {
        case .text(let value): try c.encode(value)
        case .list(let values): try c.encode(values)
        }
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.singleValueContainer()
        if let value = try? c.decode(String.self) { self = .text(value) }
        else { self = .list((try? c.decode([String].self)) ?? []) }
    }

    var display: String {
        switch self {
        case .text(let value): return value
        case .list(let values): return values.joined(separator: ", ")
        }
    }

    var isEmpty: Bool {
        switch self {
        case .text(let value):
            return value.trimmingCharacters(in: .whitespaces).isEmpty
        case .list(let values): return values.isEmpty
        }
    }
}

struct InterviewAnswer: Codable, Equatable, Identifiable {
    let id: String
    let prompt: String
    let answer: AnswerValue
}

struct ProfileAppliance: Codable, Equatable, Identifiable {
    let kind: String
    let count: Int
    let rooms: [String]?

    var id: String { kind }

    /// Model output is a machine key, so give it a human label here rather
    /// than asking the model for one it might phrase differently each turn.
    var display: String {
        switch kind {
        case "ac": return "Air conditioner"
        case "geyser": return "Water heater"
        case "chimney": return "Chimney"
        case "induction": return "Induction cooktop"
        case "refrigerator", "fridge": return "Refrigerator"
        case "ro": return "RO purifier"
        case "pump": return "Water pump"
        case "ev": return "EV charger"
        case "washing_machine": return "Washing machine"
        case "tv": return "Television"
        default: return kind.replacingOccurrences(of: "_", with: " ")
                            .capitalized
        }
    }

    var symbol: String {
        switch kind {
        case "ac": return "snowflake"
        case "geyser": return "drop.fill"
        case "chimney": return "wind"
        case "induction": return "flame.fill"
        case "refrigerator", "fridge": return "refrigerator.fill"
        case "ro": return "drop.triangle.fill"
        case "pump": return "arrow.up.circle.fill"
        case "ev": return "bolt.car.fill"
        case "washing_machine": return "washer.fill"
        case "tv": return "tv.fill"
        default: return "powerplug.fill"
        }
    }
}

/// What the interview is for. Everything downstream is derived from this
/// deterministically, so the model shapes the questions and never the wiring.
struct HouseholdProfile: Codable, Equatable {
    var name: String?
    var sanctionedLoadW: Double?
    var bedrooms: Int?
    var occupants: Int?
    var appliances: [ProfileAppliance]
    var notes: [String]
    var summary: String

    enum CodingKeys: String, CodingKey {
        case name, bedrooms, occupants, appliances, notes, summary
        case sanctionedLoadW = "sanctioned_load_w"
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        name = try? c.decodeIfPresent(String.self, forKey: .name)
        sanctionedLoadW = try? c.decodeIfPresent(Double.self,
                                                 forKey: .sanctionedLoadW)
        bedrooms = try? c.decodeIfPresent(Int.self, forKey: .bedrooms)
        occupants = try? c.decodeIfPresent(Int.self, forKey: .occupants)
        appliances = (try? c.decodeIfPresent([ProfileAppliance].self,
                                             forKey: .appliances)) ?? []
        notes = (try? c.decodeIfPresent([String].self, forKey: .notes)) ?? []
        summary = (try? c.decodeIfPresent(String.self,
                                          forKey: .summary)) ?? ""
    }

    var sanctionKW: Double { (sanctionedLoadW ?? 5000) / 1000 }

    /// Rough connected load, for the profile card. The authoritative number
    /// comes back from the solver with diversity applied.
    var indicativeConnectedW: Double {
        let watts: [String: Double] = [
            "ac": 1500, "geyser": 2000, "chimney": 250, "induction": 2000,
            "refrigerator": 200, "fridge": 200, "ro": 60, "pump": 750,
            "ev": 3300, "washing_machine": 500, "tv": 150,
        ]
        return appliances.reduce(400.0) {
            $0 + (watts[$1.kind] ?? 200) * Double($1.count)
        }
    }
}

struct InterviewTurn: Codable {
    let question: InterviewQuestion?
    let profile: HouseholdProfile?
    let done: Bool
    let source: String?

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        question = try? c.decodeIfPresent(InterviewQuestion.self,
                                          forKey: .question)
        profile = try? c.decodeIfPresent(HouseholdProfile.self,
                                         forKey: .profile)
        done = (try? c.decodeIfPresent(Bool.self, forKey: .done)) ?? false
        source = try? c.decodeIfPresent(String.self, forKey: .source)
    }
}

struct InterviewRequest: Codable {
    let answers: [InterviewAnswer]
    let profile: HouseholdProfile?
}
