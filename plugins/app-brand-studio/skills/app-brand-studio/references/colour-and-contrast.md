# Colour and contrast

## Two palettes, not one

The expressive brand palette is for the logo, illustration, marketing, app icon and moments of delight. It can include colours that fail contrast, because it is rarely carrying text. The interface palette is a set of semantic tokens that every screen is built from, and every text or control pairing inside it is measured.

Build in two tiers. Primitives are named by what they are (`orange-600`, `ink-900`); semantic tokens are named by job (`--color-action`, `--color-text-muted`) and point at primitives. Screens only ever use semantic tokens, which is what makes dark mode and later rebrands cheap.

Minimum semantic set:

| Token | Job |
|---|---|
| `bg` | Page background |
| `surface` | Cards, sheets, inputs; `surface-raised` if elevation matters |
| `text` | Primary text on `bg` and `surface` |
| `text-muted` | Secondary text, captions, placeholders. Must still pass 4.5:1 |
| `border` | Dividers (decorative) and `border-strong` for input outlines (3:1 if it identifies the control) |
| `action` / `on-action` | Primary button fill and its label |
| `action-hover`, `action-pressed` | Usually a lightness shift of 0.04 to 0.08 in OKLCH; re-check the label on each |
| `action-disabled` / `on-action-disabled` | Exempt from contrast, but pair with a non-colour cue and keep the label legible |
| `link` | Underlined by default; colour alone is not enough |
| `focus` | Focus ring; 3:1 against every surface it can sit on |
| `success`, `warning`, `error` (+ `on-` and `-surface` variants) | Status, always with an icon or text, never colour alone |
| `accent` | Brand flourish; usually decorative only. Say so explicitly |

## What WCAG 2.2 AA actually requires

| Criterion | Level | Applies to | Requirement |
|---|---|---|---|
| 1.4.3 Contrast (Minimum) | AA | Text and images of text | 4.5:1; 3:1 for large text (at least 24 CSS px regular, or 18.66 px / 14 pt bold) |
| 1.4.11 Non-text Contrast | AA | Visual information needed to identify UI components and their states, and meaningful graphics | 3:1 against adjacent colours |
| 1.4.1 Use of Color | A | Any information | Colour cannot be the only means (errors, links in text, selection, required fields, chart series) |
| 2.4.7 Focus Visible | AA | Keyboard focus | A visible indicator must exist |
| 2.4.11 Focus Not Obscured (Minimum) | AA, new in 2.2 | Focused item | Not entirely hidden by sticky headers, sheets, banners |
| 2.4.13 Focus Appearance | AAA, new in 2.2 | Focus indicator | Area and 3:1 change of contrast. Aim for it, but do not claim AA needs it |
| 1.4.12 Text Spacing, 1.4.4 Resize Text | AA | Layout | Not a colour check, but the type system must survive them |

Notes that change real decisions:

- Inactive (disabled) controls are exempt from 1.4.3 and 1.4.11. That is a permission, not a goal: a disabled label at 1.5:1 is unreadable. Aim for roughly 3:1 on disabled labels and add a non-colour cue.
- Placeholder text is text. If it is visible, it needs 4.5:1. Better: use a persistent label and keep the placeholder optional.
- Large-text thresholds were written around Latin type. Treat Chinese text below 24 px as normal text and hold it to 4.5:1; CJK strokes are thin and dense at small sizes.
- Thin-stroke icons that carry meaning need 3:1; the same icon as decoration beside a text label does not.
- The ratio is not rounded up. 4.499:1 fails. `contrast.py` truncates for that reason.
- Text over photos or gradients: measure against the worst region under the text (lightest for light text), or put a scrim under it and measure the composited result.
- APCA is a useful second opinion for dark mode and thin type, but it is not the WCAG 2.2 conformance measure. Report WCAG ratios as the check.

## Measuring with the script

Composite every translucent layer before measuring; `contrast.py` does this. A pairing file mirrors the real UI:

```json
{
  "tokens": {
    "bg": "#FFFBF5", "surface": "#FFFFFF", "text": "#1E1A17", "text-muted": "#6A5F57",
    "action": "#C2410C", "on-action": "#FFFFFF", "focus": "#1E1A17",
    "error": "#B42318", "scrim": "#1E1A1799", "photo-light": "#F3E9DC"
  },
  "layers": { "hero-scrim": ["scrim", "photo-light"] },
  "pairs": [
    {"fg": "text", "bg": "bg", "role": "text", "where": "body"},
    {"fg": "text-muted", "bg": "surface", "role": "text", "where": "card caption"},
    {"fg": "on-action", "bg": "action", "role": "text", "where": "button label 17px"},
    {"fg": "action", "bg": "bg", "role": "ui", "where": "button boundary vs page"},
    {"fg": "focus", "bg": "bg", "role": "ui", "where": "focus ring"},
    {"fg": "error", "bg": "surface", "role": "text", "where": "inline error"},
    {"fg": "#FFFFFF", "bg": "hero-scrim", "role": "large-text", "where": "hero title on photo"}
  ]
}
```

```bash
python3 scripts/contrast.py check pairs.json
python3 scripts/contrast.py fix "#F97316" "#FFFFFF"            # move the foreground
python3 scripts/contrast.py fix "#FFFFFF" "#F97316" --keep fg  # move the background instead
```

Every pairing that appears on a shown screen goes in the file, including hover and pressed states, muted text on every surface it appears on, and the focus ring on every surface. Paste the resulting table into the kit.

Fixing keeps hue and changes OKLCH lightness, reducing chroma only if the colour would fall outside sRGB. If the fix makes the brand colour unrecognisable, keep the bright version as a decorative or large-surface colour and introduce a darker "action" sibling for text and controls. Say this explicitly; it is the most common honest answer.

## States

Hover and pressed: shift lightness, not hue. On light themes darken (pressed darker than hover); on dark themes lighten. Recheck the label on each.

Selection: combine a fill or colour change with a shape cue (check mark, weight change, indicator bar, outline).

Errors: error colour plus icon plus message text, and a thicker or differently styled border on the field. Never only a red border.

Links: underline in body text. If a design drops the underline, the link colour needs 3:1 against surrounding text and a non-colour cue on hover and focus, which is more work than an underline.

## Dark mode

Only when it is in scope. Build it as its own semantic token set from the same primitives:

- Background around L 0.15 to 0.22 in OKLCH rather than pure black, unless the brand is deliberately OLED-black.
- Elevation goes lighter, not darker; shadows barely read.
- Saturated light-mode accents vibrate on dark; reduce chroma and raise lightness.
- `on-action` may flip from white to near-black; check it.
- Run the full pairing file again with the dark tokens. Never infer dark results from light ones.
