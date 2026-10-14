"""
Tests for database_migrations.py: steps run once and in order on an existing
database, and a brand-new database skips them (its tables are already current).
"""

from sqlalchemy import create_engine, text

from app import database_migrations


def _columns(engine) -> list[str]:
    with engine.connect() as connection:
        return [row[1] for row in connection.execute(text("PRAGMA table_info(entry)"))]


def test_existing_database_runs_new_steps_once(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'old.db'}")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE entry (id VARCHAR PRIMARY KEY)"))
    monkeypatch.setattr(
        database_migrations,
        "MIGRATIONS",
        ["ALTER TABLE entry ADD COLUMN location VARCHAR NOT NULL DEFAULT ''"],
    )

    database_migrations.apply_migrations(engine, fresh_database=False)
    database_migrations.apply_migrations(engine, fresh_database=False)

    assert _columns(engine) == ["id", "location"]


def test_fresh_database_skips_steps(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'new.db'}")
    assert database_migrations.database_is_empty(engine)
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE entry (id VARCHAR PRIMARY KEY, location VARCHAR)"))
    monkeypatch.setattr(database_migrations, "MIGRATIONS", ["ALTER TABLE entry ADD COLUMN location VARCHAR"])

    database_migrations.apply_migrations(engine, fresh_database=True)

    with engine.connect() as connection:
        assert connection.execute(text("PRAGMA user_version")).scalar_one() == 1
