{
  // Unbiased integer in [0, n) from the secure generator, by rejection sampling.
  const buf = new Uint32Array(1);
  const randBelow = n => { const lim = Math.floor(2 ** 32 / n) * n; let x; do { crypto.getRandomValues(buf); x = buf[0]; } while (x >= lim); return x % n; };
  const esc = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = id => document.getElementById(id);
  const ICON_LOCK = '<svg viewBox="0 0 24 24" style="height:1em;flex:none"><path d="M7 10V7a5 5 0 0 1 10 0v3h1a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-9a1 1 0 0 1 1-1zm2 0h6V7a3 3 0 0 0-6 0z" fill="currentColor"/></svg>';

  let DB = [], LEAVES = [], MIDS = [], TWISTS = [], REFS = [], BAG = [];
  // each slot: { path: [node,...] | null, lock: categoryName | null }. Paths can hold hidden
  // facet nodes (Do, Make, Twist...) that are stepped through but never shown as the pick.
  let slots = [{ path: null, lock: null }];
  try { const n = +localStorage.getItem("olp-n"); if (n >= 1 && n <= 3) slots = Array.from({ length: n }, () => ({ path: null, lock: null })); } catch (e) {}

  const byName = n => DB.find(c => c.name === n);
  const visible = p => p.filter(n => !n.hide);
  // An item with nothing more specific underneath draws its next layer from the twist deck.
  const kidsOf = n => n.children || (n.twist ? TWISTS : null);
  const canDown = s => !!(s.path && kidsOf(s.path[s.path.length - 1]));
  const canUp = s => !!(s.path && s.path.length > 1);

  // One shown layer down: pick a child at random; if it is a hidden facet, keep going.
  const down = path => {
    const p = path.slice();
    let node = p[p.length - 1], kids = kidsOf(node);
    if (!kids) return null;
    do {
      node = kids[randBelow(kids.length)];
      if (node.mash) node = mashUp(p[0].name);
      p.push(node); kids = node.children;
    } while (node.hide && kids);
    return p;
  };
  // One shown layer up: drop the last node and any hidden facets above it.
  const up = path => {
    if (path.length < 2) return null;
    const p = path.slice(0, -1);
    while (p.length > 1 && p[p.length - 1].hide) p.pop();
    return p;
  };

  // Different categories across squares in one pick (sampling without replacement).
  // Mash-up twist: pair the card with a random item from a different category.
  const mashUp = cat => {
    let r; do { r = REFS[randBelow(REFS.length)]; } while (r.cat === cat);
    return { name: `Mash it up with: ${r.name}`, note: `From ${r.cat}` };
  };

  // Shuffle bag: every category comes up once, in random order, before any repeats.
  const saveBag = () => { try { localStorage.setItem("olp-bag", JSON.stringify(BAG)); } catch (e) {} };
  const refill = () => {
    BAG = DB.map(c => c.name);
    for (let i = BAG.length - 1; i > 0; i--) { const j = randBelow(i + 1); [BAG[i], BAG[j]] = [BAG[j], BAG[i]]; }
  };
  const drawCat = taken => {
    for (let round = 0; round < 2; round++) {
      const k = BAG.findIndex(n => !taken.has(n));
      if (k >= 0) { const name = BAG.splice(k, 1)[0]; saveBag(); return byName(name); }
      refill();
    }
    const pool = DB.filter(c => !taken.has(c.name));
    return pool[randBelow(pool.length)];
  };

  const chooseCategories = () => {
    const taken = new Set(slots.filter(s => s.lock).map(s => s.lock));
    return slots.map(s => {
      if (s.lock) return byName(s.lock);
      const c = drawCat(taken);
      taken.add(c.name);
      return c;
    });
  };

  const squareHTML = (s, i) => {
    if (!s.path) return `<button class="glass press sq" data-i="${i}" aria-label="Empty square ${i + 1}"><div class="cap">${s.lock ? `<span>${esc(s.lock)}</span>${ICON_LOCK}` : ""}</div><div class="big"></div></button>`;
    const p = s.path, last = p[p.length - 1];
    const trail = p.length === 1 ? "Category" : p.slice(0, -1).filter(n => !TWISTS.includes(n)).map(n => n.name).join(" · ");
    const layer = visible(p).length;
    const dots = Array.from({ length: Math.max(layer, 3) }, (_, k) => `<i class="${k < layer ? "on" : ""}"></i>`).join("");
    return `<button class="glass press sq" data-i="${i}" aria-label="${esc(trail + ": " + last.name)}"><div class="cap"><span>${esc(trail)}</span>${s.lock ? ICON_LOCK : ""}</div><div class="big"><span>${esc(last.name)}</span>${last.note ? `<small class="note">${esc(last.note)}</small>` : ""}</div><div class="dots" aria-hidden="true">${dots}</div></button>`;
  };

  const render = () => {
    const el = $("slots");
    el.dataset.n = slots.length; el.style.setProperty("--n", slots.length);
    el.innerHTML = slots.map((s, i) => `<div class="cell">${squareHTML(s, i)}</div>`).join("");
    document.querySelectorAll("#count button").forEach(b => b.setAttribute("aria-pressed", +b.dataset.n === slots.length));
    $("up").disabled = !slots.some(canUp);
    $("down").disabled = !slots.some(canDown);
  };

  const shiftWash = () => document.querySelectorAll("#wash i").forEach(i => {
    i.style.transform = `translate(${randBelow(41) - 20}%, ${randBelow(41) - 20}%) scale(${0.85 + randBelow(40) / 100})`;
  });

  const nudge = (i, cls) => { const el = document.querySelector(`.sq[data-i="${i}"]`); if (!el) return; el.classList.remove(cls); void el.offsetWidth; el.classList.add(cls); };

  // Slot-reel reveal: results are decided first, the flicker is only decoration.
  const spin = indices => {
    shiftWash();
    render();
    if (calm) return;
    indices.forEach((i, order) => {
      const big = document.querySelector(`.sq[data-i="${i}"] .big`);
      if (!big) return;
      const final = big.innerHTML, depth = slots[i].path.length;
      const pool = depth === 1 ? DB.map(c => c.name) : canDown(slots[i]) ? MIDS : LEAVES;
      const ticks = 10 + order * 4;
      let t = 0;
      const step = () => {
        big.classList.remove("tick"); void big.offsetWidth; big.classList.add("tick");
        if (t++ < ticks) { big.textContent = pool[randBelow(pool.length)]; setTimeout(step, 40 + t * t * 0.55); }
        else big.innerHTML = final;
      };
      step();
    });
  };

  // Pick for me: fresh categories, back at the top layer.
  const pickAll = () => {
    const cats = chooseCategories();
    slots.forEach((s, i) => s.path = [cats[i]]);
    spin(slots.map((_, i) => i));
  };

  const pickOne = i => {
    const others = new Set(slots.filter((s, j) => j !== i && s.path).map(s => s.path[0].name));
    const pool = slots[i].lock ? [byName(slots[i].lock)] : DB.filter(c => !others.has(c.name));
    slots[i].path = [pool[randBelow(pool.length)]];
    spin([i]);
  };

  // Down: every square goes one layer deeper at random. Up: every square steps back, no re-roll.
  const goDown = only => {
    const moved = [];
    slots.forEach((s, i) => {
      if (only !== undefined && i !== only) return;
      const p = s.path && down(s.path);
      if (p) { s.path = p; moved.push(i); } else if (s.path) setTimeout(() => nudge(i, "nope"), 0);
    });
    if (moved.length) spin(moved);
  };
  const goUp = () => {
    const moved = [];
    slots.forEach((s, i) => { const p = s.path && up(s.path); if (p) { s.path = p; moved.push(i); } });
    render();
    moved.forEach(i => { const b = document.querySelector(`.sq[data-i="${i}"] .big`); if (b && !calm) b.classList.add("tick"); });
  };

  const setCount = n => {
    while (slots.length < n) slots.push({ path: null, lock: null });
    slots.length = n;
    try { localStorage.setItem("olp-n", n); } catch (e) {}
    render();
  };

  // Category sheet (long-press a square)
  const openSheet = i => {
    const host = $("sheetHost"), cur = slots[i].lock;
    const names = DB.map(c => c.name).sort((a, b) => a.localeCompare(b));
    const rows = q => [`<button data-c="">Any category${!cur ? " ✓" : ""}</button>`]
      .concat(names.filter(n => n.toLowerCase().includes(q)).map(n => `<button data-c="${esc(n)}" aria-current="${n === cur}"><span>${esc(n)}</span>${n === cur ? "<span>✓</span>" : ""}</button>`)).join("");
    host.innerHTML = `<div class="scrim" id="scrim"></div><div class="glass sheet" role="dialog" aria-label="Choose a category">
      <div class="grab"></div><div class="shead"><b>Square ${i + 1}</b><button class="done" id="done">Done</button></div>
      <input class="search" id="q" type="search" placeholder="Search ${names.length} categories" autocomplete="off"><div class="list" id="list">${rows("")}</div></div>`;
    const close = () => host.innerHTML = "";
    $("scrim").onclick = close; $("done").onclick = close;
    $("q").oninput = e => $("list").innerHTML = rows(e.target.value.trim().toLowerCase());
    $("list").onclick = e => { const b = e.target.closest("button"); if (!b) return; slots[i].lock = b.dataset.c || null; close(); pickOne(i); };
  };

  // Card gestures: long-press (or right-click) a card to choose its category
  let pressTimer = null;
  const sq = e => e.target.closest(".sq");
  $("slots").addEventListener("pointerdown", e => { const el = sq(e); if (!el) return; pressTimer = setTimeout(() => openSheet(+el.dataset.i), 520); });
  ["pointerup", "pointerleave", "pointercancel"].forEach(t => $("slots").addEventListener(t, () => clearTimeout(pressTimer)));
  $("slots").addEventListener("contextmenu", e => { const el = sq(e); if (!el) return; e.preventDefault(); clearTimeout(pressTimer); openSheet(+el.dataset.i); });
  $("pick").addEventListener("click", pickAll);
  $("down").addEventListener("click", () => goDown());
  $("up").addEventListener("click", goUp);
  $("count").addEventListener("click", e => { const b = e.target.closest("button"); if (b) setCount(+b.dataset.n); });

  // Fit the iPhone 15 frame to the window on larger screens
  const fit = () => document.documentElement.style.setProperty("--s", Math.min(1, (innerHeight - 32) / 876, (innerWidth - 24) / 417).toFixed(3));
  addEventListener("resize", fit); fit();

  render();
  Promise.all(["categories.json", "twists.json"].map(u => fetch(u).then(r => r.json()))).then(([d, t]) => {
    DB = d; TWISTS = t;
    const walk = (n, cat) => { if (!n.children) { LEAVES.push(n.name); REFS.push({ name: n.name, cat }); return; } if (!n.hide) MIDS.push(n.name); n.children.forEach(k => walk(k, cat)); };
    DB.forEach(c => c.children.forEach(k => walk(k, c.name)));
    try { BAG = JSON.parse(localStorage.getItem("olp-bag") || "[]").filter(n => byName(n)); } catch (e) { BAG = []; }
    $("pick").disabled = false;
  }).catch(() => { $("slots").insertAdjacentHTML("afterend", `<p style="color:var(--muted);text-align:center">Couldn't load the category list</p>`); });
}
