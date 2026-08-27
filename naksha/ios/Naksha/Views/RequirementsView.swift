import SwiftUI

/// The conversation. One question at a time, each one chosen from what is still
/// unknown, so the user never fills in a form of forty fields.
struct RequirementsView: View {
    @EnvironmentObject private var store: DesignStore
    let rooms: [ScannedRoom]

    private var engine: QuestionEngine { QuestionEngine(rooms: rooms) }
    private var current: Question? {
        engine.nextQuestion(given: store.requirements)
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                progress

                if let q = current {
                    QuestionCard(question: q, rooms: rooms)
                        .id(q.id)
                } else {
                    finished
                }

                if !store.requirements.appliances.isEmpty {
                    collected
                }
            }
            .padding(20)
        }
        .navigationTitle("Your requirements")
        .background(Color(white: 0.97).ignoresSafeArea())
    }

    /// Derived from what has actually been recorded, so the bar cannot drift
    /// out of step with the answers.
    private var answeredCount: Int {
        var n = 0
        for room in rooms {
            let a = store.requirements.perRoom[room.name]
            if a != nil || store.requirements.appliances
                .contains(where: { $0.room == room.name }) { n += 1 }
            if a?.fan != nil { n += 1 }
            if a?.sockets != nil { n += 1 }
        }
        if store.requirements.sanctionedLoadW > 0 { n += 1 }
        return n
    }

    private var progress: some View {
        let total = max(engine.totalQuestionEstimate, 1)
        let done = min(answeredCount, total)
        return VStack(alignment: .leading, spacing: 6) {
            ProgressView(value: Double(done), total: Double(total))
                .tint(Theme.accent)
            Text(current == nil
                 ? "All set."
                 : "Question \(done + 1) of about \(total)")
                .font(.caption).foregroundColor(Theme.muted)
        }
    }

    private var finished: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label("Requirements collected", systemImage: "checkmark.seal")
                .font(.subheadline.weight(.semibold))
                .foregroundColor(Theme.accent)

            let demand = QuestionEngine.estimateDemand(store.requirements)
            HStack {
                Text("Estimated demand").font(.caption)
                    .foregroundColor(Theme.muted)
                Spacer()
                Text("\(Int(demand)) W")
                    .font(.caption.weight(.bold)).foregroundColor(Theme.ink)
            }
            if demand > store.requirements.sanctionedLoadW {
                Text("This is above your sanctioned load of "
                     + "\(Int(store.requirements.sanctionedLoadW)) W. The "
                     + "design will flag it and can stagger the heavy loads.")
                    .font(.caption).foregroundColor(Theme.warn)
            }

            Button {
                Task { await store.requestDesign() }
            } label: {
                Label("Design the installation", systemImage: "wand.and.stars")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)

            if case .ready(let design) = store.state {
                NavigationLink {
                    DesignTabsView(design: design)
                } label: {
                    Label("Open the drawings", systemImage: "doc.richtext")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
                .controlSize(.large)
            }
        }
        .padding(16)
        .background(RoundedRectangle(cornerRadius: 14).fill(Color.white))
    }

    private var collected: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("SO FAR").font(.caption2.weight(.bold))
                .foregroundColor(Theme.muted)
            ForEach(store.requirements.appliances) { a in
                HStack {
                    Text(a.name).font(.caption)
                    Spacer()
                    Text(a.room).font(.caption).foregroundColor(Theme.muted)
                    Text("\(Int(a.watts)) W")
                        .font(.caption.monospacedDigit())
                        .foregroundColor(Theme.ink)
                    Button {
                        store.requirements.appliances.removeAll { $0.id == a.id }
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(Theme.muted)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }
}

// MARK: - One question

private struct QuestionCard: View {
    @EnvironmentObject private var store: DesignStore
    let question: Question
    let rooms: [ScannedRoom]

    @State private var socketCount: Int = 0
    @State private var loadKW: Double = 5

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text(question.prompt)
                .font(.headline).foregroundColor(Theme.ink)
                .fixedSize(horizontal: false, vertical: true)
            if let helper = question.helper {
                Text(helper).font(.caption).foregroundColor(Theme.muted)
                    .fixedSize(horizontal: false, vertical: true)
            }

            switch question.kind {
            case .appliances(let room, let kind):
                appliancePicker(room: room, roomKind: kind)

            case .fan(let room):
                HStack(spacing: 10) {
                    Button("Yes") { setFan(true, room) }
                        .buttonStyle(.borderedProminent)
                    Button("No") { setFan(false, room) }
                        .buttonStyle(.bordered)
                }

            case .socketCount(let room, let suggested):
                VStack(alignment: .leading, spacing: 10) {
                    Stepper("\(socketCount == 0 ? suggested : socketCount) sockets",
                            value: Binding(
                                get: { socketCount == 0 ? suggested : socketCount },
                                set: { socketCount = $0 }),
                            in: 0...12)
                    Button("Confirm") {
                        setSockets(socketCount == 0 ? suggested : socketCount,
                                   room)
                    }
                    .buttonStyle(.borderedProminent)
                }

            case .sanctionedLoad:
                VStack(alignment: .leading, spacing: 10) {
                    HStack {
                        Slider(value: $loadKW, in: 1...15, step: 0.5)
                        Text(String(format: "%.1f kW", loadKW))
                            .font(.caption.monospacedDigit())
                            .frame(width: 62, alignment: .trailing)
                    }
                    Button("Confirm") {
                        store.requirements.sanctionedLoadW = loadKW * 1000
                    }
                    .buttonStyle(.borderedProminent)
                }

            case .confirmDemand(let demand, _):
                VStack(alignment: .leading, spacing: 10) {
                    Text("You can raise the sanction with your DISCOM, or let "
                         + "the design stagger the water heaters and air "
                         + "conditioners so they never run together.")
                        .font(.caption).foregroundColor(Theme.muted)
                    HStack(spacing: 10) {
                        Button("Raise sanction") {
                            store.requirements.sanctionedLoadW =
                                (demand / 1000).rounded(.up) * 1000
                        }
                        .buttonStyle(.borderedProminent)
                        Button("Stagger loads") {
                            // accepted as is; the solver reports the shortfall
                            store.requirements.sanctionedLoadW += 0.0001
                        }
                        .buttonStyle(.bordered)
                    }
                }
            }
        }
        .padding(18)
        .background(RoundedRectangle(cornerRadius: 16).fill(Color.white))
    }

    private func appliancePicker(room: String, roomKind: String) -> some View {
        let options = ApplianceOption.options(forRoomKind: roomKind)
        return VStack(alignment: .leading, spacing: 8) {
            ForEach(options) { option in
                Button {
                    store.requirements.appliances.append(
                        ApplianceEntry(name: option.name,
                                       watts: option.watts,
                                       room: room,
                                       kind: option.kind,
                                       dedicated: option.dedicated,
                                       vguardCategory: option.vguardCategory))
                } label: {
                    HStack {
                        Image(systemName: "plus.circle")
                            .foregroundColor(Theme.accent)
                        Text(option.name).font(.subheadline)
                            .foregroundColor(Theme.ink)
                        Spacer()
                        Text("\(Int(option.watts)) W")
                            .font(.caption.monospacedDigit())
                            .foregroundColor(Theme.muted)
                        if option.vguardCategory != nil {
                            Text("V-Guard")
                                .font(.system(size: 8, weight: .bold))
                                .padding(.horizontal, 5).padding(.vertical, 2)
                                .background(Capsule()
                                    .fill(Theme.accent.opacity(0.12)))
                                .foregroundColor(Theme.accent)
                        }
                    }
                    .padding(.vertical, 6)
                }
                .buttonStyle(.plain)
                Divider()
            }
            Button("Nothing else here") { markRoomDone(room) }
                .font(.footnote.weight(.semibold))
                .padding(.top, 4)
        }
    }

    private func markRoomDone(_ room: String) {
        var answers = store.requirements.perRoom[room] ?? RoomAnswers()
        if answers.fan == nil && !["living", "bedroom", "dining", "study"]
            .contains(rooms.first { $0.name == room }?.kind ?? "") {
            answers.fan = false
        }
        store.requirements.perRoom[room] = answers
    }

    private func setFan(_ value: Bool, _ room: String) {
        var answers = store.requirements.perRoom[room] ?? RoomAnswers()
        answers.fan = value
        store.requirements.perRoom[room] = answers
    }

    private func setSockets(_ count: Int, _ room: String) {
        var answers = store.requirements.perRoom[room] ?? RoomAnswers()
        answers.sockets = count
        store.requirements.perRoom[room] = answers
    }
}

