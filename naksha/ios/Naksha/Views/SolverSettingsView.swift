import SwiftUI

/// Where the solver lives.
///
/// The design engine runs on a laptop rather than on the phone, so the two have
/// to find each other. That is a real setup step and hiding it causes a worse
/// failure: the user scans a house, taps design, and gets the sample back with
/// no explanation. This screen makes the connection explicit and testable
/// before it matters.
struct SolverSettingsView: View {
    @EnvironmentObject private var store: DesignStore
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    TextField("192.168.1.42:8000", text: $store.solverAddress)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                        .keyboardType(.URL)
                    Button {
                        Task { await store.checkReachability() }
                    } label: {
                        HStack {
                            Text("Test connection")
                            Spacer()
                            status
                        }
                    }
                    .disabled(store.solverEndpoint == nil)
                } header: {
                    Text("Solver address")
                } footer: {
                    Text("Start the solver on your Mac with "
                         + "`python3 serve.py`. It prints the address to use. "
                         + "The phone and the Mac must be on the same Wi-Fi. "
                         + "Leave this empty to work from the bundled sample "
                         + "design only.")
                }

                Section {
                    Label(store.usingSolver
                          ? "Scanned rooms will be designed by the solver"
                          : "No solver set, only the sample design is available",
                          systemImage: store.usingSolver
                          ? "checkmark.circle" : "info.circle")
                        .font(.footnote)
                        .foregroundColor(store.usingSolver
                                         ? Theme.accent : Theme.muted)
                } header: { Text("Current behaviour") }

                Section {
                    stepRow(1, "On your Mac, in `naksha/solver`, run "
                             + "`python3 serve.py`")
                    stepRow(2, "Copy the `http://...:8000` address it prints")
                    stepRow(3, "Paste it above and tap Test connection")
                    stepRow(4, "Scan your rooms, answer the questions, then "
                             + "tap Design the installation")
                } header: { Text("Setting it up") }
            }
            .scrollContentBackground(.hidden)
            .background(VGuardBackdrop())
            .navigationTitle("Solver")
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { dismiss() }
                }
            }
            .task { await store.checkReachability() }
        }
    }

    @ViewBuilder private var status: some View {
        switch store.reachability {
        case .unknown:
            Text("Not tested").font(.caption).foregroundColor(Theme.muted)
        case .checking:
            ProgressView()
        case .ok(let message):
            Label(message, systemImage: "checkmark.circle.fill")
                .font(.caption).foregroundColor(Theme.accent)
                .labelStyle(.titleAndIcon)
        case .failed(let message):
            Label(message, systemImage: "xmark.circle.fill")
                .font(.caption).foregroundColor(Theme.warn)
                .lineLimit(2)
        }
    }

    private func stepRow(_ n: Int, _ text: String) -> some View {
        HStack(alignment: .top, spacing: 10) {
            Text("\(n)")
                .font(.caption2.weight(.bold))
                .foregroundColor(.white)
                .frame(width: 17, height: 17)
                .background(Circle().fill(Theme.accent))
            Text(.init(text)).font(.caption)
            Spacer(minLength: 0)
        }
    }
}
