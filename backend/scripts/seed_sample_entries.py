"""
Seed sample entries: fills the site with a dozen made-up entries so you can
see how the grid looks before adding real work.

  Add them:     .venv/Scripts/python scripts/seed_sample_entries.py
  Remove them:  .venv/Scripts/python scripts/seed_sample_entries.py --remove

Entries go through the normal entry service, so if OPENROUTER_API_KEY is set
they also get embeddings (and "Related" works). The ids of what was added are
kept in data/sample_entry_ids.json so --remove deletes only the samples.
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session  # noqa: E402

from app.config import settings  # noqa: E402
from app.database import create_tables, engine  # noqa: E402
from app.features.entries import service as entries_service  # noqa: E402
from app.features.entries.schemas import EntryCreate, MediaItem  # noqa: E402
from scripts import sample_images as draw  # noqa: E402

IDS_FILE = settings.data_dir / "sample_entry_ids.json"

# (title, kind, days ago, tags, why it's here, source name, image painter + size or None)
SAMPLES = [
    ("Sourdough, bake #4", "recipe", 2, ["bread", "fermentation"],
     "Pushed hydration to 78%. The crumb finally opened up, but the shape spread. Next time: a tighter final shape and a colder proof.",
     "", (draw.blob((214, 170, 110), (120, 80, 40)), 600, 450)),
    ("This site", "project", 3, ["web", "design"],
     "A personal museum in progress. Built with React and Python. Tags come from a language model; related pieces are found with embeddings.",
     "", None),
    ("Life drawing, October 1", "sketch", 4, ["figure drawing"],
     "Two-minute poses. Trying to draw the weight first and the outline second.",
     "", (draw.rings((40, 40, 40), (245, 243, 238), 7), 450, 600)),
    ("Ways of Seeing", "book", 9, ["art", "design"],
     "Short, sharp, and still changes how I look at a museum wall. The chapter on the nude stuck with me most.",
     "John Berger", None),
    ("Kimchi, second batch", "recipe", 12, ["fermentation", "korean food"],
     "Less fish sauce, more gochugaru. Day five is the sweet spot.",
     "", (draw.gradient((200, 60, 40), (240, 200, 160)), 600, 600)),
    ("Embeddings, explained visually", "link", 15, ["machine learning"],
     "The clearest picture I've found of what an embedding actually is: a place in a space where nearby means similar.",
     "a blog post", None),
    ("Ink studies", "artwork", 20, ["ink", "abstract"],
     "Repetition until the hand stops thinking. Sumi ink on cheap paper.",
     "", (draw.stripes((25, 30, 80), (235, 232, 225), 16, 0.6), 500, 650)),
    ("Path tracer in a weekend", "project", 34, ["graphics", "rust"],
     "Followed Ray Tracing in One Weekend, then added a BVH. Watching the noise clear up is the best part.",
     "", (draw.blob((250, 240, 220), (30, 40, 60), 0.6, 0.4), 640, 400)),
    ("Salt Fat Acid Heat", "book", 41, ["cooking"],
     "Changed cooking from following recipes to adjusting by taste. The acid chapter especially.",
     "Samin Nosrat", None),
    ("A reel about Japanese joinery", "video", 50, ["woodworking", "design"],
     "No nails, no glue, just geometry. Saved because the craft is a kind of programming.",
     "Instagram", (draw.gradient((150, 110, 70), (60, 40, 25)), 450, 560)),
    ("Notes on keeping a sketchbook", "note", 63, ["art", "habits"],
     "The rule I keep coming back to: draw badly, often. This site is partly that rule applied to everything else.",
     "", None),
    ("Miso caramel", "recipe", 80, ["fermentation", "dessert"],
     "White miso folded into a dry caramel. Salty, deep, slightly funky. Great on apples.",
     "", (draw.rings((190, 140, 70), (250, 236, 210), 12), 520, 520)),
]


def add_samples() -> None:
    create_tables()
    media_dir = settings.media_dir
    media_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    created_ids: list[str] = []

    with Session(engine) as db:
        for index, (title, kind, days_ago, tags, why, source, image) in enumerate(SAMPLES):
            media = []
            if image:
                painter, width, height = image
                file_name = f"sample-{index}.png"
                draw.write_png(str(media_dir / file_name), width, height, painter)
                media.append(MediaItem(type="image", url=f"/media/{file_name}"))

            entry = entries_service.create_entry(
                db,
                EntryCreate(
                    title=title,
                    kind=kind,
                    description=why,
                    source_name=source,
                    media=media,
                    tags=tags,
                    visibility="public",
                    occurred_at=now - timedelta(days=days_ago),
                ),
            )
            created_ids.append(entry.id)
            print(f"added  {title}")

    existing = json.loads(IDS_FILE.read_text()) if IDS_FILE.exists() else []
    IDS_FILE.write_text(json.dumps(existing + created_ids))


def remove_samples() -> None:
    if not IDS_FILE.exists():
        print("No sample entries to remove.")
        return
    with Session(engine) as db:
        for entry_id in json.loads(IDS_FILE.read_text()):
            entry = entries_service.get_entry(db, entry_id, viewer_is_owner=True)
            if entry:
                entries_service.delete_entry(db, entry)
                print(f"removed  {entry.title}")
    for image in settings.media_dir.glob("sample-*.png"):
        image.unlink()
    IDS_FILE.unlink()


if __name__ == "__main__":
    remove_samples() if "--remove" in sys.argv else add_samples()
