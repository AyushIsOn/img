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
            VStack(alignment: .leading, spacing: 22) {
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
                            ?? "Thanks.", size: 34)
        }
    }

    private var summaryCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            if !profile.summary.isEmpty {
                Text(profile.summary)
                    .font(.title3.weight(.medium))
                    .foregroundStyle(Theme.ink)
                    .lineSpacing(3)
                    .fixedSize(horizontal: false, vertical: true)
            }

            // Two by two rather than four across. Four columns on a phone left
            // each label about 70 points wide, so "kW connected" and "bedrooms"
            // were set at 9pt and still crowding each other.
            VStack(spacing: 14) {
                HStack(spacing: 14) {
                    metric(String(format: "%g", profile.sanctionKW),
                           "kW sanctioned")
                    metric(String(format: "%.1f",
                                  profile.indicativeConnectedW / 1000),
                           "kW connected")
                }
                HStack(spacing: 14) {
                    metric(profile.bedrooms.map(String.init) ?? "?",
                           (profile.bedrooms == 1) ? "bedroom" : "bedrooms")
                    metric(profile.occupants.map(String.init) ?? "?",
                           (profile.occupants == 1) ? "person" : "people")
                }
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

    /// Each figure sits in its own tile. The value is the thing being read, so
    /// it is set large, and the label under it is legible rather than a caption
    /// squeezed into whatever space was left.
    private func metric(_ value: String, _ label: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(value)
                .font(Brand.display(34))
                .foregroundStyle(Brand.markGradient)
                .minimumScaleFactor(0.7)
                .lineLimit(1)
            Text(label)
                .font(.system(size: 13, weight: .medium))
                .foregroundStyle(Theme.muted)
                .lineLimit(1)
                .minimumScaleFactor(0.8)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.vertical, 12)
        .padding(.horizontal, 14)
        .glassCard(14)
    }

    private var applianceCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            SectionLabel(text: "What you are planning")
            ForEach(profile.appliances) { item in
                HStack(spacing: 12) {
                    Image(systemName: item.symbol)
                        .font(.system(size: 18))
                        .foregroundStyle(Brand.amber)
                        .frame(width: 26)
                    Text(item.display)
                        .font(.body)
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
                .font(.caption)
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
