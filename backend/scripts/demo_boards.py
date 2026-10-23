"""
Demo boards: the made-up spaces for local runs, and more made-up entries for
each of them. Four boards (bread, ceramics, graphics, photography), each
gathering a few of demo_entries.py's topics plus the extra topics here;
every topic not claimed by a board stays on home.

Only used by seed_demo_entries.py. Nothing here is real.
"""

# slug: name, the board's brief, and which topics (by their first tag) it holds.
BOARDS = {
    "bread": {
        "name": "Bread",
        "description": "Loaves, starters, ferments and the long wait in between.",
        "topics": ["bread", "korean food", "flatbread"],
    },
    "ceramics": {
        "name": "Ceramics",
        "description": "Clay, glaze, kilns and other slow work with the hands.",
        "topics": ["ceramics", "woodworking", "glaze"],
    },
    "graphics": {
        "name": "Graphics",
        "description": "Pictures made with math and pictures made with type.",
        "topics": ["graphics", "typography", "generative art"],
    },
    "photography": {
        "name": "Photography",
        "description": "Mostly film, mostly walks, and the cities they happen in.",
        "topics": ["photography", "architecture", "night"],
    },
}

# More entries, one topic per board, in the same shape as demo_entries.TOPICS.
EXTRA_TOPICS = [
    {
        "tags": ["flatbread", "baking"],
        "extra_tags": ["pizza", "oven", "dough"],
        "colors": [(222, 160, 90), (150, 70, 40), (245, 225, 195), (70, 40, 25)],
        "items": [
            ("Neapolitan dough, 72 hours", "recipe", "series"),
            ("Steel versus stone", "note", "note"),
            ("Pita that actually puffed", "recipe", "upload"),
            ("The Elements of Pizza", "book", "book"),
            ("Wood-fired oven, rented for a day", "photo", "drive"),
            ("Stretching dough by hand", "video", "youtube"),
            ("Leopard spotting, finally", "photo", "instagram"),
            ("Thread: cold proofing", "post", "x"),
            ("Why high heat matters", "link", "web"),
            ("Naan on a cast iron pan", "recipe", "upload"),
        ],
        "why": [
            "Three days of waiting for ninety seconds in the oven.",
            "The bottom burned and the top was perfect. Next time, less time on the steel.",
            "Saved for the hydration table.",
            "Flat breads are where bread started. Simple and unforgiving.",
            "Better than the one I paid for last week.",
        ],
    },
    {
        "tags": ["glaze", "kiln"],
        "extra_tags": ["celadon", "firing", "test tiles"],
        "colors": [(120, 160, 150), (60, 90, 85), (230, 228, 215), (170, 120, 80)],
        "items": [
            ("Test tiles, cone 6", "photo", "series"),
            ("Celadon that came out green", "photo", "upload"),
            ("The Glaze Book", "book", "book"),
            ("Kiln log, spring", "note", "note"),
            ("Ash glaze from the fireplace", "photo", "drive"),
            ("Loading a kiln, slowly", "video", "youtube"),
            ("Crawling, and how to stop it", "link", "web"),
            ("Tea bowl, reduction fired", "photo", "instagram"),
            ("Thread: why glazes run", "post", "x"),
            ("Shino over tenmoku", "photo", "upload"),
        ],
        "why": [
            "You never quite know what the kiln will give back.",
            "Same recipe, two shelves, two different colors.",
            "Kept for the failures more than the successes.",
            "Glaze chemistry is cooking with rocks.",
            "The drips were an accident. I'm keeping them.",
        ],
    },
    {
        "tags": ["generative art", "plotter"],
        "extra_tags": ["noise", "algorithms", "pen"],
        "colors": [(30, 30, 40), (220, 90, 60), (240, 235, 225), (60, 110, 170)],
        "items": [
            ("Flow fields, first plot", "artwork", "upload"),
            ("Pen plotter, unboxed", "photo", "drive"),
            ("Generative Design", "book", "book"),
            ("Circle packing in an afternoon", "project", "github"),
            ("Truchet tiles, every variation", "artwork", "series"),
            ("Vera Molnár retrospective", "link", "web"),
            ("A thousand lines, one rule", "artwork", "instagram"),
            ("Thread: what counts as generative", "post", "x"),
            ("Live coding a plotter path", "video", "youtube"),
            ("Notes on letting the rule decide", "note", "note"),
        ],
        "why": [
            "Write the rule, then get out of the way.",
            "Took six hours to plot and four minutes to write.",
            "Molnár was doing this with punch cards in 1968.",
            "Random, but not too random.",
            "The pen skipped and it made it better.",
        ],
    },
    {
        "tags": ["night", "street"],
        "extra_tags": ["neon", "long exposure", "walks"],
        "colors": [(20, 25, 50), (230, 120, 60), (200, 60, 120), (240, 220, 160)],
        "items": [
            ("Night walk, roll 22", "photo", "series"),
            ("Neon in the rain", "photo", "upload"),
            ("Long exposure, bridge traffic", "photo", "drive"),
            ("Saul Leiter, colors", "link", "web"),
            ("Pushing film two stops", "video", "youtube"),
            ("Laundromat at 2am", "photo", "instagram"),
            ("Street Photography Now", "book", "book"),
            ("Thread: asking strangers", "post", "x"),
            ("Why I walk without headphones", "note", "note"),
            ("Corner store, closing time", "photo", "upload"),
        ],
        "why": [
            "The city is a different place after midnight.",
            "Shot at 1/15 with a steady wall.",
            "Leiter made the rain look like painting.",
            "Pushed two stops; grainier than I meant, and I like it.",
            "Nobody looks up at night.",
        ],
    },
]
