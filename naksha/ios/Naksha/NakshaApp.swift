import SwiftUI

@main
struct NakshaApp: App {
    @StateObject private var store = DesignStore()

    var body: some Scene {
        WindowGroup {
            VGuardScreen {
                NavigationStack {
                    RootView()
                }
                // Lists and forms show the backdrop instead of a system fill.
                .scrollContentBackground(.hidden)
            }
            .environmentObject(store)
        }
    }
}

/// The app opens on the interview, because nothing can be designed without the
/// sanctioned load and a picture of what the household intends to own.
///
/// The solver settings live in the toolbar at every stage, not just on the home
/// screen. The interview itself needs the solver, so putting that control
/// behind the interview would have made the app impossible to set up.
struct RootView: View {
    @EnvironmentObject private var store: DesignStore
    @State private var showingSettings = false

    var body: some View {
        content
            .navigationTitle(title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button { showingSettings = true } label: {
                        Image(systemName: store.usingSolver
                              ? "antenna.radiowaves.left.and.right"
                              : "gearshape")
                            .foregroundStyle(store.usingSolver
                                             ? Brand.amber : Theme.muted)
                    }
                }
            }
            .sheet(isPresented: $showingSettings) { SolverSettingsView() }
    }

    private var title: String {
        if let profile = store.profile, store.interviewDone {
            return profile.name.map { "\($0)'s home" } ?? "Your home"
        }
        return ""
    }

    @ViewBuilder private var content: some View {
        if let profile = store.profile, store.interviewDone {
            ProfileSummaryView(profile: profile)
        } else {
            InterviewView()
        }
    }
}
