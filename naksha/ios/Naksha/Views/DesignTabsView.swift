import SwiftUI

/// The finished design: drawing, circuit schedule, AR overlay, material list.
struct DesignTabsView: View {
    let design: Design

    var body: some View {
        TabView {
            DrawingTab(design: design)
                .tabItem { Label("Drawing", systemImage: "doc.richtext") }
            ScheduleTab(design: design)
                .tabItem { Label("Circuits", systemImage: "list.bullet.indent") }
            NavigationStack { ARWiringView(design: design) }
                .tabItem { Label("AR", systemImage: "arkit") }
            NavigationStack { AsBuiltView(design: design) }
                .tabItem { Label("As-built", systemImage: "checkmark.seal") }
            MaterialListView(design: design)
                .tabItem { Label("Buy", systemImage: "cart") }
        }
        .navigationTitle(design.plan.name)
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - Drawing

private struct DrawingTab: View {
    let design: Design
    @State private var highlighted: String? = nil
    @State private var showCircuits = true

    var body: some View {
        VStack(spacing: 0) {
            PlanCanvasView(design: design,
                           showCircuits: showCircuits,
                           highlighted: highlighted)
                .frame(maxHeight: .infinity)

            VStack(spacing: 10) {
                Toggle("Show conduit routing", isOn: $showCircuits)
                    .font(.footnote)
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 7) {
                        ForEach(Array(design.circuits.enumerated()),
                                id: \.1.id) { i, c in
                            Button {
                                highlighted = highlighted == c.id ? nil : c.id
                            } label: {
                                Text(c.id)
                                    .font(.caption2.weight(.semibold))
                                    .padding(.vertical, 5)
                                    .padding(.horizontal, 9)
                                    .background(Capsule().fill(
                                        highlighted == c.id
                                        ? Theme.circuitColour(i)
                                        : Theme.circuitColour(i).opacity(0.15)))
                                    .foregroundColor(highlighted == c.id
                                                     ? .white
                                                     : Theme.circuitColour(i))
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }
                if design.summary.demandExceedsSanction {
                    Label(String(format:
                        "Maximum demand %.0f W exceeds the %.0f W sanction",
                        design.summary.maximumDemandW,
                        design.summary.sanctionedLoadW),
                          systemImage: "exclamationmark.triangle.fill")
                        .font(.caption2).foregroundColor(Theme.warn)
                }
            }
            .padding(14)
            .background(Color.white)
        }
    }
}

// MARK: - Circuit schedule

private struct ScheduleTab: View {
    let design: Design

    var body: some View {
        List {
            Section {
                row("Floor area",
                    String(format: "%.1f m\u{00B2}", design.summary.floorAreaM2))
                row("Connected load",
                    String(format: "%.0f W", design.summary.connectedLoadW))
                row("Maximum demand",
                    String(format: "%.0f W", design.summary.maximumDemandW))
                row("Sanctioned load",
                    String(format: "%.0f W", design.summary.sanctionedLoadW))
                row("Conduit",
                    String(format: "%.1f m", design.summary.conduitM))
            } header: { Text("Summary") }

            Section {
                ForEach(Array(design.circuits.enumerated()), id: \.1.id) { i, c in
                    VStack(alignment: .leading, spacing: 5) {
                        HStack {
                            Circle().fill(Theme.circuitColour(i))
                                .frame(width: 8, height: 8)
                            Text(c.id).font(.subheadline.weight(.bold))
                            Text(c.kind.displayName)
                                .font(.caption).foregroundColor(Theme.muted)
                            Spacer()
                            Text(String(format: "%.0f W", c.connectedWatts))
                                .font(.caption.monospacedDigit())
                        }
                        HStack(spacing: 14) {
                            tag("\(Int(c.mcbAmps)) A MCB")
                            tag(String(format: "%g mm\u{00B2}", c.cableMM2))
                            tag(String(format: "%.0f m", c.routeLengthM))
                            tag(String(format: "%.1f%% drop", c.vdropPercent))
                        }
                        let rooms = Set(design.points
                            .filter { c.pointIDs.contains($0.id) }
                            .map(\.room)).sorted()
                        Text(rooms.joined(separator: ", "))
                            .font(.caption2).foregroundColor(Theme.muted)
                    }
                    .padding(.vertical, 3)
                }
            } header: { Text("Final circuits") }

            if !design.checks.isEmpty {
                Section {
                    ForEach(design.checks, id: \.self) { note in
                        Label(note, systemImage: "exclamationmark.circle")
                            .font(.caption).foregroundColor(Theme.warn)
                    }
                } header: { Text("Design notes") }
            }
        }
    }

    private func row(_ k: String, _ v: String) -> some View {
        HStack {
            Text(k).font(.subheadline)
            Spacer()
            Text(v).font(.subheadline.weight(.semibold).monospacedDigit())
        }
    }

    private func tag(_ text: String) -> some View {
        Text(text).font(.system(size: 10, weight: .medium))
            .padding(.vertical, 3).padding(.horizontal, 7)
            .background(Capsule().fill(Color(white: 0.94)))
            .foregroundColor(Theme.ink)
    }
}

// MARK: - Material list and product suggestions

struct MaterialListView: View {
    let design: Design

    var body: some View {
        List {
            Section {
                ForEach(design.billOfQuantities.lines) { line in
                    HStack {
                        VStack(alignment: .leading, spacing: 1) {
                            Text(line.item).font(.subheadline)
                            Text(String(format: "%g %@ at Rs %.0f",
                                        line.qty, line.unit, line.rate))
                                .font(.caption2).foregroundColor(Theme.muted)
                        }
                        Spacer()
                        Text(String(format: "Rs %.0f", line.amount))
                            .font(.subheadline.monospacedDigit())
                    }
                }
                HStack {
                    Text("Material total").font(.subheadline.weight(.bold))
                    Spacer()
                    Text(String(format: "Rs %.0f",
                                design.billOfQuantities.total))
                        .font(.subheadline.weight(.bold).monospacedDigit())
                        .foregroundColor(Theme.accent)
                }
            } header: { Text("Bill of quantities") }
              footer: { Text("Quantities include a 10% cutting allowance on "
                             + "cable. Rates are indicative.") }

            Section {
                ForEach(ProductCatalogue.recommendations(for: design)) { rec in
                    VStack(alignment: .leading, spacing: 3) {
                        HStack(alignment: .firstTextBaseline) {
                            Text(rec.product.name)
                                .font(.subheadline.weight(.semibold))
                            Spacer()
                            Text("x\(rec.quantity)")
                                .font(.caption.monospacedDigit())
                                .foregroundColor(Theme.muted)
                            Text(String(format: "Rs %.0f", rec.lineTotal))
                                .font(.subheadline.monospacedDigit())
                                .foregroundColor(Theme.ink)
                        }
                        Text(rec.product.spec)
                            .font(.caption2).foregroundColor(Theme.muted)
                        Text(rec.reason)
                            .font(.caption2).foregroundColor(Theme.accent)
                    }
                    .padding(.vertical, 3)
                }
                HStack {
                    Text("Product total").font(.subheadline.weight(.bold))
                    Spacer()
                    Text(String(format: "Rs %.0f",
                                ProductCatalogue.total(for: design)))
                        .font(.subheadline.weight(.bold).monospacedDigit())
                        .foregroundColor(Theme.accent)
                }
            } header: { Text("Recommended for this design") }
              footer: { Text("Every line is here because the design produced "
                             + "a point that needs it. Nothing is merchandised "
                             + "separately, so the list cannot drift from what "
                             + "the house actually needs. Prices indicative.") }
        }
    }
}
