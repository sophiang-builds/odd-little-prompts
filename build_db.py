"""Builds categories.json, the single source the app and picker.py read.

Each node is {"name": str, "children": [...]}. Depth is uneven on purpose:
a branch stops where going finer stops being useful.
Edit the TREE text below (two spaces per level) and rerun: python3 build_db.py
"""
import json, pathlib

TREE = """
Music
  Instrument
    Strings
      Guitar
      Ukulele
      Violin
      Cello
      Bass guitar
      Harp
    Keys
      Piano
      Synthesiser
      Organ
      Accordion
    Wind
      Flute
      Saxophone
      Trumpet
      Clarinet
      Harmonica
    Percussion
      Drum kit
      Cajón
      Hand drums
      Marimba
      Body percussion
    Voice
      Lead vocal
      Harmony singing
      Beatboxing
      Whistling
  Genre
    Pop
      Synth-pop
      City pop
      K-pop
      Cantopop
    Rock
      Indie rock
      Punk
      Shoegaze
      Classic rock
    Electronic
      House
      Drum and bass
      Lo-fi beats
      Ambient
    Jazz
      Bossa nova
      Swing
      Jazz fusion
      Bebop
    Folk and roots
      Singer-songwriter
      Bluegrass
      Celtic folk
      Country
    Hip-hop and R&B
      Boom bap
      Neo-soul
      Trap
      Classic R&B
    Classical
      Baroque
      Romantic era
      Minimalism
      Film score
  Activity
    Write a song
      About a smell
      Using only three chords
      As a lullaby
      From an object's point of view
    Cover a song
      In a different genre
      At half speed
      As a duet
      Unplugged
    Make a beat
      Using kitchen sounds
      Under 60 seconds
      At 90 BPM
      With one drum sound
    Listen deeply
      An album start to finish
      A genre you've never heard
      A song from the year you were born
      A friend's favourite track
  Mood
    Rainy afternoon
    Road trip
    Late night
    Sunday morning
    Party
    Heartbreak
Drawing
  Medium
    Dry
      Graphite pencil
      Charcoal
      Coloured pencil
      Oil pastel
      Ballpoint pen
    Wet
      Watercolour
      Gouache
      Ink and brush
      Acrylic
      Markers
    Digital
      Pixel art
      Vector shapes
      Digital painting
      One-layer only
  Subject
    People
      Self-portrait
      A friend from memory
      Hands
      Someone across the room
    Places
      The view from a window
      An imaginary city
      Your bedroom
      A street corner
    Things
      The contents of a bag
      Your shoes
      A houseplant
      Breakfast
    Creatures
      A pet
      A bird
      A made-up animal
      A sea creature
  Style
    Line only
    Silhouette
    Cartoon
    Botanical study
    Comic panel
    Isometric
  Constraint
    Non-dominant hand
    Under 5 minutes
    One continuous line
    Eyes closed
    Only three colours
    Upside down
Cooking
  Cuisine
    Asian
      Cantonese
      Japanese
      Thai
      Korean
      Vietnamese
      Indian
    European
      Italian
      French
      Spanish
      Greek
    Americas
      Mexican
      Peruvian
      Southern US
      Brazilian
    Middle East and Africa
      Lebanese
      Moroccan
      Ethiopian
      Turkish
  Dish type
    Noodles
    Dumplings
    Soup
    Salad
    Flatbread
    Dessert
    Breakfast
  Technique
    Steaming
    Roasting
    Fermenting
    Stir-frying
    Braising
    No cooking at all
  Challenge
    Five ingredients max
    Under 20 minutes
    Use what's in the fridge
    One pan only
    Make it for someone else
Writing
  Form
    Poem
      Haiku
      Sonnet
      Free verse
      Limerick
    Story
      Six-word story
      Flash fiction
      Fairy tale retold
      Letter-format story
    Non-fiction
      Diary entry
      Review of something tiny
      Letter to your past self
      How-to guide
  Prompt
    A door that wasn't there yesterday
    The last message on a phone
    A smell from childhood
    Two strangers stuck in a lift
    A city where it never stops raining
  Constraint
    No letter E
    Exactly 100 words
    Second person only
    All dialogue
    Start with the ending
Movement
  Activity
    Dance
      Hip-hop
      Salsa
      Freestyle
      Contemporary
    Stretch
      Yoga flow
      Desk stretches
      Mobility routine
    Outdoors
      Walk a new route
      Hike
      Cycle
      Swim
    Play
      Frisbee
      Badminton
      Skipping rope
      Hula hoop
  Duration
    5 minutes
    15 minutes
    30 minutes
    An hour
Photography
  Subject
    Shadows
    Reflections
    Strangers' hands
    Signs and lettering
    Something red
    Textures
  Rule
    Only from knee height
    Black and white
    Ten shots only
    Same spot, different times
    Macro, as close as you can
Making
  Paper
    Origami
    Collage
    Zine
    Paper cutting
  Fibre
    Knitting
    Embroidery
    Crochet
    Weaving
  Build
    Clay sculpture
    Cardboard model
    Lego build
    Upcycle something old
  Print
    Potato stamp
    Linocut
    Cyanotype
    Stencil
"""

