---
description: Check an existing palette or token file against WCAG 2.2 AA and propose the smallest fixes
argument-hint: <hex colours, a CSS/JSON token file path, or a description of where each colour is used>
---

Use the app-brand-studio skill's contrast tooling only (`scripts/contrast.py` and `references/colour-and-contrast.md`) on:

$ARGUMENTS

Work out every foreground and background pairing that actually appears (text, muted text, button labels, borders that identify controls, focus rings, status colours, anything with opacity), write them into a pairing file and run `contrast.py check`. For each failure, run `contrast.py fix` and give the nearest passing value with its ratio, and say when the honest fix is to keep the original as a decorative colour and add a darker sibling for text. Report the final table. Do not claim the app is compliant from colour checks alone.
