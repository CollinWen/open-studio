"""
Seed demo entries: wipes the LOCAL database and media folder, then fills
them with about 200 made-up entries so the site can be tried with a full
collection: four boards (bread, ceramics, graphics, photography; from
demo_boards.py) and the home board, each with its own topics (demo_entries.py).
Pictures are generated gradients and patterns. Within each topic, some
entries build on the one before ("builds on" chains). Two demo agents
(demo_agents.py) are signed on to the boards, with a status, a log of what
they planned, found and asked, and a few unlisted finds to publish; their
tokens are printed at the end, so a Claude session can be connected as one.

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
from app.features.agent_log import service as log_service  # noqa: E402
from app.features.agent_log.models import AgentLogLine  # noqa: E402
from app.features.agent_log.schemas import LogLineCreate  # noqa: E402
from app.features.agents import service as agents_service  # noqa: E402
from app.features.agents.schemas import AgentCreate  # noqa: E402
from app.features.boards import service as boards_service  # noqa: E402
from app.features.boards.schemas import BoardCreate  # noqa: E402
from app.features.entries import service as entries_service  # noqa: E402
from app.features.entries.schemas import EntryCreate, MediaItem  # noqa: E402
from app.features.entry_links import models as _link_models  # noqa: E402,F401  (so the wipe drops links too)
from app.features.entry_links import service as links_service  # noqa: E402
from app.features.tags import service as tags_service  # noqa: E402
from app.features.tags.schemas import TagNotes  # noqa: E402
from scripts import sample_images as draw  # noqa: E402
from scripts.demo_agents import AGENTS, FINDS, LOG  # noqa: E402
from scripts.demo_boards import BOARDS, EXTRA_TOPICS  # noqa: E402
from scripts.demo_entries import NOTE_PARAGRAPHS, SOURCE_NAMES, TOPICS, YOUTUBE_IDS  # noqa: E402

# Generated pictures are small; gradients scale up smoothly in the browser.
LONG_SIDE = 420
SHAPES = [(4, 3), (3, 4), (1, 1), (16, 9), (2, 3), (2, 1), (5, 4)]
OLDEST_DAYS_AGO = 2600  # about seven years
# Each topic's first tag is a key tag on its board; these four also get a description.
TAG_DESCRIPTIONS = {
    "bread": "Loaves, starters and the long wait in between.",
    "graphics": "Pictures made with math: renderers, shaders, noise.",
    "ceramics": "Clay, glaze and kilns. Slow work for fast weeks.",
    "photography": "Mostly film, mostly walks.",
}
ALL_TOPICS = TOPICS + EXTRA_TOPICS
# How often an entry builds on the one before it in its topic, and what the link says.
CHAIN_CHANCE = 0.45
CHAIN_NOTES = [
    "tried again with what this taught me",
    "picks up where this left off",
    "same question, a better answer",
    "the next step after this",
    "fixes what went wrong here",
]
OWNER = Viewer(role="owner")


def seed_demo() -> None:
    if settings.r2_enabled:
        sys.exit("R2 is configured, so this looks like production. Not wiping anything.")
    print(f"Wiping {settings.data_dir} ...")
    wipe_local_data()

    rng = random.Random(7)
    now = datetime.now(timezone.utc)
    picture_count = 0
    board_of_topic = {topic: slug for slug, board in BOARDS.items() for topic in board["topics"]}
    with Session(engine) as db:
        for slug, board in BOARDS.items():
            boards_service.create_board(
                db, BoardCreate(slug=slug, name=board["name"], description=board["description"])
            )
        made: list[list] = []
        for topic in ALL_TOPICS:
            made.append([])
            for title, kind, style in topic["items"]:
                media, picture_count = make_media(style, topic["colors"], picture_count, rng)
                entry = entries_service.create_entry(
                    db,
                    EntryCreate(
                        title=title,
                        kind="post" if style == "x" else kind,
                        description=write_description(style, topic["why"], rng),
                        media=media,
                        tags=topic["tags"] + rng.sample(topic["extra_tags"], rng.randint(0, 2)),
                        visibility=rng.choices(["public", "unlisted", "private"], [18, 1, 1])[0],
                        board=board_of_topic.get(topic["tags"][0], "home"),
                        occurred_at=now - timedelta(days=int(rng.random() ** 1.6 * OLDEST_DAYS_AGO)),
                        **describe_source(style, title, rng),
                    ),
                    OWNER,
                )
                made[-1].append(entry)
                print(f"added  {style:<9} {title}")
        for topic in ALL_TOPICS:
            name = topic["tags"][0]
            notes = TagNotes(description=TAG_DESCRIPTIONS.get(name, ""), importance=1)
            tags_service.save_tag_notes(db, name, notes)
        link_count = link_chains(db, made, rng)
        by_title = {entry.title: entry for topic_entries in made for entry in topic_entries}
        tokens = add_demo_agents(db, by_title, now)
    entry_count = sum(len(topic["items"]) for topic in ALL_TOPICS) + len(FINDS)
    print(f"Done: {entry_count} entries on {len(BOARDS) + 1} boards, {link_count} builds-on links, "
          f"{picture_count} pictures, {len(AGENTS)} agents.")
    for name, token in tokens.items():
        print(f"  agent {name}: {token}")


def link_chains(db: Session, made: list[list], rng: random.Random) -> int:
    """Within each topic, oldest first, some entries build on the one before."""
    count = 0
    for topic_entries in made:
        ordered = sorted(topic_entries, key=lambda entry: entry.occurred_at)
        for earlier, later in zip(ordered, ordered[1:]):
            if rng.random() < CHAIN_CHANCE:
                links_service.add_builds_on(db, OWNER, later, earlier, rng.choice(CHAIN_NOTES))
                count += 1
    return count


def add_demo_agents(db: Session, by_title: dict, now: datetime) -> dict[str, str]:
    """The demo agents, their unlisted finds and their log, spread back in time. Returns their tokens."""
    tokens = {}
    for name, agent in AGENTS.items():
        made, tokens[name] = agents_service.create_agent(
            db, AgentCreate(name=name, description=agent["description"], boards=agent["boards"])
        )
        made.status = agent["status"]
        made.last_seen_at = now - timedelta(hours=agent["seen_hours_ago"])
        db.add(made)
        db.commit()
    for name, board, title, kind, why, tags, builds_on, note in FINDS:
        viewer = Viewer(role="agent", agent_name=name)
        data = EntryCreate(title=title, kind=kind, description=why, tags=tags, board=board, occurred_at=now)
        find = entries_service.create_entry(db, data, viewer)
        links_service.add_builds_on(db, viewer, find, by_title[builds_on], note)
        by_title[title] = find
    for name, hours_ago, board, line_type, text, about in LOG:
        line = LogLineCreate(board=board, type=line_type, text=text, entry_id=by_title[about].id if about else None)
        written = log_service.add_line(db, Viewer(role="agent", agent_name=name), line)
        stored = db.get(AgentLogLine, written.id)
        stored.created_at = now - timedelta(hours=hours_ago)
        db.add(stored)
    db.commit()
    return tokens


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