// MARK: - Sketch fallback for phones without LiDAR

struct SketchPlanView: View {
    @EnvironmentObject private var store: DesignStore
    @State private var name = ""
    @State private var kind = "bedroom"
    @State private var width = 3.5
    @State private var depth = 3.0

    private let kinds = ["living", "bedroom", "kitchen", "bath",
                         "dining", "study", "utility", "passage"]

    var body: some View {
        Form {
            Section("Add a room") {
                TextField("Name", text: $name)
                Picker("Type", selection: $kind) {
                    ForEach(kinds, id: \.self) { Text($0.capitalized).tag($0) }
                }
                Stepper(String(format: "Width %.1f m", width),
                        value: $width, in: 1...12, step: 0.25)
                Stepper(String(format: "Depth %.1f m", depth),
                        value: $depth, in: 1...12, step: 0.25)
                Button("Add room") {
                    let x = nextOriginX()
                    store.scannedRooms.append(
                        ScannedRoom(name: name.isEmpty
                                        ? "Room \(store.scannedRooms.count + 1)"
                                        : name,
                                    kind: kind,
                                    polygon: [[x, 0], [x + width, 0],
                                              [x + width, depth], [x, depth]],
                                    doorways: [[x + width / 2, 0]]))
                    name = ""
                }
            }
            if !store.scannedRooms.isEmpty {
                Section("Rooms") {
                    ForEach(store.scannedRooms) { r in
                        HStack {
                            Text(r.name)
                            Spacer()
                            Text(String(format: "%.1f m\u{00B2}", r.areaM2))
                                .foregroundColor(Theme.muted)
                        }
                    }
                    .onDelete { store.scannedRooms.remove(atOffsets: $0) }
                }
                Section {
                    NavigationLink("Next, what goes in each room") {
                        RequirementsView(rooms: store.scannedRooms)
                    }
                }
            }
        }
        .navigationTitle("Sketch the plan")
    }

    /// Lay new rooms out left to right so the rough plan does not overlap.
    private func nextOriginX() -> Double {
        store.scannedRooms
            .flatMap { $0.polygon.map { $0[0] } }
            .max()
            .map { $0 + 0.15 } ?? 0
    }
}
