#!/usr/bin/env python3
"""WCAG 2.2 contrast checks for brand and interface colours.

Colours are #RGB, #RRGGBB or #RRGGBBAA. A translucent colour is composited
over whatever sits under it before measuring, which is how it is actually seen.

  contrast.py ratio FG BG [--under HEX]
      One pairing. If BG is translucent, --under is what BG sits on
      (default #FFFFFF).

  contrast.py check PAIRS.json [--json]
      Every pairing in a token set. Exit code 1 if any required pairing fails.

  contrast.py fix FG BG [--target 4.5] [--under HEX] [--keep fg|bg]
      Nearest colour (by OKLCH lightness, hue kept) that meets the target.

PAIRS.json:
  {
    "tokens": {"bg": "#FFFFFF", "text": "#1B1B1F", "scrim": "#00000066"},
    "layers": {"card-on-scrim": ["scrim", "bg"]},
    "pairs": [
      {"fg": "text", "bg": "bg", "role": "text", "where": "body copy"},
      {"fg": "#FFFFFF", "bg": "card-on-scrim", "role": "large-text"}
    ]
  }

"layers" defines a composited background from top to bottom: each layer is
painted over the next, the last must be opaque. Roles and their AA targets:
  text 4.5, large-text 3.0, ui 3.0 (controls, focus, borders that identify a
  control, meaningful icons and graphics), decorative (reported, no target),
  disabled (reported, WCAG exempts inactive controls).
"""
import argparse
import json
import math
import sys

TARGETS = {"text": 4.5, "large-text": 3.0, "ui": 3.0, "decorative": None, "disabled": None}
AAA = {"text": 7.0, "large-text": 4.5}


def parse(hex_str):
    s = hex_str.strip().lstrip("#")
    if len(s) in (3, 4):
        s = "".join(c * 2 for c in s)
    if len(s) not in (6, 8) or any(c not in "0123456789abcdefABCDEF" for c in s):
        raise ValueError(f"not a hex colour: {hex_str}")
    r, g, b = (int(s[i:i + 2], 16) / 255 for i in (0, 2, 4))
    a = int(s[6:8], 16) / 255 if len(s) == 8 else 1.0
    return (r, g, b, a)


def to_hex(rgb):
    return "#" + "".join(f"{round(max(0, min(1, c)) * 255):02X}" for c in rgb[:3])


def over(top, bottom):
    """Source-over composite in sRGB space, which is what browsers and UIKit do."""
    a = top[3]
    if bottom[3] < 1:
        raise ValueError("the bottom layer must be opaque")
    return tuple(top[i] * a + bottom[i] * (1 - a) for i in range(3)) + (1.0,)


