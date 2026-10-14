"""
Database: opens the SQLite file and hands out sessions to the rest of the app.

Tables themselves are defined in each feature's models.py. This file only
creates them on startup and provides `get_db` for routes to use.
Changes to existing tables (new fields) live in database_migrations.py.
"""

from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings
from app.database_migrations import apply_migrations, database_is_empty

settings.data_dir.mkdir(parents=True, exist_ok=True)
engine = create_engine(
    f"sqlite:///{settings.database_path}",
    connect_args={"check_same_thread": False},
)


def create_tables() -> None:
    """Create any missing tables, then apply migrations to existing ones."""
    from app.features.entries import models  # noqa: F401
    from app.features.tags import models as tag_models  # noqa: F401

    fresh_database = database_is_empty(engine)
    SQLModel.metadata.create_all(engine)
    apply_migrations(engine, fresh_database)


def get_db() -> Iterator[Session]:
    """One database session per request."""
    with Session(engine) as session:
        yield session
