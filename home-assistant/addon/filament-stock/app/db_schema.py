from sqlalchemy import text

from .database import engine


def apply_sqlite_migrations() -> None:
    """Lightweight SQLite migrations (create_all does not alter existing tables)."""
    with engine.begin() as conn:
        cols = {row[1] for row in conn.execute(text("PRAGMA table_info(filaments)"))}
        if "packaging_type" not in cols:
            conn.execute(
                text(
                    "ALTER TABLE filaments ADD COLUMN packaging_type VARCHAR NOT NULL DEFAULT 'spool'"
                )
            )