def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    r, g, b = (lin(c) for c in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    """fg may be translucent; bg must be opaque."""
    fg = over(fg, bg) if fg[3] < 1 else fg
    l1, l2 = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


# OKLab / OKLCH, used only to search for a passing colour that keeps its hue.
def srgb_to_oklch(rgb):
    r, g, b = (lin(c) for c in rgb[:3])
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (math.copysign(abs(v) ** (1 / 3), v) for v in (l, m, s))
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    B = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(A, B), math.atan2(B, A)


def oklch_to_srgb(L, C, h):
    A, B = C * math.cos(h), C * math.sin(h)
    l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3
    m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3
    s = (L - 0.0894841775 * A - 1.2914855480 * B) ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    b = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

    def enc(c):
        return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055 if c > 0 else 12.92 * c
    return tuple(enc(c) for c in (r, g, b))


def in_gamut(rgb, eps=1e-6):
    return all(-eps <= c <= 1 + eps for c in rgb)


def at_lightness(L, C, h):
    """Colour at lightness L with the same hue, reducing chroma until it fits sRGB."""
    lo, hi = 0.0, C
    if in_gamut(oklch_to_srgb(L, C, h)):
        return oklch_to_srgb(L, C, h) + (1.0,)
    for _ in range(30):
        mid = (lo + hi) / 2
        if in_gamut(oklch_to_srgb(L, mid, h)):
            lo = mid
        else:
            hi = mid
    rgb = tuple(max(0, min(1, c)) for c in oklch_to_srgb(L, lo, h))
    return rgb + (1.0,)


def fix(moving, fixed, target, moving_is_fg):
    """Search lighter and darker; return the passing colour closest in lightness."""
    L0, C, h = srgb_to_oklch(moving)
    best = None
    for direction in (-1, 1):
        steps = [L0 + direction * i * 0.0025 for i in range(1, 401)]
        for L in steps:
            if not 0 <= L <= 1:
                break
            cand = at_lightness(L, C, h)
            # Quantise to 8-bit so the reported hex is the one that passes.
            cand = parse(to_hex(cand))
            r = ratio(cand, fixed) if moving_is_fg else ratio(fixed, cand)
            if r >= target:
                if best is None or abs(L - L0) < best[0]:
                    best = (abs(L - L0), cand, r)
                break
    return best


def resolve(name, tokens, layers):
    if name in layers:
        stack = [resolve(n, tokens, {}) for n in layers[name]]
        col = stack[-1]
        if col[3] < 1:
            raise ValueError(f"layer '{name}': the last layer must be opaque")
        for top in reversed(stack[:-1]):
            col = over(top, col)
        return col
    return parse(tokens.get(name, name))


def fmt(r):
    # Truncate rather than round so 4.499 never prints as a pass.
    return f"{math.floor(r * 100) / 100:.2f}:1"


def cmd_ratio(a):
    fg, bg = parse(a.fg), parse(a.bg)
    if bg[3] < 1:
        bg = over(bg, parse(a.under))
    r = ratio(fg, bg)
    print(f"{a.fg} on {a.bg}: {fmt(r)}")
    for role, t in TARGETS.items():
        if t:
            print(f"  {role:<11} AA {t}:1  {'pass' if r >= t else 'FAIL'}"
                  + (f"   AAA {AAA[role]}:1 {'pass' if r >= AAA[role] else 'fail'}" if role in AAA else ""))
    if fg[3] < 1:
        print(f"  (foreground composited to {to_hex(over(fg, bg))})")


def cmd_check(a):
    with open(a.file, encoding="utf-8") as f:
        spec = json.load(f)
    tokens, layers = spec.get("tokens", {}), spec.get("layers", {})
    rows, failed = [], False
    for p in spec["pairs"]:
        role = p.get("role", "text")
        if role not in TARGETS:
            raise ValueError(f"unknown role '{role}' (use one of {', '.join(TARGETS)})")
        bg = resolve(p["bg"], tokens, layers)
        fg = resolve(p["fg"], tokens, layers) if p["fg"] in layers else parse(tokens.get(p["fg"], p["fg"]))
        r = ratio(fg, bg)
        t = TARGETS[role]
        status = "n/a" if t is None else ("pass" if r >= t else "FAIL")
        failed |= status == "FAIL"
        rows.append({"fg": p["fg"], "bg": p["bg"], "role": role, "where": p.get("where", ""),
                     "fg_hex": to_hex(over(fg, bg) if fg[3] < 1 else fg), "bg_hex": to_hex(bg),
                     "ratio": math.floor(r * 100) / 100, "target": t, "status": status})
    if a.json:
        print(json.dumps(rows, indent=2))
    else:
        print("| Foreground | Background | Role | Where | Seen as | Ratio | AA target | Result |")
        print("|---|---|---|---|---|---|---|---|")
        for x in rows:
            print(f"| {x['fg']} | {x['bg']} | {x['role']} | {x['where']} | {x['fg_hex']} on {x['bg_hex']} "
                  f"| {x['ratio']:.2f}:1 | {str(x['target']) + ':1' if x['target'] else 'none'} | {x['status']} |")
    sys.exit(1 if failed else 0)


def cmd_fix(a):
    fg, bg = parse(a.fg), parse(a.bg)
    if bg[3] < 1:
        bg = over(bg, parse(a.under))
    if fg[3] < 1:
        fg = over(fg, bg)
    now = ratio(fg, bg)
    if now >= a.target:
        print(f"already passes: {fmt(now)} >= {a.target}:1")
        return
    moving_is_fg = a.keep == "bg"
    best = fix(fg if moving_is_fg else bg, bg if moving_is_fg else fg, a.target, moving_is_fg)
    if not best:
        print(f"no colour with this hue reaches {a.target}:1 against the fixed colour; change the other one")
        sys.exit(1)
    _, cand, r = best
    which = "foreground" if moving_is_fg else "background"
    print(f"was {fmt(now)}; {which} {to_hex(cand)} gives {fmt(r)} (target {a.target}:1, hue kept)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("ratio")
    p.add_argument("fg")
    p.add_argument("bg")
    p.add_argument("--under", default="#FFFFFF")
    p.set_defaults(func=cmd_ratio)
    p = sub.add_parser("check")
    p.add_argument("file")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_check)
    p = sub.add_parser("fix")
    p.add_argument("fg")
    p.add_argument("bg")
    p.add_argument("--target", type=float, default=4.5)
    p.add_argument("--under", default="#FFFFFF")
    p.add_argument("--keep", choices=["fg", "bg"], default="bg", help="which colour stays fixed (default bg)")
    p.set_defaults(func=cmd_fix)
    a = ap.parse_args()
    try:
        a.func(a)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
