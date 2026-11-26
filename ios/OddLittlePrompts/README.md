# Odd Little Prompts (iOS, SwiftUI)

Native version of the web app. It still has the earlier pick mode (tap a card to go deeper); the explore controls and swipe-to-swap are not ported yet. It uses using Apple's Liquid Glass components (`glassEffect`, `GlassEffectContainer`, `glassEffectID`, `.buttonStyle(.glassProminent)`).

Needs a Mac with Xcode 26 and an iOS 26 deployment target, because Liquid Glass first shipped in iOS 26.

1. In Xcode: File > New > Project > iOS App, product name OddLittlePrompts, interface SwiftUI. Set the display name (target > General > Display Name) to Odd Little Prompts.
2. Delete the generated `ContentView.swift` and `OddLittlePromptsApp.swift`.
3. Drag every Swift file and `categories.json` in this folder into the project (tick "Copy items if needed" and the app target). `categories.json` must be in the target so it ships in the bundle.
4. App icon: open Assets > AppIcon and drop `AppIcon-1024.png` into the single 1024 × 1024 slot. It is full-bleed with no transparency, as Apple requires; iOS rounds the corners.
5. Logo: in Assets, add a new Image Set named `Logo`. Set Appearances to Any, Dark, drop `logo-horizontal.svg` into Any and `logo-horizontal-dark.svg` into Dark, and tick Preserve Vector Data.
6. Set the deployment target to iOS 26.0 and run on an iPhone 15 simulator or your phone.

Gestures: tap Pick for me or shake the phone to pick; tap a square to go one layer deeper; hold a square to lock it to a category; the segmented control at the bottom switches between 1, 2 and 3 squares.

To update the categories, edit `build_db.py` and the `.txt` files at the repo root, run `python3 build_db.py`, and copy the new `categories.json` here.
