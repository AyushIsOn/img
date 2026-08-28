import SwiftUI

/// What goes in this room, asked once per scanned room.
///
/// Fixed questions rather than model written ones, and deliberately so. These
/// three decide the entire schedule for a room, they are the same three every
/// time, and each one carries a recommendation computed from the measured area.
/// A model adds nothing here and could omit one.
///
/// The recommendation is the point. "How many lights" is a question nobody can
/// answer well. "Two 12 W panels and a 25 W batten, about 2,050 lm for 14.6 m2,
/// which is the 140 lux a bedroom wants" is a question anyone can answer.
struct RoomBriefView: View {
    @EnvironmentObject private var store: DesignStore
    let rooms: [ScannedRoom]

    @State private var index = 0
    @State private var lights = 0
    @State private var fans = 0
    @State private var wantsAC = false
    @State private var tons = 1.0

    private var room: ScannedRoom? {
        rooms.indices.contains(index) ? rooms[index] : nil
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                if let room {
                    header(room)
                    lightingCard(room)
                    fanCard(room)
                    acCard(room)
                    nextButton(room)
                } else {
                    finished
                }
            }
            .padding(20)
        }
        .navigationTitle("What goes in each room")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear(perform: prime)
        .onChange(of: index) { _, _ in prime() }
    }

    /// Start each room on its own recommendation, so accepting the advice is
    /// the default and the user only moves the numbers they disagree with.
    private func prime() {
        guard let room else { return }
        let advice = Lighting.advise(for: room)
        lights = advice.fittings
        fans = Lighting.suggestedFans(for: room)
        wantsAC = false
        tons = room.areaM2 > 16 ? 1.5 : 1.0
    }

    // MARK: Cards

    private func header(_ room: ScannedRoom) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            SectionLabel(text: "Room \(index + 1) of \(rooms.count)")
            BrandText(text: room.name, size: 28)
            Text(String(format: "%@  ·  %.1f m² measured by the scan",
                        room.kind.capitalized, room.areaM2))
                .font(.footnote)
                .foregroundStyle(Theme.muted)
        }
    }

    private func lightingCard(_ room: ScannedRoom) -> some View {
        let advice = Lighting.advise(for: room)
        return VStack(alignment: .leading, spacing: 14) {
            Text("How many lights do you want?")
                .font(.title3.weight(.bold))
                .foregroundStyle(Theme.ink)

            counter(value: $lights, range: 0...12)

            HStack(alignment: .top, spacing: 9) {
                Image(systemName: "sparkles")
                    .font(.system(size: 11, weight: .bold))
                    .foregroundStyle(Brand.gold)
                    .padding(.top, 2)
                Text(advice.sentence)
                    .font(.caption)
                    .foregroundStyle(Theme.muted)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .padding(11)
            .glassCard(12, tinted: true)
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .glassCard(22)
    }

    private func fanCard(_ room: ScannedRoom) -> some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("How many fans do you want?")
                .font(.title3.weight(.bold))
                .foregroundStyle(Theme.ink)
            counter(value: $fans, range: 0...4)
            Text(Lighting.fanAdvice(for: room))
                .font(.caption)
                .foregroundStyle(Theme.muted)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .glassCard(22)
    }

    private func acCard(_ room: ScannedRoom) -> some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Do you want an air conditioner here?")
                .font(.title3.weight(.bold))
                .foregroundStyle(Theme.ink)

            HStack(spacing: 10) {
                Button("Yes") { wantsAC = true }
                    .buttonStyle(wantsAC ? AnyButtonStyle(.vguard)
                                         : AnyButtonStyle(.vguardGlass))
                Button("No") { wantsAC = false }
                    .buttonStyle(!wantsAC ? AnyButtonStyle(.vguard)
                                          : AnyButtonStyle(.vguardGlass))
            }

            if wantsAC {
                VStack(alignment: .leading, spacing: 10) {
                    HStack {
                        Text("Capacity").font(.caption)
                            .foregroundStyle(Theme.muted)
                        Spacer()
                        Text(String(format: "%g ton", tons))
                            .font(Brand.display(20))
                            .foregroundStyle(Brand.markGradient)
                    }
                    Slider(value: $tons, in: 0.75...2.5, step: 0.25)
                    Text(Lighting.acAdvice(for: room))
                        .font(.caption)
                        .foregroundStyle(Theme.muted)
                        .fixedSize(horizontal: false, vertical: true)
                }
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .glassCard(22)
        .animation(.spring(response: 0.32, dampingFraction: 0.8), value: wantsAC)
    }

    private func counter(value: Binding<Int>,
                         range: ClosedRange<Int>) -> some View {
        HStack(spacing: 16) {
            Button {
                value.wrappedValue = max(range.lowerBound,
                                         value.wrappedValue - 1)
            } label: {
                Image(systemName: "minus")
                    .font(.system(size: 15, weight: .bold))
                    .foregroundStyle(Theme.ink)
                    .frame(width: 44, height: 44)
                    .glassChip()
            }
            .buttonStyle(.plain)

            Text("\(value.wrappedValue)")
                .font(Brand.display(34))
                .foregroundStyle(Brand.markGradient)
                .frame(minWidth: 52)
                .contentTransition(.numericText())

            Button {
                value.wrappedValue = min(range.upperBound,
                                         value.wrappedValue + 1)
            } label: {
                Image(systemName: "plus")
                    .font(.system(size: 15, weight: .bold))
                    .foregroundStyle(Theme.ink)
                    .frame(width: 44, height: 44)
                    .glassChip()
            }
            .buttonStyle(.plain)

            Spacer()
        }
        .animation(.spring(response: 0.28, dampingFraction: 0.7),
                   value: value.wrappedValue)
    }

    // MARK: Advancing

    private func nextButton(_ room: ScannedRoom) -> some View {
        Button {
            record(room)
            if index + 1 < rooms.count { index += 1 }
            else { index = rooms.count }
        } label: {
            Label(index + 1 < rooms.count ? "Next room" : "Design the wiring",
                  systemImage: index + 1 < rooms.count
                               ? "arrow.right" : "wand.and.stars")
        }
        .buttonStyle(.vguard)
    }

    private func record(_ room: ScannedRoom) {
        store.requirements.perRoom[room.name] =
            RoomAnswers(lights: lights, fan: fans > 0, sockets:
                        QuestionEngine.suggestedSockets(for: room))
        // Fans beyond the first are recorded as extra points through the
        // appliance list, since RoomAnswers carries only a flag.
        store.requirements.appliances.removeAll {
            $0.room == room.name && ($0.kind == "ac" || $0.kind == "fan")
        }
        if fans > 1 {
            for _ in 2...fans {
                store.requirements.appliances.append(
                    ApplianceEntry(name: "Ceiling fan", watts: 75,
                                   room: room.name, kind: "fan",
                                   dedicated: false, vguardCategory: "Fans"))
            }
        }
        if wantsAC {
            store.requirements.appliances.append(
                ApplianceEntry(name: String(format: "Air conditioner %g T",
                                            tons),
                               watts: tons * 1200,
                               room: room.name, kind: "ac",
                               dedicated: true,
                               vguardCategory: "Air Conditioners"))
        }
    }

    private var finished: some View {
        VStack(alignment: .leading, spacing: 14) {
            Label("Requirements recorded", systemImage: "checkmark.seal.fill")
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(Brand.gold)

            Button {
                Task { await store.requestDesign() }
            } label: {
                Label("Design the wiring", systemImage: "wand.and.stars")
            }
            .buttonStyle(.vguard)
            .disabled({ if case .working = store.state { return true }
                        return false }())

            switch store.state {
            case .working(let message):
                HStack(spacing: 10) {
                    ProgressView().tint(Brand.amber)
                    Text(message).font(.caption).foregroundStyle(Theme.muted)
                }
            case .failed(let message):
                Text(message).font(.caption2).foregroundStyle(Theme.warn)
                    .fixedSize(horizontal: false, vertical: true)
            case .ready(let design):
                NavigationLink { DesignTabsView(design: design) } label: {
                    Label("Open the drawings", systemImage: "doc.richtext")
                }
                .buttonStyle(.vguardGlass)
            case .idle:
                EmptyView()
            }

            Button("Go back and change something") { index = 0 }
                .font(.caption)
                .foregroundStyle(Theme.muted)
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .glassCard(22, tinted: true)
    }
}

// MARK: - Lighting advice from the measured area

/// The lumen method, run on device purely to explain the recommendation.
///
/// The solver still decides what is installed. This exists so the question can
/// say why a number is suggested, in the units an owner recognises.
enum Lighting {

    struct Advice {
        let fittings: Int
        let sentence: String
    }

    /// Illuminance targets in lux, from common Indian residential practice.
    private static func lux(for kind: String) -> Double {
        switch kind {
        case "kitchen", "study", "utility": return 200
        case "living", "dining":            return 150
        case "bath":                        return 120
        default:                            return 140      // bedroom
        }
    }

    static func advise(for room: ScannedRoom) -> Advice {
        let area = max(room.areaM2, 1)
        let target = lux(for: room.kind)
        // Maintenance factor and utilisation, folded into one figure, which is
        // the usual shortcut for a domestic room with light walls.
        let required = target * area / 0.7
        let panelLumens = 1_100.0                  // a 12 W LED panel
        let battenLumens = 2_200.0                 // a 25 W LED batten

        var fittings = max(1, Int((required / panelLumens).rounded()))
        var text: String

        if area >= 10 && fittings >= 2 {
            // A batten plus panels is what these rooms actually get, and it
            // spreads light better than panels alone.
            let panels = max(1, fittings - 2)
            let total = Double(panels) * panelLumens + battenLumens
            fittings = panels + 1
            text = String(format:
                "Based on the scan, %d × 12 W panel%@ and one 25 W tubelight, "
                + "about %.0f lm across %.1f m², reaches the %.0f lux a %@ "
                + "wants. Put the tubelight on the wall opposite the window.",
                panels, panels == 1 ? "" : "s", total, area, target, room.kind)
        } else {
            let total = Double(fittings) * panelLumens
            text = String(format:
                "Based on the scan, %d × 12 W panel%@, about %.0f lm across "
                + "%.1f m², reaches the %.0f lux a %@ wants.",
                fittings, fittings == 1 ? "" : "s", total, area, target,
                room.kind)
        }
        return Advice(fittings: fittings, sentence: text)
    }

    static func suggestedFans(for room: ScannedRoom) -> Int {
        guard ["living", "bedroom", "dining", "study"].contains(room.kind)
        else { return 0 }
        return room.areaM2 > 20 ? 2 : 1
    }

    static func fanAdvice(for room: ScannedRoom) -> String {
        guard ["living", "bedroom", "dining", "study"].contains(room.kind) else {
            return "A \(room.kind) does not normally take a ceiling fan. An "
                 + "exhaust point is added separately."
        }
        return room.areaM2 > 20
            ? String(format: "At %.1f m² two 1200 mm sweep fans cover the room "
                     + "more evenly than one.", room.areaM2)
            : String(format: "One 1200 mm sweep fan suits %.1f m².",
                     room.areaM2)
    }

    static func acAdvice(for room: ScannedRoom) -> String {
        // The usual domestic rule of thumb, roughly 0.06 ton per square metre
        // for a room under a normal ceiling.
        let suggested = max(0.75, (room.areaM2 * 0.06 / 0.25).rounded() * 0.25)
        return String(format: "For %.1f m², about %g ton is the usual choice. "
                      + "It gets a dedicated circuit and its own isolator.",
                      room.areaM2, suggested)
    }
}

/// Lets a button style be chosen at the call site, which SwiftUI otherwise
/// makes awkward because the two styles are different types.
struct AnyButtonStyle: ButtonStyle {
    private let make: (Configuration) -> AnyView

    init<S: ButtonStyle>(_ style: S) {
        make = { configuration in
            AnyView(style.makeBody(configuration: configuration))
        }
    }

    func makeBody(configuration: Configuration) -> some View {
        make(configuration)
    }
}
