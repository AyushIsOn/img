import RoomPlan
import SwiftUI

struct HomeView: View {
    @EnvironmentObject private var store: DesignStore

    private var lidarAvailable: Bool {
        RoomCaptureSession.isSupported
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                header

                VStack(spacing: 12) {
                    NavigationLink {
                        RoomScanView()
                    } label: {
                        Card(icon: "camera.viewfinder",
                             title: "Scan the house",
                             detail: lidarAvailable
                                ? "Walk each room with the LiDAR scanner. "
                                + "Walls, doors and windows are measured for you."
                                : "Needs a LiDAR device, an iPhone Pro or "
                                + "iPad Pro. Use the sample design instead.",
                             enabled: lidarAvailable)
                    }
                    .disabled(!lidarAvailable)

                    NavigationLink {
                        PlanImportView()
                    } label: {
                        Card(icon: "doc.viewfinder",
                             title: "Use the architect's plan",
                             detail: "Import a photo or PDF, set the scale, "
                                   + "then trace the rooms over it.")
                    }

                    NavigationLink {
                        SketchPlanView()
                    } label: {
                        Card(icon: "square.on.square.dashed",
                             title: "Draw it roughly",
                             detail: "No LiDAR needed. Sketch the rooms and give "
                                 + "approximate sizes.")
                    }

                    Button {
                        store.loadSample()
                    } label: {
                        Card(icon: "doc.text.magnifyingglass",
                             title: "Open the sample design",
                             detail: "A finished 2 BHK, straight from the design "
                                 + "engine. Best way to see the output.")
                    }
                    .buttonStyle(.plain)
                }

                stateSection
            }
            .padding(20)
        }
        .navigationTitle("NAKSHA")
        .background(Color(white: 0.97).ignoresSafeArea())
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("Design the wiring, then order the wire.")
                .font(.title3.weight(.semibold))
                .foregroundColor(Theme.ink)
            Text("Lay out your lighting, sockets, water and gas points before "
                 + "the walls are closed. You get a drawing your electrician "
                 + "can build from, and a material list that adds up.")
                .font(.footnote)
                .foregroundColor(Theme.muted)
        }
    }

    @ViewBuilder private var stateSection: some View {
        switch store.state {
        case .idle:
            EmptyView()

        case .working(let message):
            HStack(spacing: 10) {
                ProgressView()
                Text(message).font(.footnote).foregroundColor(Theme.muted)
            }
            .padding(.top, 4)

        case .failed(let message):
            VStack(alignment: .leading, spacing: 6) {
                Label("Could not build the design", systemImage:
                        "exclamationmark.triangle")
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(Theme.warn)
                Text(message).font(.caption).foregroundColor(Theme.muted)
                Button("Try the sample") { store.loadSample() }
                    .font(.caption.weight(.semibold))
            }
            .padding(14)
            .background(RoundedRectangle(cornerRadius: 12)
                .fill(Theme.warn.opacity(0.08)))

        case .ready(let design):
            VStack(alignment: .leading, spacing: 12) {
                Text("Ready").font(.caption.weight(.bold))
                    .foregroundColor(Theme.accent)
                NavigationLink {
                    DesignTabsView(design: design)
                } label: {
                    VStack(alignment: .leading, spacing: 10) {
                        PlanCanvasView(design: design, showCircuits: true)
                            .frame(height: 210)
                            .clipShape(RoundedRectangle(cornerRadius: 10))
                        HStack(spacing: 16) {
                            stat("\(design.points.count)", "points")
                            stat("\(design.circuits.count)", "circuits")
                            stat(String(format: "%.0f m",
                                        design.summary.conduitM), "conduit")
                            stat(String(format: "Rs %.0f",
                                        design.billOfQuantities.total),
                                 "material")
                        }
                        Text(design.plan.name)
                            .font(.footnote.weight(.semibold))
                            .foregroundColor(Theme.ink)
                    }
                    .padding(14)
                    .background(RoundedRectangle(cornerRadius: 14)
                        .fill(Color.white))
                }
                .buttonStyle(.plain)
            }
        }
    }

    private func stat(_ value: String, _ label: String) -> some View {
        VStack(alignment: .leading, spacing: 1) {
            Text(value).font(.caption.weight(.bold)).foregroundColor(Theme.ink)
            Text(label).font(.system(size: 9)).foregroundColor(Theme.muted)
        }
    }
}

// MARK: - Reusable card

struct Card: View {
    let icon: String
    let title: String
    let detail: String
    var enabled: Bool = true

    var body: some View {
        HStack(alignment: .top, spacing: 14) {
            Image(systemName: icon)
                .font(.title3)
                .foregroundColor(enabled ? Theme.accent : Theme.muted)
                .frame(width: 28)
            VStack(alignment: .leading, spacing: 3) {
                Text(title).font(.subheadline.weight(.semibold))
                    .foregroundColor(enabled ? Theme.ink : Theme.muted)
                Text(detail).font(.caption).foregroundColor(Theme.muted)
                    .fixedSize(horizontal: false, vertical: true)
            }
            Spacer(minLength: 0)
        }
        .padding(16)
        .background(RoundedRectangle(cornerRadius: 14).fill(Color.white))
    }
}
