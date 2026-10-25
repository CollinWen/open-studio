"""
Database: opens the SQLite file and hands out sessions to the rest of the app.

Tables themselves are defined in each feature's models.py. This file only
creates them on startup and provides `get_db` for routes to use.
Changes to existing tables (new fields) live in database_migrations.py.
Connections are set up so reads don't wait on writes and writes queue briefly
rather than failing when several arrive at once (many agents writing).
"""

from collections.abc import Iterator

from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine

from app.config import settings
from app.database_migrations import apply_migrations, database_is_empty

# How long a write waits for another one to finish before giving up.
WRITE_WAIT_MILLISECONDS = 5000

settings.data_dir.mkdir(parents=True, exist_ok=True)
engine = create_engine(
    f"sqlite:///{settings.database_path}",
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def _configure_connection(connection, _record) -> None:
    """Let readers carry on during a write (WAL), and let writers queue instead of failing,
    so many agents can use the studio at once. Foreign keys on, so deleting an entry
    also deletes its links."""
    cursor = connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute(f"PRAGMA busy_timeout={WRITE_WAIT_MILLISECONDS}")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_tables() -> None:
    """Create any missing tables, then apply migrations to existing ones."""
    from app.features.agent_log import models as agent_log_models  # noqa: F401
    from app.features.agents import models as agent_models  # noqa: F401
    from app.features.boards import models as board_models  # noqa: F401
    from app.features.entries import models  # noqa: F401
    from app.features.entry_links import models as link_models  # noqa: F401
    from app.features.tags import models as tag_models  # noqa: F401

    fresh_database = database_is_empty(engine)
    SQLModel.metadata.create_all(engine)
    apply_migrations(engine, fresh_database)


def get_db() -> Iterator[Session]:
    """One database session per request."""
    with Session(engine) as session:
        yield session
