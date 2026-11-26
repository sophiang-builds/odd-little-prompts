"""Random picks from categories.json, chosen by code, never by a language model.

Randomness comes from `secrets` (the operating system's cryptographic generator).
secrets.randbelow(n) returns each of 0..n-1 with exactly equal chance, so there is
no modulo bias. The phone app does the same thing with crypto.getRandomValues.

Each step down the tree picks one child with equal chance. That means every
branch at a level is equally likely, not every end point: Music > Mood (6 items)
gets picked as often as Music > Instrument (5 families), which is what "dive one
layer deeper" should feel like.

Usage:
  python3 picker.py Music Drawing          # one pick per category, one layer deep
  python3 picker.py Music --depth 3        # go three layers in
  python3 picker.py --any                  # surprise category
  python3 picker.py --test                 # check the picks are actually even
"""
import argparse, json, pathlib, secrets
from collections import Counter

DB = json.loads(pathlib.Path(__file__).with_name("categories.json").read_text())

def find(name):
    for c in DB:
        if c["name"].lower() == name.lower():
            return c
    raise SystemExit(f"No category '{name}'. Options: {', '.join(c['name'] for c in DB)}")

def pick(node, depth):
    path = [node["name"]]
    for _ in range(depth):
        kids = node.get("children")
        if not kids:
            break
        node = kids[secrets.randbelow(len(kids))]
        path.append(node["name"])
    return path

def fairness_test(trials=60000):
    """Chi-square test on a 6-way choice. A fair pick lands near 5 degrees of freedom."""
    kids = find("Music")["children"][3]["children"]  # Mood: 6 options
    counts = Counter(secrets.randbelow(len(kids)) for _ in range(trials))
    exp = trials / len(kids)
    chi = sum((counts[i] - exp) ** 2 / exp for i in range(len(kids)))
    for i, k in enumerate(kids):
        print(f"  {k['name']:<16}{counts[i]:>7}  ({counts[i] / trials:.2%})")
    verdict = "looks fair" if chi < 15.09 else "SUSPICIOUS"  # 99th percentile, 5 dof
    print(f"chi-square {chi:.2f} (fair is under 15.09): {verdict}")
    return chi < 15.09

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("categories", nargs="*")
    ap.add_argument("--depth", type=int, default=1)
    ap.add_argument("--any", action="store_true")
    ap.add_argument("--test", action="store_true")
    a = ap.parse_args()
    if a.test:
        raise SystemExit(0 if fairness_test() else 1)
    cats = [DB[secrets.randbelow(len(DB))]] if a.any or not a.categories else [find(n) for n in a.categories[:3]]
    for c in cats:
        print(" > ".join(pick(c, a.depth)))
