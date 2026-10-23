"""
Seed demo entries: wipes the LOCAL database and media folder, then fills
them with about 130 made-up entries (from demo_entries.py) so the site can be
tried with a full collection. Pictures are generated gradients and patterns.

  .venv/Scripts/python scripts/seed_demo_entries.py             wipe and refill
  .venv/Scripts/python scripts/seed_demo_entries.py --offline   same, without OpenRouter

Entries go through the normal entry service. With OPENROUTER_API_KEY set they
get embeddings, so "Related" is by meaning (about one cheap embedding call per
entry). With --offline, Related falls back to shared tags.

Refuses to run when Cloudflare R2 is configured: that means production.
"""

import os
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

if "--offline" in sys.argv:
    os.environ["OPENROUTER_API_KEY"] = ""  # set before the app reads its settings

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, SQLModel  # noqa: E402

from app.auth.viewer import Viewer  # noqa: E402
from app.config import settings  # noqa: E402
from app.database import create_tables, engine  # noqa: E402
from app.features.boards import service as boards_service  # noqa: E402
from app.features.entries import service as entries_service  # noqa: E402
from app.features.entries.schemas import EntryCreate, MediaItem  # noqa: E402
from app.features.entry_links import models as _link_models  # noqa: E402,F401  (so the wipe drops links too)
from app.features.tags import service as tags_service  # noqa: E402
from app.features.tags.schemas import TagNotes  # noqa: E402
from scripts import sample_images as draw  # noqa: E402
from scripts.demo_entries import NOTE_PARAGRAPHS, SOURCE_NAMES, TOPICS, YOUTUBE_IDS  # noqa: E402

# Generated pictures are small; gradients scale up smoothly in the browser.
LONG_SIDE = 420
SHAPES = [(4, 3), (3, 4), (1, 1), (16, 9), (2, 3), (2, 1), (5, 4)]
OLDEST_DAYS_AGO = 2600  # about seven years
KEY_TAGS = {
    "bread": "Loaves, starters and the long wait in between.",
    "graphics": "Pictures made with math: renderers, shaders, noise.",
    "ceramics": "Clay, glaze and kilns. Slow work for fast weeks.",
    "photography": "Mostly film, mostly walks.",
}


def seed_demo() -> None:
    if settings.r2_enabled:
        sys.exit("R2 is configured, so this looks like production. Not wiping anything.")
    print(f"Wiping {settings.data_dir} ...")
    wipe_local_data()

    rng = random.Random(7)
    now = datetime.now(timezone.utc)
    picture_count = 0
    with Session(engine) as db:
        for topic in TOPICS:
            for title, kind, style in topic["items"]:
                media, picture_count = make_media(style, topic["colors"], picture_count, rng)
                entries_service.create_entry(
                    db,
                    EntryCreate(
                        title=title,
                        kind="post" if style == "x" else kind,
                        description=write_description(style, topic["why"], rng),
                        media=media,
                        tags=topic["tags"] + rng.sample(topic["extra_tags"], rng.randint(0, 2)),
                        visibility=rng.choices(["public", "unlisted", "private"], [18, 1, 1])[0],
                        occurred_at=now - timedelta(days=int(rng.random() ** 1.6 * OLDEST_DAYS_AGO)),
                        **describe_source(style, title, rng),
                    ),
                    Viewer(role="owner"),
                )
                print(f"added  {style:<9} {title}")
        for name, description in KEY_TAGS.items():
            tags_service.save_tag_notes(db, name, TagNotes(description=description, importance=1))
    print(f"Done: {sum(len(topic['items']) for topic in TOPICS)} entries, {picture_count} pictures.")


def wipe_local_data() -> None:
    SQLModel.metadata.drop_all(engine)
    create_tables()
    with Session(engine) as db:
        boards_service.ensure_home_board(db)
    settings.media_dir.mkdir(parents=True, exist_ok=True)
    for file in settings.media_dir.iterdir():
        if file.is_file():
            file.unlink()
    (settings.data_dir / "sample_entry_ids.json").unlink(missing_ok=True)  # left by the old sample script


