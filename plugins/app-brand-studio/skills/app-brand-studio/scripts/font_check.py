#!/usr/bin/env python3
"""Read a font's identity and licence fields and test glyph coverage.

  font_check.py FONT [FONT ...] [--text "..."] [--text-file F] [--sample NAME ...] [--union]

FONT can also be a directory (every font file inside is read). Use --union to
test coverage across all the files together, for example the unicode-range
slices a web font service ships for CJK. Without --union each file is tested
on its own, which is right for full font files.

FONT can be .ttf, .otf, .woff, .woff2 or a .ttc collection (every face is read).
Samples: latin, latin-ext, punct, numbers, zh-hant, zh-hk (Hong Kong
Cantonese and HKSCS characters), or all.

The name table is what the font file says about itself. It is evidence, not
proof: always read the licence file published at the official source too.

Needs:  pip install fonttools brotli   (brotli only for .woff2)
"""
import argparse
import os
import sys

try:
    from fontTools.ttLib import TTCollection, TTFont
except ImportError:
    sys.exit("fontTools is not installed: pip install fonttools brotli")

SAMPLES = {
    "latin": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "latin-ext": "ÀÁÂÄÅÆÇÈÉÊËÌÍÎÏÑÒÓÔÖØŒÙÚÛÜŸàáâäåæçèéêëìíîïñòóôöøœùúûüÿßĀāĒēĪīŌōŪūŁłŃńŚśŹźŻżČčŠšŽžĞğİıŞş",
    "punct": ".,:;!?'\"‘’“”–…·•()[]{}@#&*/\\%‰+−×÷=<>≤≥~^|_€£¥$¢©®™°",
    "numbers": "0123456789½¼¾",
    # Common Traditional Chinese, CJK punctuation and full-width forms.
    "zh-hant": ("的一是不了人我在有他這中大來上國個到說們為子和你地出道也時年得就那要下以生會自著去之過家學"
                "對可她裡後小麼心多天而能好都然沒日於起還發成事只作當想看文無開手十用主行方又如前所本見經頭"
                "面公同三已老從動兩長知民樣現分將外但身些與高意進把法此實回二理美點月明其種聲全工己話兒者向情"
                "部正名定女問力機給等幾很業最間新什打便位因重被走電四第門相次東政海口使教西再平真聽世氣信北少"
                "關並內加化由卻代軍產入先山五太水萬市眼體別處總才場師書比住員九笑性通目華報立馬命張活難神數件"
                "安表原車白應路期叫死常提感金何更反合放做系計或司利受光王果親界及今京務制解各任至清物台象記邊"
                "共風戰干接它許八特覺望直服毛林題建南度統色字請交愛讓認算論百吃義科怎元社術結六功指思非流每青"
                "管夫連遠資隊跟帶花快條院變聯言權往展該領傳近留紅治決周保達辦運武半候七必城父強步完革深區即求"
                "品士轉量空甚眾技輕程告江語英基派滿式李息寫呢識極令黃德收臉錢黨倒未持取設始版雙歷越史商千片容"
                "研像找友孩站廣改議形委早房音火際則首單據導影失拿網香似斯專石若兵弟誰校讀志飛觀爭究包組造落視"
                "濟喜離雖壞紙雜歡廳廠藝術鐵灣錄響證據權衛獨團屬園圖書館邊遞選擇顏體驗設計"
                "，。、；：？！「」『』（）《》〈〉…—　．＠＃％＆＊＋－＝０１２３４５６７８９"),
    # Characters used in written Cantonese and Hong Kong place names. Many
    # Taiwan-oriented Traditional Chinese fonts miss some of these.
    "zh-hk": "嘅咗喺啲冇嚟噉咁㗎囉嘢佢哋睇攞搵揾瞓嗰呢乜嘢咩唔係噃喎嘞啦咪啱嬲諗嚿餸鍾瞓郁嘈攰蝦餃燒賣邨埗鰂涌滙豐屯門荃灣葵涌粉嶺沙田西貢銅鑼灣旺角尖沙咀",
}


