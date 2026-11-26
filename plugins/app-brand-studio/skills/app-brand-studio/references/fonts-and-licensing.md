# Fonts and licensing

Licence and coverage are checks. Do them on the actual files and the actual licence text, every time, and record what you read. Memory of "this font is OFL" is a lead, not evidence; licences, versions and hosting change.

## Verification procedure (per family)

1. Find the official source: the foundry's or designer's own repository or site, or the Google Fonts entry. For Google Fonts, the family's folder in `github.com/google/fonts` sits under `ofl/`, `apache/` or `ufl/`, which tells you the licence; the licence file is in that folder. Aggregator and download sites (font "free download" sites) are not official sources.
2. Read the licence file itself (OFL.txt, LICENSE, LICENSE.txt). Fetch it; do not summarise from the listing page alone.
3. Get the exact version from the file you will ship: `python3 scripts/font_check.py path/to/font.ttf` prints family, version (name ID 5), copyright, licence description and URL, the OS/2 embedding flag, weight class and variable axes. If the name table disagrees with the licence page, trust the licence file and flag the disagreement.
4. Check for a Reserved Font Name in the copyright line (OFL). If present and you subset, convert or otherwise modify the font, the modified version must not use that name unless the holder permits it. Serving the unmodified font, or using a hosted service that has permission, avoids this.
5. Check the `fsType` embedding flag. A "restricted" flag on a font claimed to be open is a red flag to investigate, not something to ignore.
6. Test coverage on the full font files for every script and string the app shows (below).
7. Record: family, version, source URL, licence name, licence file URL, RFN yes or no, obligations.

## Licence quick reference

| Licence | Commercial apps | Web self-hosting | Native embedding | Obligations |
|---|---|---|---|---|
| SIL Open Font License 1.1 | Yes | Yes | Yes | Keep the copyright notice and licence with each copy (a text file or readable metadata); do not sell the font on its own; modified versions are OFL too and must not use a Reserved Font Name |
| Apache 2.0 | Yes | Yes | Yes | Include the licence and any NOTICE file; mark modified files |
| Ubuntu Font Licence 1.0 | Yes | Yes | Yes | Read the file: conditions on modification and naming |
| "Free for personal use", "demo", "freeware" without a licence file | Fails | Fails | Fails | Reject |
| Apple system fonts (SF Pro, SF Compact, New York) | Only via the system on Apple platforms | No | Not bundled; not for Android or web hosting | Use the system font API, not files |
| Other OS system fonts (PingFang, Microsoft JhengHei, Segoe UI) | Only as installed system fonts | No | No | Name them in fallback stacks only |

Practical obligations to put in the kit: ship the licence file beside the font files in the repo and in the app bundle; add the fonts to the app's open-source acknowledgements screen; keep the copyright metadata intact when subsetting.

## Choosing and explaining a pairing

Default to one family when a single superfamily has both the voice and the reading comfort (a variable sans with optical sizes often does). Add a second family only when it contributes a distinct voice, usually display or headline, and give it a narrow job.

Compare the candidates at the sizes they will actually be used, not at specimen sizes:

- x-height relative to cap height: similar x-heights let display and body share a line without one looking shrunken.
- Width and spacing: narrow display faces save space in headlines but tire in body copy.
- Stroke contrast and terminals: high-contrast serifs read as editorial and warm at 32 px and become fragile below about 16 px.
- Apertures and letter distinction (Il1, O0, rn/m): matters for codes, prices and small labels.
- Figures: proportional for prose, tabular (`font-variant-numeric: tabular-nums`) for prices, timers, scores and tables. Check the font actually has `tnum`.
- Personality: say what the shapes do to the feeling ("the single-storey g and round dots soften it; the tight tracking keeps it adult").

Show in context: a heading, a paragraph, a form label, a button, a number-heavy line, and the Traditional Chinese equivalents if relevant.

## Type scale and spacing

Mobile base body is 16 to 17 px (iOS body is 17 pt by default). Use a modest ratio on small screens (about 1.2) and a wider one on large screens (about 1.25 to 1.333), with `clamp()` between them on web.