def make_media(style: str, colors: list, picture_count: int, rng: random.Random) -> tuple[list[MediaItem], int]:
    """Pictures for one entry, in the shape each source would give them."""

    def picture(shape: tuple[int, int] | None = None) -> str:
        nonlocal picture_count
        across, down = shape or rng.choice(SHAPES)
        scale = LONG_SIDE / max(across, down)
        file_name = f"demo-{picture_count}.png"
        draw.write_png(str(settings.media_dir / file_name), round(across * scale), round(down * scale), pick_painter(colors, rng))
        picture_count += 1
        return f"/media/{file_name}"

    if style == "upload" or style == "drive":
        media = [MediaItem(type="image", url=picture())]
    elif style == "series":
        media = [MediaItem(type="image", url=picture(), caption=f"{i + 1}") for i in range(rng.randint(2, 5))]
    elif style == "instagram":
        media = [MediaItem(type="image", url=picture((1, 1)))]
    elif style == "github":
        url = picture((2, 1))
        media = [MediaItem(type="image", url=url, thumbnail_url=url)]
    elif style == "youtube":
        video = rng.choice(YOUTUBE_IDS)
        media = [MediaItem(type="embed", url=f"https://www.youtube-nocookie.com/embed/{video}", thumbnail_url=picture((16, 9)))]
    elif style == "web" and rng.random() < 0.5:
        media = [MediaItem(type="image", url=picture((40, 21)))]  # the usual link-preview shape
    else:
        media = []  # books, notes, X posts and some webpages are text only
    return media, picture_count


def pick_painter(colors: list, rng: random.Random) -> draw.Painter:
    """Mostly soft gradients, with an occasional bold pattern."""
    a, b, c, d = rng.sample(colors, 4)
    soft = [
        lambda: draw.gradient(a, b),
        lambda: draw.diagonal(a, c),
        lambda: draw.three_stop(a, b, d),
        lambda: draw.blob(a, b, rng.uniform(0.3, 0.7), rng.uniform(0.3, 0.7)),
        lambda: draw.horizon(a, b, c, d, rng.uniform(0.45, 0.7)),
        lambda: draw.sun(a, b, c, rng.uniform(0.3, 0.7), rng.uniform(0.4, 0.7), rng.uniform(0.08, 0.2)),
    ]
    bold = [
        lambda: draw.rings(a, c, rng.randint(4, 12)),
        lambda: draw.stripes(a, c, rng.randint(6, 20), rng.uniform(-0.8, 0.8)),
        lambda: draw.checker(a, c, rng.randint(3, 10)),
    ]
    return rng.choice(soft if rng.random() < 0.75 else bold)()


def write_description(style: str, why: list[str], rng: random.Random) -> str:
    if style == "note":
        return "\n\n".join([rng.choice(why)] + rng.sample(NOTE_PARAGRAPHS, rng.randint(2, 4)))
    if style == "x":
        return " ".join(rng.sample(why, 2)) + " (from a thread I keep rereading)"
    return " ".join(rng.sample(why, rng.randint(1, 3)))


def describe_source(style: str, title: str, rng: random.Random) -> dict:
    """source_name and source_url, as each link reader would fill them in."""
    slug = "".join(ch if ch.isalnum() else "-" for ch in title.lower()).strip("-")
    code = "".join(rng.choices("ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz0123456789_-", k=11))
    if style == "youtube":
        return {"source_name": rng.choice(SOURCE_NAMES["youtube"]), "source_url": f"https://www.youtube.com/watch?v={code}"}
    if style == "drive":
        return {"source_name": "Google Drive", "source_url": f"https://drive.google.com/file/d/{code}{code}/view"}
    if style == "github":
        return {"source_name": f"demo-studio/{slug}", "source_url": f"https://github.com/demo-studio/{slug}"}
    if style == "instagram":
        return {"source_name": "Instagram", "source_url": f"https://www.instagram.com/p/{code}/"}
    if style == "x":
        return {"source_name": "X", "source_url": f"https://x.com/demo_studio/status/{rng.randint(10**17, 10**18)}"}
    if style == "web":
        return {"source_name": rng.choice(SOURCE_NAMES["web"]), "source_url": f"https://example.com/{slug}"}
    if style == "book":
        return {"source_name": rng.choice(SOURCE_NAMES["book"]), "source_url": ""}
    return {"source_name": "", "source_url": ""}


if __name__ == "__main__":
    seed_demo()
