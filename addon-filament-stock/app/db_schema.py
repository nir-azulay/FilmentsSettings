"""Lightweight SQLite migrations.

`create_all()` in main.py creates new tables/columns but does NOT alter
existing ones. Anything that touches an existing table goes here.
"""

from sqlalchemy import text

from .database import engine


def apply_sqlite_migrations() -> None:
    with engine.begin() as conn:
        _filaments_packaging_type_migration(conn)
        _color_stocks_refill_columns(conn)


def _table_columns(conn, table: str) -> set[str]:
    return {row[1] for row in conn.execute(text(f"PRAGMA table_info({table})"))}


def _filaments_packaging_type_migration(conn) -> None:
    """0.3.0: move packaging_type off filaments onto each color row.

    Historical context:
      * 0.1.x added `filaments.packaging_type` (spool|refill).
      * 0.3.0 splits per-color into `quantity` + `quantity_refill`.
      * For every existing color, if the parent filament was a refill, the
        existing (quantity, quantity_used) really meant refill counts -- move
        them into (quantity_refill, used_refill) and zero out the spool fields.

    Then drop `filaments.packaging_type` since it is no longer meaningful at
    the filament level.
    """
    filaments_cols = _table_columns(conn, "filaments")
    if "packaging_type" not in filaments_cols:
        return  # already migrated, or fresh install with new schema

    # Ensure the new color columns exist before we backfill into them.
    _ensure_color_refill_columns(conn)

    # Backfill: any color whose parent filament was a refill needs its
    # (quantity, quantity_used) moved into (quantity_refill, used_refill).
    conn.execute(
        text(
            """
            UPDATE color_stocks
               SET quantity_refill = color_stocks.quantity,
                   used_refill     = color_stocks.quantity_used,
                   quantity        = 0,
                   quantity_used   = 0
             WHERE filament_id IN (
                   SELECT id FROM filaments WHERE packaging_type = 'refill'
             )
            """
        )
    )

    # Drop the now-unused packaging_type column.
    # SQLite 3.35+ supports ALTER TABLE DROP COLUMN; HA's bundled SQLite is new
    # enough. Wrap in try/except so older sqlite installs degrade gracefully
    # (the column will just sit unused).
    try:
        conn.execute(text("ALTER TABLE filaments DROP COLUMN packaging_type"))
    except Exception:
        pass


def _color_stocks_refill_columns(conn) -> None:
    """Standalone migration -- if filaments never had packaging_type but the
    color_stocks table still pre-dates 0.3.0 (e.g. someone created a DB by
    hand), ensure the new refill columns exist."""
    _ensure_color_refill_columns(conn)


def _ensure_color_refill_columns(conn) -> None:
    cols = _table_columns(conn, "color_stocks")
    if "quantity_refill" not in cols:
        conn.execute(
            text(
                "ALTER TABLE color_stocks ADD COLUMN quantity_refill INTEGER NOT NULL DEFAULT 0"
            )
        )
    if "used_refill" not in cols:
        conn.execute(
            text(
                "ALTER TABLE color_stocks ADD COLUMN used_refill INTEGER NOT NULL DEFAULT 0"
            )
        )
