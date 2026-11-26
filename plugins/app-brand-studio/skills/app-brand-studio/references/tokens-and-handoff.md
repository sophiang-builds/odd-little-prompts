# Tokens and handoff

## Kit order

1. The winner, the reasoning, and what you would change for a different audience or platform.
2. Brand palette (expressive) and interface tokens, with the allowed pairings table and measured ratios.
3. Fonts: family, version, official source link, licence link, obligations, weights used.
4. Responsive type scale with line heights and fallback stacks.
5. Two representative screens rendered from `assets/screen.html` with the final tokens.
6. Do and don't (five to eight lines each at most, specific to this brand).
7. Copy-ready tokens for the platform.
8. Measured / proposed / test next.

## Allowed pairings table

| Text or element | On | Ratio | Use |
|---|---|---|---|
| `text` #1E1A17 | `bg` #FFFBF5 | 16.76:1 | All text |
| `on-action` #FFFFFF | `action` #C2410C | 5.17:1 | Button labels |
| `accent` #F97316 | `bg` | 2.71:1 | Decorative only: illustration, large shapes. Never text, icons or focus |

(Example values. Every ratio in a real kit comes from `contrast.py check` output.)

## Web: CSS custom properties

```css
/* Primitives */
:root {
  --orange-700: #C2410C;
  --ink-900: #1E1A17;
  --paper-50: #FFFBF5;
}

/* Semantic tokens, light */
:root {
  color-scheme: light;
  --color-bg: var(--paper-50);
  --color-surface: #FFFFFF;
  --color-text: var(--ink-900);
  --color-text-muted: #6A5F57;
  --color-border: #E7DDD3;           /* decorative divider */
  --color-border-strong: #8C7F75;    /* input outline, 3:1 */
  --color-action: var(--orange-700);
  --color-action-hover: #A93809;
  --color-action-pressed: #8F2F07;
  --color-on-action: #FFFFFF;
  --color-focus: var(--ink-900);
  --color-error: #B42318;
  --color-error-surface: #FEF3F2;
  --color-success: #067647;
  --color-warning-text: #93370D;     /* warning yellow fails as text; use this */

  --font-display: "Fraunces", Georgia, "Noto Serif HK", serif;
  --font-body: "Inter", "Noto Sans HK", "PingFang HK", "Microsoft JhengHei", system-ui, sans-serif;

  --text-display: clamp(2.125rem, 1.6rem + 2.2vw, 3.5rem);
  --text-h1: clamp(1.75rem, 1.45rem + 1.2vw, 2.5rem);
  --text-body: clamp(1rem, 0.97rem + 0.15vw, 1.0625rem);
  --leading-body: 1.55;

  --radius-control: 12px;
  --focus-ring: 0 0 0 3px var(--color-bg), 0 0 0 5px var(--color-focus);
}

/* Dark: only if in scope, and measured separately */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { /* dark semantic values */ }
}
:root[data-theme="dark"] { /* same dark values */ }

:lang(zh-HK), :lang(zh-Hant) { line-height: 1.75; letter-spacing: 0; }
```

Self-hosted font faces:

```css
@font-face {
  font-family: "Inter";
  src: url("/fonts/InterVariable.woff2") format("woff2");
  font-weight: 100 900;
  font-display: swap;
}
```

## iOS: SwiftUI

Put colours in the asset catalogue with Any and Dark appearances (so they also work in UIKit and widgets), and expose semantic names:

```swift
import SwiftUI

extension Color {
    static let brandBg = Color("Bg")
    static let brandText = Color("Text")
    static let brandAction = Color("Action")
    static let brandOnAction = Color("OnAction")
}

extension Font {
    static let brandDisplay = Font.custom("Fraunces-SemiBold", size: 34, relativeTo: .largeTitle)
    static let brandBody = Font.custom("Inter-Regular", size: 17, relativeTo: .body)
}
```

`relativeTo:` keeps Dynamic Type working. Test at the largest accessibility sizes.

## Android: Compose

```kotlin
val BrandLight = lightColorScheme(
    background = Color(0xFFFFFBF5),
    onBackground = Color(0xFF1E1A17),
    primary = Color(0xFFC2410C),
    onPrimary = Color(0xFFFFFFFF),
    error = Color(0xFFB42318),
)
val Inter = FontFamily(Font(R.font.inter_regular, FontWeight.Normal), Font(R.font.inter_semibold, FontWeight.SemiBold))
val BrandType = Typography(bodyLarge = TextStyle(fontFamily = Inter, fontSize = 17.sp, lineHeight = 26.sp))
```

## Cross-platform JSON (Design Tokens Community Group format)

```json
{
  "color": {
    "action": { "$type": "color", "$value": "#C2410C" },
    "on-action": { "$type": "color", "$value": "#FFFFFF" }
  },
  "font": {
    "body": { "$type": "fontFamily", "$value": ["Inter", "Noto Sans HK", "PingFang HK", "sans-serif"] }
  }
}
```

## Closing sections

Measured: list each check with its tool and result (pairing table from `contrast.py`, coverage lines from `font_check.py`, licence files read with URLs and dates).

Proposed: concept, palette mood, pairing rationale, layout, voice, anything not tested on real devices or real users.

Test next: smallest supported screen (320 px wide web, iPhone SE), largest text setting (iOS AX5, Android 200%), long strings and translations (German labels, long Chinese names, numbers with currency), keyboard and switch-control focus order and visibility, screen-reader labels, real photos under text, and colour-vision simulations of status colours.
