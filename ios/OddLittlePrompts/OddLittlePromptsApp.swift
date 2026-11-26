import SwiftUI

@main
struct OddLittlePromptsApp: App {
    var body: some Scene {
        WindowGroup { ContentView() }
    }
}

extension Color {
    // App palette (coral, sun, teal on navy and cream)
    static let twbCoral = Color(red: 255 / 255, green: 90 / 255, blue: 78 / 255)    // #FF5A4E
    static let twbSun = Color(red: 255 / 255, green: 194 / 255, blue: 60 / 255)     // #FFC23C
    static let twbTeal = Color(red: 46 / 255, green: 196 / 255, blue: 182 / 255)    // #2EC4B6
    static let twbNavy = Color(red: 27 / 255, green: 26 / 255, blue: 46 / 255)      // #1B1A2E
    static let twbCream = Color(red: 255 / 255, green: 246 / 255, blue: 233 / 255)   // #FFF6E9
}

// Shake the phone to pick: UIKit reports the gesture, SwiftUI listens for it.
extension Notification.Name { static let deviceDidShake = Notification.Name("deviceDidShake") }

extension UIWindow {
    open override func motionEnded(_ motion: UIEvent.EventSubtype, with event: UIEvent?) {
        if motion == .motionShake { NotificationCenter.default.post(name: .deviceDidShake, object: nil) }
        super.motionEnded(motion, with: event)
    }
}

extension View {
    func onShake(_ action: @escaping () -> Void) -> some View {
        onReceive(NotificationCenter.default.publisher(for: .deviceDidShake)) { _ in action() }
    }
}
