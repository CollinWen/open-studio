"""
Database migrations: changes to tables that already exist, applied in order on startup.

database.py creates missing tables, but never changes a table that's already in
the database. So when a field is added to (or renamed in) a models.py, add one
SQL statement to the end of MIGRATIONS. The database remembers how many steps
it has run (SQLite's `user_version`), so each step runs exactly once.

Never edit, reorder or remove a step once it's been deployed; add a new one instead.
"""

from sqlalchemy import Engine, inspect, text

# One SQL statement per step, oldest first.
# Example: "ALTER TABLE entry ADD COLUMN location VARCHAR NOT NULL DEFAULT ''"
MIGRATIONS: list[str] = []


def database_is_empty(engine: Engine) -> bool:
    """True before any table exists, i.e. a brand-new database."""
    return not inspect(engine).get_table_names()


def apply_migrations(engine: Engine, fresh_database: bool) -> None:
    """Run every step the database hasn't run yet."""
    with engine.begin() as connection:
        if fresh_database:
            # Tables were just created from models.py, so they already include every change.
            _set_version(connection, len(MIGRATIONS))
            return

        version = connection.execute(text("PRAGMA user_version")).scalar_one()
        for number, statement in enumerate(MIGRATIONS[version:], start=version + 1):
            connection.execute(text(statement))
            _set_version(connection, number)


def _set_version(connection, version: int) -> None:
    # PRAGMA can't take bound parameters; version is always our own integer.
    connection.execute(text(f"PRAGMA user_version = {int(version)}"))
