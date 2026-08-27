import SwiftUI

@main
struct NakshaApp: App {
    @StateObject private var store = DesignStore()

    var body: some Scene {
        WindowGroup {
            NavigationStack {
                HomeView()
            }
            .environmentObject(store)
            .tint(Theme.accent)
        }
    }
}
