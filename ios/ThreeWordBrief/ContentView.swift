import SwiftUI

struct ContentView: View {
    @AppStorage("squareCount") private var count = 1
    @State private var slots: [Slot] = [Slot()]
    @State private var pickTick = 0
    @State private var sheetFor: Int? = nil
    @Namespace private var glass

    var body: some View {
        ZStack {
            Wash(seed: pickTick).ignoresSafeArea()

            VStack(spacing: 0) {
                // Three Word Brief logo. Add brand/logo-horizontal.svg (and the -dark one as its
                // Dark appearance) to Assets as an image set named "Logo", with Preserve Vector Data on.
                Image("Logo")
                    .resizable()
                    .scaledToFit()
                    .frame(height: 30)
                    .accessibilityLabel("Three Word Brief")
                    .padding(.top, 8)

                Spacer()

                // 1 square: centred. 2: stacked squares. 3: full-width cards filling the space.
                GlassEffectContainer(spacing: 14) {
                    VStack(spacing: 12) {
                        ForEach(slots.indices, id: \.self) { i in
                            SquareView(slot: slots[i], count: slots.count)
                                .glassEffect(.regular.interactive(), in: .rect(cornerRadius: slots.count == 3 ? 30 : 38))
                                .glassEffectID(slots[i].id, in: glass)
                                .onTapGesture { slots[i].path.isEmpty ? pickOne(i) : deeper(i) }
                                .onLongPressGesture { sheetFor = i }
                        }
                    }
                    .frame(maxWidth: slots.count == 1 ? 340 : .infinity,
                           maxHeight: slots.count == 1 ? nil : .infinity)
                }
                .frame(maxHeight: slots.count == 1 ? nil : .infinity)
                .padding(.horizontal, 20)
                .animation(.spring(response: 0.45, dampingFraction: 0.72), value: slots.count)

                Button("Pick for me", action: pickAll)
                    .font(.title3.weight(.semibold))
                    .buttonStyle(.glassProminent)
                    .controlSize(.large)
                    .tint(.twbTeal)
                    .foregroundStyle(Color.twbNavy)
                    .padding(.top, 26)

                if slots.count == 1 { Spacer() } else { Spacer().frame(height: 22) }

                Picker("Squares", selection: $count) {
                    Image(systemName: "square.fill").tag(1)
                    Image(systemName: "rectangle.grid.1x2.fill").tag(2)
                    Image(systemName: "line.3.horizontal").tag(3)
                }
                .pickerStyle(.segmented)
                .frame(width: 180)
                .padding(.bottom, 12)
            }
        }
        .onAppear { resize(to: count) }
        .onChange(of: count) { _, n in resize(to: n) }
        .onShake(pickAll)
        .sensoryFeedback(.impact(weight: .medium), trigger: pickTick)
        .sheet(item: Binding(get: { sheetFor.map(SheetTarget.init) }, set: { sheetFor = $0?.index })) { t in
            CategorySheet(current: slots[t.index].lock) { choice in
                slots[t.index].lock = choice
                sheetFor = nil
                pickOne(t.index)
            }
            .presentationDetents([.medium, .large])
        }
    }

    // MARK: picking

    private func resize(to n: Int) {
        while slots.count < n { slots.append(Slot()) }
        if slots.count > n { slots.removeLast(slots.count - n) }
    }

    /// Different categories across squares in one pick (sampling without replacement).
    private func pickAll() {
        var taken = Set(slots.compactMap(\.lock))
        for i in slots.indices {
            let cat: Node
            if let lock = slots[i].lock, let c = Deck.categories.first(where: { $0.name == lock }) {
                cat = c
            } else {
                let pool = Deck.categories.filter { !taken.contains($0.name) }
                guard let c = pool.randomElement() else { continue }
                cat = c
            }
            taken.insert(cat.name)
            slots[i].path = Deck.descend([cat], steps: 2)
        }
        spin(Array(slots.indices))
    }

    private func pickOne(_ i: Int) {
        let others = Set(slots.indices.filter { $0 != i }.compactMap { slots[$0].path.first?.name })
        let pool = slots[i].lock.flatMap { l in Deck.categories.filter { $0.name == l } }
            ?? Deck.categories.filter { !others.contains($0.name) }
        guard let cat = pool.randomElement() else { return }
        slots[i].path = Deck.descend([cat], steps: 2)
        spin([i])
    }

    private func deeper(_ i: Int) {
        guard slots[i].canGoDeeper else { return }
        slots[i].path = Deck.descend(slots[i].path, steps: 1)
        spin([i])
    }

