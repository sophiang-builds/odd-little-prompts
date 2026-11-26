import SwiftUI

@main
struct TryYourLuckApp: App {
    var body: some Scene {
        WindowGroup { ContentView() }
    }
}

extension Color {
    static let jomudBlue = Color(red: 15 / 255, green: 102 / 255, blue: 219 / 255)
    static let jomudPeach = Color(red: 240 / 255, green: 122 / 255, blue: 58 / 255)
    static let jomudLilac = Color(red: 122 / 255, green: 63 / 255, blue: 224 / 255)
    static let jomudRose = Color(red: 232 / 255, green: 80 / 255, blue: 106 / 255)
    static let jomudCream = Color(red: 251 / 255, green: 245 / 255, blue: 238 / 255)
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