def parse(text):
    root, stack = {"name": "root", "children": []}, []
    for line in text.splitlines():
        if not line.strip():
            continue
        depth = (len(line) - len(line.lstrip(" "))) // 2
        node = {"name": line.strip(), "children": []}
        stack = stack[:depth]
        (stack[-1] if stack else root)["children"].append(node)
        stack.append(node)
    return root["children"]

def strip(n):
    return {"name": n["name"], **({"children": [strip(c) for c in n["children"]]} if n["children"] else {})}

def parse_compact(path):
    """Category | Facet: a, b, c | Facet: d, e"""
    cats = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, *facets = [x.strip() for x in line.split("|")]
        kids = []
        for f in facets:
            fname, items = f.split(":", 1)
            # "hide": the facet label (Do, Make, Twist...) is a grouping, not something worth
            # showing as a pick on its own, so the explore app steps straight through it.
            kids.append({"name": fname.strip(), "hide": True, "children": [{"name": i.strip()[0].upper() + i.strip()[1:]} for i in items.split(",") if i.strip()]})
        cats.append({"name": name, "children": kids})
    return cats

def attach_exact(data, path):
    """Two line kinds:
    Category > Item: Name | note; Name     adds children under that item (note optional)
    Category > Item = note                 adds a note (translation, romanisation) to the item
    """
    missing = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        is_note = " = " in line and (":" not in line or line.index(" = ") < line.index(":"))
        head, rest = line.split(" = ", 1) if is_note else line.split(":", 1)
        cat, item = [x.strip() for x in head.split(">", 1)]
        kids = []
        for x in rest.split(";"):
            if not x.strip():
                continue
            name, _, note = x.partition("|")
            kid = {"name": name.strip()}
            if note.strip():
                kid["note"] = note.strip()
            kids.append(kid)
        found = 0
        def walk(n):
            nonlocal found
            for k in n.get("children", []):
                if k["name"].lower() == item.lower():
                    if is_note:
                        k["note"] = rest.strip(); found += 1
                    elif "children" not in k:
                        k["children"] = kids; found += 1
                walk(k)
        for c in data:
            if c["name"] == cat:
                walk(c)
        if not found:
            missing.append(f"{cat} > {item}")
    if missing:
        print(f"{path.name}: not found (check spelling):", "; ".join(missing))
    return data

def flag_twists(data):
    """Every item gets a third shown layer. Items with nothing more specific underneath
    are flagged "twist": the app then draws their next layer from twists.json."""
    def walk(n, shown):
        shown += 0 if n.get("hide") else 1
        if "children" in n:
            for k in n["children"]:
                walk(k, shown)
        elif shown < 3:
            n["twist"] = 1
    for c in data:
        walk(c, 0)
    return data

def parse_twists(path):
    groups = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        g, items = line.split(":", 1)
        kids = [{"name": x.strip(), **({"mash": 1} if g.strip() == "Mash-up" else {})} for x in items.split(",") if x.strip()]
        groups.append({"name": g.strip(), "hide": True, "children": kids})
    return groups

if __name__ == "__main__":
    data = [strip(n) for n in parse(TREE)]
    data += parse_compact(pathlib.Path(__file__).with_name("more_categories.txt"))
    data = attach_exact(data, pathlib.Path(__file__).with_name("exact_items.txt"))
    data = attach_exact(data, pathlib.Path(__file__).with_name("deeper_items.txt"))
    data = flag_twists(data)
    twists = parse_twists(pathlib.Path(__file__).with_name("twists.txt"))
    pathlib.Path(__file__).with_name("twists.json").write_text(json.dumps(twists, ensure_ascii=False, indent=1))
    names = [c["name"] for c in data]
    dupes = {n for n in names if names.count(n) > 1}
    assert not dupes, f"duplicate categories: {dupes}"
    out = pathlib.Path(__file__).with_name("categories.json")
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    def leaves(n): return 1 if "children" not in n else sum(leaves(c) for c in n["children"])
    print(f"{len(data)} categories, {sum(leaves(n) for n in data)} end points -> {out.name}")
