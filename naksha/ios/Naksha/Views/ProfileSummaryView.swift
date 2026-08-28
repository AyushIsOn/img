import SwiftUI

/// What the interview understood, and the two ways to give it a floor plan.
///
/// Worth showing rather than skipping past. It is the moment the user can see
/// that the answers were actually comprehended, and it is where the honest
/// division of labour is visible: the model summarised the household, and the
/// load figures beside it come from the rule engine.
struct ProfileSummaryView: View {
    @EnvironmentObject private var store: DesignStore
    let profile: HouseholdProfile

    private var overSanction: Bool {
        profile.indicativeConnectedW > (profile.sanctionedLoadW ?? 5000)
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                greeting
                summaryCard
                if !profile.appliances.isEmpty { applianceCard }
                if !profile.notes.isEmpty { notesCard }
                if case .ready(let design) = store.state {
                    readyCard(design)
                }
                nextSteps
                Button("Redo the interview") { store.restartInterview() }
                    .font(.caption)
                    .foregroundStyle(Theme.muted)
                    .padding(.top, 2)
            }
            .padding(20)
        }
    }

    private var greeting: some View {
        VStack(alignment: .leading, spacing: 6) {
            SectionLabel(text: "Your profile")
            BrandText(text: profile.name.map { "Thanks, \($0)." }
                            ?? "Thanks.", size: 30)
        }
    }

    private var summaryCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            if !profile.summary.isEmpty {
                Text(profile.summary)
                    .font(.callout)
                    .foregroundStyle(Theme.ink)
                    .fixedSize(horizontal: false, vertical: true)
            }

            HStack(spacing: 0) {
                metric(String(format: "%g", profile.sanctionKW), "kW sanction")
                divider
                metric(profile.bedrooms.map(String.init) ?? "?", "bedrooms")
                divider
                metric(profile.occupants.map(String.init) ?? "?", "people")
                divider
                metric(String(format: "%.1f",
                              profile.indicativeConnectedW / 1000),
                       "kW connected")
            }

            if overSanction {
                Label("Your connected load is above the sanction. The design "
                      + "will flag it and can stagger the heavy circuits.",
                      systemImage: "exclamationmark.triangle.fill")
                    .font(.caption)
                    .foregroundStyle(Theme.warn)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .glassCard(22, tinted: true)
    }

    private var divider: some View {
        Rectangle().fill(Color.white.opacity(0.12))
            .frame(width: 1, height: 30)
    }

    private func metric(_ value: String, _ label: String) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(value)
                .font(Brand.display(22))
                .foregroundStyle(Brand.markGradient)
            Text(label)
                .font(.system(size: 9, weight: .medium))
                .foregroundStyle(Theme.muted)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private var applianceCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            SectionLabel(text: "What you are planning")
            ForEach(profile.appliances) { item in
                HStack(spacing: 12) {
                    Image(systemName: item.symbol)
                        .font(.system(size: 14))
                        .foregroundStyle(Brand.amber)
                        .frame(width: 22)
                    Text(item.display)
                        .font(.subheadline)
                        .foregroundStyle(Theme.ink)
                    Spacer()
                    if item.count > 1 {
                        Text("x\(item.count)")
                            .font(.caption.weight(.bold).monospacedDigit())
                            .foregroundStyle(Brand.gold)
                    }
                }
            }
            Text("These are placed in the right rooms automatically once you "
                 + "scan, from the room type and its size.")
                .font(.caption2)
                .foregroundStyle(Theme.muted)
                .fixedSize(horizontal: false, vertical: true)
                .padding(.top, 2)
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .glassCard(22)
    }

    private var notesCard: some View {
        VStack(alignment: .leading, spacing: 9) {
            SectionLabel(text: "Noted")
            ForEach(profile.notes, id: \.self) { note in
                HStack(alignment: .top, spacing: 8) {
                    Circle().fill(Brand.amber).frame(width: 4, height: 4)
                        .padding(.top, 6)
                    Text(note).font(.caption).foregroundStyle(Theme.muted)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .glassCard(22)
    }

    private func readyCard(_ design: Design) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            SectionLabel(text: "Design ready")
            NavigationLink { DesignTabsView(design: design) } label: {
                VStack(alignment: .leading, spacing: 10) {
                    PlanCanvasView(design: design, showCircuits: true)
                        .frame(height: 190)
                        .clipShape(RoundedRectangle(cornerRadius: 12,
                                                    style: .continuous))
                    HStack(spacing: 16) {
                        metric("\(design.points.count)", "points")
                        metric("\(design.circuits.count)", "circuits")
                        metric(String(format: "%.0f m",
                                      design.summary.conduitM), "conduit")
                        metric(String(format: "Rs %.0f",
                                      design.billOfQuantities.total),
                               "material")
                    }
                }
                .padding(14)
                .glassCard(20, tinted: true)
            }
            .buttonStyle(.plain)
        }
    }

    private var nextSteps: some View {
        VStack(alignment: .leading, spacing: 12) {
            SectionLabel(text: "Now give us the floor plan")

            NavigationLink { RoomScanView() } label: {
                Card(icon: "camera.viewfinder",
                     title: "Scan the house",
                     detail: "Walk each room with the LiDAR scanner. Walls, "
                           + "doors and furniture are measured for you.")
            }
            .buttonStyle(.plain)

            NavigationLink { PlanImportView() } label: {
                Card(icon: "doc.viewfinder",
                     title: "Use the architect's plan",
                     detail: "Import a photo or PDF, set the scale, then trace "
                           + "the rooms over it.")
            }
            .buttonStyle(.plain)

            NavigationLink { SketchPlanView() } label: {
                Card(icon: "square.on.square.dashed",
                     title: "Draw it roughly",
                     detail: "No LiDAR needed. Sketch the rooms and give "
                           + "approximate sizes.")
            }
            .buttonStyle(.plain)
        }
    }
}
