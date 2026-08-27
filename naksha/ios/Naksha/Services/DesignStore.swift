import Foundation
import Combine

/// Holds the current design and knows how to obtain one.
///
/// Two sources are supported. The bundled sample lets the app run and be
/// demonstrated with real solver output and no network. The remote solver is
/// the production path: the scanned or drawn geometry plus the collected
/// requirements are posted, and the same JSON contract comes back.
///
/// The engineering deliberately does not run in the app. It runs in one
/// place, is version controlled, and is auditable.
@MainActor
final class DesignStore: ObservableObject {

    enum State {
        case idle
        case working(String)
        case ready(Design)
        case failed(String)
    }

    @Published var state: State = .idle
    @Published var requirements = RequirementSet()
    @Published var scannedRooms: [ScannedRoom] = []

    /// Address of the solver, entered by the user and remembered between
    /// launches. Empty means stay on the bundled sample, which keeps the app
    /// usable with no laptop on the network.
    @Published var solverAddress: String =
        UserDefaults.standard.string(forKey: "solverAddress") ?? "" {
        didSet { UserDefaults.standard.set(solverAddress,
                                           forKey: "solverAddress") }
    }

    @Published var reachability: Reachability = .unknown

    enum Reachability: Equatable {
        case unknown, checking, ok(String), failed(String)
    }

    var solverEndpoint: URL? {
        let trimmed = solverAddress.trimmingCharacters(in: .whitespaces)
        guard !trimmed.isEmpty else { return nil }
        let withScheme = trimmed.contains("://") ? trimmed
                                                 : "http://\(trimmed)"
        return URL(string: withScheme)
    }

    var usingSolver: Bool { solverEndpoint != nil }

    /// Confirms the phone can actually reach the laptop before the user gets
    /// as far as designing, because "it silently used the sample instead" is a
    /// confusing way to fail.
    func checkReachability() async {
        guard let endpoint = solverEndpoint else {
            reachability = .unknown
            return
        }
        reachability = .checking
        do {
            var request = URLRequest(
                url: endpoint.appendingPathComponent("health"))
            request.timeoutInterval = 5
            let (data, response) = try await URLSession.shared.data(for: request)
            guard let http = response as? HTTPURLResponse,
                  (200..<300).contains(http.statusCode) else {
                reachability = .failed("Server responded with an error")
                return
            }
            let info = try? JSONSerialization.jsonObject(with: data)
                as? [String: Any]
            let plans = (info?["plans"] as? [String])?.count ?? 0
            reachability = .ok("Connected, \(plans) sample plans available")
        } catch {
            reachability = .failed(error.localizedDescription)
        }
    }

    var design: Design? {
        if case .ready(let d) = state { return d }
        return nil
    }

    // MARK: - Sources

    func loadSample() {
        state = .working("Loading sample design")
        do {
            guard let url = Bundle.main.url(forResource: "sample-2bhk",
                                            withExtension: "json") else {
                throw StoreError.missingResource("sample-2bhk.json")
            }
            let data = try Data(contentsOf: url)
            let design = try JSONDecoder().decode(Design.self, from: data)
            state = .ready(design)
        } catch {
            state = .failed(Self.describe(error))
        }
    }

    func requestDesign() async {
        guard let endpoint = solverEndpoint else {
            // No solver configured. Say so rather than quietly substituting
            // the sample, which looks like the scan was simply ignored.
            state = .failed("No solver address set, so the scanned rooms "
                          + "cannot be designed. Set one in Settings, or open "
                          + "the sample design instead.")
            return
        }
        state = .working("Designing the installation")
        do {
            var request = URLRequest(url: endpoint.appendingPathComponent("design"))
            request.httpMethod = "POST"
            request.setValue("application/json",
                             forHTTPHeaderField: "Content-Type")
            request.httpBody = try JSONEncoder().encode(
                DesignRequest(rooms: scannedRooms,
                              requirements: requirements))
            let (data, response) = try await URLSession.shared.data(for: request)
            if let http = response as? HTTPURLResponse,
               !(200..<300).contains(http.statusCode) {
                throw StoreError.server(http.statusCode)
            }
            let design = try JSONDecoder().decode(Design.self, from: data)
            state = .ready(design)
        } catch {
            state = .failed(Self.describe(error))
        }
    }

    func reset() {
        state = .idle
        requirements = RequirementSet()
        scannedRooms = []
    }

    // MARK: - Errors

    enum StoreError: LocalizedError {
        case missingResource(String)
        case server(Int)

        var errorDescription: String? {
            switch self {
            case .missingResource(let name):
                return "\(name) is missing from the app bundle."
            case .server(let code):
                return "The solver returned status \(code)."
            }
        }
    }

    private static func describe(_ error: Error) -> String {
        if let local = error as? LocalizedError,
           let text = local.errorDescription { return text }
        if let decoding = error as? DecodingError {
            return "The design could not be decoded: \(decoding)"
        }
        return error.localizedDescription
    }
}

// MARK: - Payloads

/// A room captured by RoomPlan or drawn by hand, reduced to what the solver
/// needs: a floor polygon, a room type, and the doorways.
struct ScannedRoom: Codable, Identifiable {
    var id = UUID()
    var name: String
    var kind: String
    var polygon: [[Double]]
    var doorways: [[Double]]

    var areaM2: Double {
        guard polygon.count > 2 else { return 0 }
        var sum = 0.0
        for i in polygon.indices {
            let a = polygon[i]
            let b = polygon[(i + 1) % polygon.count]
            sum += a[0] * b[1] - b[0] * a[1]
        }
        return abs(sum) / 2
    }
}

struct DesignRequest: Codable {
    let rooms: [ScannedRoom]
    let requirements: RequirementSet
}