    /// Slot-reel reveal. The result is already decided; the flicker is decoration.
    private func spin(_ indices: [Int]) {
        pickTick += 1
        for (order, i) in indices.enumerated() {
            let final = slots[i].path.last?.name ?? ""
            let ticks = 10 + order * 4
            slots[i].spinning = true
            Task { @MainActor in
                for t in 0..<ticks {
                    guard i < slots.count else { return }
                    slots[i].shown = Deck.allLeaves.randomElement() ?? ""
                    try? await Task.sleep(for: .milliseconds(40 + Int(Double(t * t) * 0.55)))
                }
                guard i < slots.count else { return }
                withAnimation(.spring(response: 0.3, dampingFraction: 0.6)) {
                    slots[i].shown = final
                    slots[i].spinning = false
                }
            }
        }
    }
}

private struct SheetTarget: Identifiable { let index: Int; var id: Int { index } }

struct SquareView: View {
    let slot: Slot
    let count: Int

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack(alignment: .top) {
                Text(slot.caption)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundStyle(.secondary)
                    .lineLimit(count == 3 ? 1 : 2)
                Spacer(minLength: 0)
                if slot.lock != nil { Image(systemName: "lock.fill").font(.caption2).foregroundStyle(.secondary) }
            }
            Spacer(minLength: 0)
            Text(slot.shown)
                .font(count == 1 ? .largeTitle : count == 2 ? .title : .title2)
                .fontWeight(.semibold)
                .minimumScaleFactor(0.7)
                .contentTransition(.interpolate)
                .opacity(slot.spinning ? 0.55 : 1)
                .blur(radius: slot.spinning ? 0.8 : 0)
            Spacer(minLength: 0)
            HStack {
                Spacer()
                if slot.canGoDeeper && !slot.spinning {
                    Image(systemName: "chevron.down").font(.caption.weight(.bold)).foregroundStyle(.secondary)
                }
            }
        }
        .padding(count == 3 ? 20 : 22)
        .frame(maxWidth: .infinity, maxHeight: count == 3 ? .infinity : nil)
        .aspectRatio(count == 3 ? nil : 1, contentMode: .fit)
        .contentShape(.rect)
        .accessibilityElement(children: .combine)
        .accessibilityHint(slot.canGoDeeper ? "Tap to go deeper, hold to choose a category" : "Hold to choose a category")
    }
}

struct CategorySheet: View {
    let current: String?
    let choose: (String?) -> Void
    @State private var query = ""

    var body: some View {
        NavigationStack {
            List {
                Button { choose(nil) } label: {
                    HStack { Text("Any category"); Spacer(); if current == nil { Image(systemName: "checkmark") } }
                }
                ForEach(Deck.categories.map(\.name).sorted().filter { query.isEmpty || $0.localizedCaseInsensitiveContains(query) }, id: \.self) { name in
                    Button { choose(name) } label: {
                        HStack { Text(name); Spacer(); if current == name { Image(systemName: "checkmark") } }
                    }
                }
            }
            .searchable(text: $query, prompt: "Search \(Deck.categories.count) categories")
            .navigationTitle("Choose a category")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

/// The Three Word Brief colour wash that sits behind the glass. It drifts to a new spot on every pick.
struct Wash: View {
    let seed: Int
    @Environment(\.colorScheme) private var scheme

    var body: some View {
        GeometryReader { geo in
            let w = geo.size.width, h = geo.size.height
            ZStack {
                (scheme == .dark ? Color.twbNavy : Color(red: 1, green: 0.92, blue: 0.82))
                blob(.twbCoral, x: 0.15, y: 0.25, size: w * 1.15, w: w, h: h, k: 1)
                blob(.twbTeal, x: 0.85, y: 0.42, size: w * 1.15, w: w, h: h, k: 2)
                blob(.twbSun, x: 0.35, y: 0.82, size: w * 1.15, w: w, h: h, k: 3)
                blob(.twbCoral, x: 0.8, y: 0.05, size: w * 0.6, w: w, h: h, k: 4)
            }
            .opacity(scheme == .dark ? 0.62 : 0.9)
            .animation(.smooth(duration: 1.6), value: seed)
        }
    }

    private func blob(_ c: Color, x: Double, y: Double, size: Double, w: Double, h: Double, k: Int) -> some View {
        // Small deterministic offset per pick, so the wash moves without flashing.
        let dx = sin(Double(seed * 7 + k * 13)) * 0.12, dy = cos(Double(seed * 5 + k * 11)) * 0.1
        return Circle()
            .fill(RadialGradient(stops: [.init(color: c, location: 0.35), .init(color: c.opacity(0), location: 1)], center: .center, startRadius: 0, endRadius: size / 2))
            .frame(width: size, height: size)
            .position(x: (x + dx) * w, y: (y + dy) * h)
    }
}

#Preview { ContentView() }
