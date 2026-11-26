# App Brand Studio

A Claude Code plugin that acts as brand designer, typographer and UI art director for an app. Describe the app and the feeling you want; it turns the words into design decisions, shows three directions on the same rendered mobile screen, and hands over a buildable kit.

Taste is a recommendation. Contrast, glyph coverage and licensing are checks, done with the bundled scripts on real colours and real font files.

## Install

From this repository's marketplace:

```
/plugin marketplace add sophiang1227/three-word-brief
/plugin install app-brand-studio@three-word-brief-plugins
```

Or load it locally while developing:

```
claude --plugin-dir ./plugins/app-brand-studio
```

## Use

The skill triggers on its own when you ask for a brand, palette, font pairing or tokens for an app. Or call it directly:

| Command | What it does |
|---|---|
| `/app-brand-studio:brand <brief>` | Full pass: brief translated into design levers, three directions on one screen, winner, tokens, fonts with licence checks, type scale, two screens, do and don't, measured vs proposed |
| `/app-brand-studio:brand-quick <brief>` | One direction and one credible alternative |
| `/app-brand-studio:contrast <colours or token file>` | WCAG 2.2 AA check of an existing palette with nearest passing fixes |

## What is inside

```
skills/app-brand-studio/
  SKILL.md                      the five-step workflow
  references/
    colour-and-contrast.md      token set, WCAG 2.2 criteria that matter, states, dark mode
    fonts-and-licensing.md      licence verification, pairing method, type scale, Traditional Chinese
    tokens-and-handoff.md       kit order, CSS / SwiftUI / Compose / DTCG JSON templates
    previews.md                 rendering the comparison and kit screens
  scripts/
    contrast.py                 ratios with alpha compositing, pairing-file check, hue-preserving fix
    font_check.py               family, version, licence fields, embedding flag, glyph coverage (incl. HK Cantonese)
    render.js                   Playwright screenshot with font-load report
  assets/
    compare.html                three phones, identical copy, one token block per direction
    screen.html                 two kit screens from one token block
```

`contrast.py` uses only the Python standard library. `font_check.py` needs `pip install fonttools brotli`. `render.js` needs Playwright with Chromium.

## Quick checks without Claude

```
python3 skills/app-brand-studio/scripts/contrast.py ratio "#767676" "#FFFFFF"
python3 skills/app-brand-studio/scripts/contrast.py fix "#F97316" "#FFFFFF"
python3 skills/app-brand-studio/scripts/font_check.py MyFont.otf --sample zh-hant --sample zh-hk
```

## Limits

Colour checks do not make an app accessible on their own; focus order, labels, text scaling and real content still need testing. Licence summaries in the references are a starting point; the skill reads the actual licence file for each font every time. No paid assets or deployment unless you ask.
