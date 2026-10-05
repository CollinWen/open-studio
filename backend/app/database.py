"""
Database: opens the SQLite file and hands out sessions to the rest of the app.

Tables themselves are defined in each feature's models.py. This file only
creates them on startup and provides `get_db` for routes to use.
"""

from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

settings.data_dir.mkdir(parents=True, exist_ok=True)
engine = create_engine(
    f"sqlite:///{settings.database_path}",
    connect_args={"check_same_thread": False},
)


def create_tables() -> None:
    """Create any missing tables. Imports models so SQLModel knows about them."""
    from app.features.entries import models  # noqa: F401
    from app.features.tags import models as tag_models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_db() -> Iterator[Session]:
    """One database session per request."""
    with Session(engine) as session:
        yield session