def name(font, nid):
    rec = font["name"].getDebugName(nid) if "name" in font else None
    return rec or ""


def cmap(font):
    best = font.getBestCmap() or {}
    return set(best)


def faces(path):
    if path.lower().endswith((".ttc", ".otc")):
        return [(f"{path}#{i}", f) for i, f in enumerate(TTCollection(path).fonts)]
    return [(path, TTFont(path, lazy=True))]


FONT_EXT = (".ttf", ".otf", ".woff", ".woff2", ".ttc", ".otc")


def expand(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            out += sorted(os.path.join(p, f) for f in os.listdir(p) if f.lower().endswith(FONT_EXT))
        else:
            out.append(p)
    return out


def report(key, text, have):
    chars = sorted({c for c in text if not c.isspace()})
    missing = [c for c in chars if ord(c) not in have]
    status = "all present" if not missing else f"MISSING {len(missing)}: {''.join(missing)}"
    print(f"  {key:<19} {len(chars) - len(missing)}/{len(chars)} {status}")
    return bool(missing)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fonts", nargs="+")
    ap.add_argument("--text", action="append", default=[], help="exact strings the app shows")
    ap.add_argument("--text-file", action="append", default=[], help="UTF-8 file of app strings")
    ap.add_argument("--sample", action="append", default=[], choices=list(SAMPLES) + ["all"])
    ap.add_argument("--union", action="store_true", help="test coverage across all files together")
    a = ap.parse_args()

    wanted = {}
    for s in (list(SAMPLES) if "all" in a.sample else a.sample):
        wanted[s] = SAMPLES[s]
    for i, t in enumerate(a.text):
        wanted[f"text{i + 1}"] = t
    for p in a.text_file:
        with open(p, encoding="utf-8") as f:
            wanted[p] = f.read()
    if not wanted:
        wanted = {"latin": SAMPLES["latin"], "punct": SAMPLES["punct"], "numbers": SAMPLES["numbers"]}

    any_missing = False
    paths = expand(a.fonts)
    if a.union:
        have, first = set(), None
        for path in paths:
            for _, font in faces(path):
                have |= cmap(font)
                first = first or font
        print(f"== union of {len(paths)} files ({name(first, 1)} {name(first, 5)})")
        for key, text in wanted.items():
            any_missing |= report(key, text, have)
        sys.exit(1 if any_missing else 0)
    for path in paths:
        for label, font in faces(path):
            print(f"== {label}")
            for nid, title in ((1, "Family"), (2, "Style"), (16, "Typographic family"), (5, "Version"),
                               (0, "Copyright"), (13, "Licence"), (14, "Licence URL"), (8, "Manufacturer"),
                               (11, "Vendor URL")):
                v = name(font, nid)
                if v:
                    v = " ".join(v.split())
                    print(f"  {title:<19} {v[:300]}{'...' if len(v) > 300 else ''}")
            os2 = font["OS/2"] if "OS/2" in font else None
            if os2 is not None:
                fs = os2.fsType
                if fs & 0x0002:
                    emb = "RESTRICTED: no embedding permitted by the font's own flag"
                elif fs & 0x0004:
                    emb = "preview and print only"
                elif fs & 0x0008:
                    emb = "editable"
                else:
                    emb = "installable (no restriction flag)"
                print(f"  {'Embedding flag':<19} fsType={fs} ({emb})")
                print(f"  {'Weight class':<19} {os2.usWeightClass}")
            if "fvar" in font:
                axes = ", ".join(f"{ax.axisTag} {ax.minValue:g}-{ax.maxValue:g}" for ax in font["fvar"].axes)
                print(f"  {'Variable axes':<19} {axes}")
            print(f"  {'Glyphs':<19} {font['maxp'].numGlyphs}")
            have = cmap(font)
            for key, text in wanted.items():
                any_missing |= report(key, text, have)
    sys.exit(1 if any_missing else 0)


if __name__ == "__main__":
    main()
