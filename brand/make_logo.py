"""Builds the Odd Little Prompts mark, favicon and horizontal logo.

The mark is three tilted cards with a sparkle on the front one. The wordmark is Inter ExtraBold
converted to outlines, with a coloured underline under each word.
Usage: python3 make_logo.py path/to/Inter-ExtraBold.ttf   (needs: pip install fonttools)
"""
import sys, pathlib
TILE, PINK, BUTTER, LILAC, CREAM = "#2B1F3D", "#FF8FB1", "#FFD45C", "#9B7BFF", "#FFF6E9"
INK_LIGHT, INK_DARK, LAST_LIGHT, LAST_DARK = "#2B1F3D", "#FFF6E9", "#7E5CF0", "#B9A2FF"
HERE = pathlib.Path(__file__).parent

def cards(tile_cls=""):
    cls = f' class="{tile_cls}"' if tile_cls else ""
    return f'''<rect{cls} width="64" height="64" rx="14" fill="{TILE}"/>
  <g stroke="{TILE}" stroke-width="3" stroke-linejoin="round">
    <rect x="-13" y="-17" width="26" height="34" rx="6" fill="{PINK}" transform="translate(23 35) rotate(-16)"/>
    <rect x="-13" y="-17" width="26" height="34" rx="6" fill="{BUTTER}" transform="translate(32 31) rotate(0)"/>
    <rect x="-13" y="-17" width="26" height="34" rx="6" fill="{LILAC}" transform="translate(41 35) rotate(16)"/>
  </g>
  <path d="M0,-11 C1.6,-3 3,-1.6 11,0 C3,1.6 1.6,3 0,11 C-1.6,3 -3,1.6 -11,0 C-3,-1.6 -1.6,-3 0,-11Z" fill="{CREAM}" transform="translate(41 35) rotate(16) scale(0.78)"/>'''

def favicon(square=False):
    body = cards()
    if square:
        body = body.replace('rx="14" fill="' + TILE + '"', 'fill="' + TILE + '"', 1)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">\n  <title>Odd Little Prompts</title>\n  {body}\n</svg>\n'

def logo(font_path, variant):
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    font = TTFont(font_path); gs = font.getGlyphSet(); cmap = font.getBestCmap(); hmtx = font["hmtx"]
    size, base, x = 44, 60, 96; s = size / font["head"].unitsPerEm
    ink = {"light": INK_LIGHT, "dark": INK_DARK, "inline": "currentColor"}[variant]
    last = {"light": LAST_LIGHT, "dark": LAST_DARK, "inline": "var(--lastInk)"}[variant]
    words, paths, bars = ["Odd", "Little", "Prompts"], [], []
    for i, (word, bar) in enumerate(zip(words, [PINK, BUTTER, LILAC])):
        start = x; d = []
        for ch in word:
            pen = SVGPathPen(gs); gn = cmap[ord(ch)]; gs[gn].draw(pen)
            d.append(f'<path d="{pen.getCommands()}" transform="translate({x:.1f} {base}) scale({s:.4f} {-s:.4f})"/>')
            x += hmtx[gn][0] * s - 0.8
        paths.append(f'<g fill="{last if i == 2 else ink}">{"".join(d)}</g>')
        bars.append(f'<rect x="{start + 2:.1f}" y="76" width="{x - start - 4:.1f}" height="6" rx="3" fill="{bar}"/>')
        x += 16
    w = x - 16 + 14
    head = '<svg xmlns="http://www.w3.org/2000/svg"' if variant != "inline" else '<svg aria-hidden="true"'
    size_attr = f' width="{w:.0f}" height="92"' if variant != "inline" else ""
    title = "<title>Odd Little Prompts</title>" if variant != "inline" else ""
    return (f'{head} viewBox="0 0 {w:.0f} 92"{size_attr}>{title}<g transform="translate(6 12)">'
            + cards("tile") + "</g>" + "".join(bars) + "".join(paths) + "</svg>\n")

if __name__ == "__main__":
    (HERE / "favicon.svg").write_text(favicon())
    (HERE / "app-icon-square.svg").write_text(favicon(square=True))
    if len(sys.argv) > 1:
        (HERE / "logo-horizontal.svg").write_text(logo(sys.argv[1], "light"))
        (HERE / "logo-horizontal-dark.svg").write_text(logo(sys.argv[1], "dark"))
        (HERE / "logo-inline.svg").write_text(logo(sys.argv[1], "inline"))
    print("written")