| Role | Mobile (px) | Desktop (px) | Line height | Notes |
|---|---|---|---|---|
| Display | 34 to 40 | 48 to 64 | 1.05 to 1.15 | Slight negative tracking for Latin only |
| H1 | 28 | 36 to 40 | 1.15 to 1.2 | |
| H2 | 22 | 28 | 1.2 to 1.25 | |
| Body | 16 to 17 | 17 to 18 | 1.45 to 1.6 Latin; 1.6 to 1.8 Chinese | |
| Label / button | 15 to 17 | 15 to 16 | 1.2 to 1.3 | Medium or semibold |
| Caption | 13 | 13 to 14 | 1.4 | Never below 12 px; Chinese no smaller than 14 px |

Fill in the real values for the chosen fonts; a face with a small x-height needs the larger end. Never apply negative letter-spacing to Chinese. Latin measure 45 to 75 characters; Chinese about 20 to 35 characters per line on mobile.

## Traditional Chinese

Decide the locale first. Hong Kong and Taiwan use different standard glyph forms for some characters, and written Cantonese uses characters many Taiwan-oriented fonts lack. For Hong Kong, prefer an HK region version (for example the HK variants in the Noto and Source Han families) and mark text `lang="zh-HK"` so the browser and font select HK forms.

Candidate families to verify (each with its own official repository and licence file; confirm both before recommending):

- Noto Sans HK / TC and Noto Serif HK / TC (Google, via Google Fonts and the notofonts CJK repository)
- Source Han Sans / Serif with HC (Hong Kong) and TC subsets (Adobe's source-han repositories)
- LXGW WenKai TC (a kai-style family, the designer's GitHub repository)
- jf open Huninn (rounded, justfont's GitHub repository)
- Iansui (handwritten kai-style, its GitHub repository)

Match Chinese to Latin by weight and colour on the page, not by name: put both in one paragraph and adjust the Chinese weight or size (often 1 px larger or one weight lighter) until the grey value is even.

Run coverage on the real files:

```bash
pip install fonttools brotli
python3 scripts/font_check.py NotoSansHK-Regular.otf --sample zh-hant --sample zh-hk --text-file app-strings-zh.txt
python3 scripts/font_check.py ./fonts/noto-sans-hk-slices --union --sample zh-hk   # sliced web fonts: test all slices together
```

Testing a single `unicode-range` slice reports most characters as missing; that is the slice, not the family. Use `--union` or the full font file.

Fallback stacks:

```css
--font-zh: "Noto Sans HK", "PingFang HK", "PingFang TC", "Microsoft JhengHei", "Heiti TC", "Noto Sans CJK TC", sans-serif;
--font-body: "Inter", "Noto Sans HK", "PingFang HK", "Microsoft JhengHei", system-ui, sans-serif;
```

Put the Latin family first so Latin characters use it and Chinese falls through to the CJK face.

## Delivery weight

Web: WOFF2 only, only the weights used (two or three), variable fonts when they replace three or more static files, `font-display: swap`, preload only the one Latin file used above the fold, and metric overrides (`size-adjust`, `ascent-override`) on the fallback to limit layout shift. CJK files are megabytes per weight: use a host that slices by `unicode-range`, subset to the app's real strings with `pyftsubset` (respecting any Reserved Font Name), or use the system Chinese font for body text and load a custom Chinese face only for headlines.

Native iOS: bundle `.ttf`/`.otf` (not WOFF2), list them under `UIAppFonts`, and scale with Dynamic Type: `Font.custom("Name", size: 17, relativeTo: .body)` in SwiftUI or `UIFontMetrics(forTextStyle:)` in UIKit. Consider PingFang (system) for Chinese body text to save several megabytes.

Native Android: put fonts in `res/font`, define a font family XML or Compose `FontFamily`, size in `sp`, and never cap the user's font scale. Android ships Noto Sans CJK, which can serve as the Chinese fallback.
