# Try Your Luck (iOS, SwiftUI)

Native version of the web app, using Apple's Liquid Glass components (`glassEffect`, `GlassEffectContainer`, `glassEffectID`, `.buttonStyle(.glassProminent)`).

Needs a Mac with Xcode 26 and an iOS 26 deployment target, because Liquid Glass first shipped in iOS 26.

1. In Xcode: File > New > Project > iOS App, name it TryYourLuck, interface SwiftUI.
2. Delete the generated `ContentView.swift` and `TryYourLuckApp.swift`.
3. Drag every file in this folder into the project (tick "Copy items if needed" and the app target). `categories.json` must be in the target so it ships in the bundle.
4. Set the deployment target to iOS 26.0 and run on an iPhone 15 simulator or your phone.

Gestures: tap Pick for me or shake the phone to pick; tap a square to go one layer deeper; hold a square to lock it to a category; the segmented control at the bottom switches between 1, 2 and 3 squares.

To update the categories, edit `build_db.py` and the `.txt` files at the repo root, run `python3 build_db.py`, and copy the new `categories.json` here.
