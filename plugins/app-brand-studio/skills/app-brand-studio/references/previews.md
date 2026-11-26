# Rendering previews

## Comparison of three directions

1. Copy `assets/compare.html` into the project or a scratch folder (keep the original as a template).
2. Replace the Google Fonts `<link>` with the families the three directions use. For a font not on Google Fonts, add `@font-face` rules pointing at local files.
3. Fill the `.dir-a`, `.dir-b` and `.dir-c` token blocks. Composition levers live in the tokens too (`--radius`, `--button-h`, `--pad`, display size, weight and tracking), so directions can differ in structure, not just colour. If a direction needs a genuinely different layout (centred hero, full-bleed colour block, underlined text buttons), add a scoped rule such as `.dir-b .btn.secondary { text-decoration: underline; }` rather than changing the shared template.
4. Edit the copy once in `<template id="screen">`. Use the app's real headline and button labels, not lorem ipsum. Keep the Chinese line if the app ships Traditional Chinese.
5. Edit the captions: name, concept, trade-off.
6. Render and look:

```bash
node scripts/render.js compare.html compare.png --width 1320 --scale 2
```

Read the PNG back and check it before showing it: fonts loaded (the script prints each family's status; `unloaded` for a family the page does not use is fine, but for one it uses means a fallback rendered), nothing clipped, the three really look different in type and composition, and the Chinese line sits comfortably with the Latin.

If fonts fail to load because the network blocks the font host, download the files from the official source, reference them with `@font-face`, and render again. If Playwright is not available at all, describe each frame as a spec (element, font, size, weight, colour token, spacing) and state that it was not rendered.

## Kit screens

`assets/screen.html` has one `.brand` token block and two templates. Paste the final tokens (from the same values as `tokens.css`) so the rendered screens and the handoff never drift apart. Make screen 2 stress something screen 1 does not: an error or empty state, number-heavy content, or the Traditional Chinese version.

## Sharing

A rendered PNG goes to the person directly. If they want to pass the comparison or kit around, offer to publish it as a page.
