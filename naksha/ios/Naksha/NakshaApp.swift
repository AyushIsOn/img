import SwiftUI

@main
struct NakshaApp: App {
    @StateObject private var store = DesignStore()

    var body: some Scene {
        WindowGroup {
            VGuardScreen {
                NavigationStack {
                    HomeView()
                }
                // The backdrop is the window's background, so navigation
                // pushes slide over a continuous gradient instead of each
                // screen carrying its own copy.
                // Lists and forms show the backdrop instead of a system fill.
                .scrollContentBackground(.hidden)
            }
            .environmentObject(store)
        }
    }
}
