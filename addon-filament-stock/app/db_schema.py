"""Lightweight SQLite migrations.

`create_all()` in main.py creates new tables/columns but does NOT alter
existing ones. Anything that touches an existing table goes here.
"""

import logging
import secrets

from sqlalchemy import text

from .database import engine

_log = logging.getLogger("filament_stock.migrations")


def apply_sqlite_migrations() -> None:
    with engine.begin() as conn:
        _filaments_packaging_type_migration(conn)
        _color_stocks_refill_columns(conn)
        _tray_assignments_spool_instance_column(conn)
        _migrate_counters_to_spool_instances(conn)


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


def _table_exists(conn, table: str) -> bool:
    row = conn.execute(
        text("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=:t"),
        {"t": table},
    ).scalar()
    return bool(row)


def _tray_assignments_spool_instance_column(conn) -> None:
    """0.15.0: add nullable FK from tray_assignments to spool_instances."""
    if not _table_exists(conn, "tray_assignments"):
        return
    cols = _table_columns(conn, "tray_assignments")
    if "spool_instance_id" not in cols:
        try:
            conn.execute(
                text(
                    "ALTER TABLE tray_assignments ADD COLUMN spool_instance_id INTEGER"
                )
            )
        except Exception:
            pass


def _generate_uid(conn) -> str:
    """Generate a unique SP-XXXXXXXX identifier with collision retry."""
    for _ in range(20):
        uid = "SP-" + secrets.token_hex(4).upper()
        exists = conn.execute(
            text("SELECT 1 FROM spool_instances WHERE uid = :u"), {"u": uid}
        ).first()
        if not exists:
            return uid
    raise RuntimeError("Failed to generate unique spool UID after 20 attempts")


def _migrate_counters_to_spool_instances(conn) -> None:
    """0.15.0: create SpoolInstance rows from existing ColorStock counters.

    Runs once -- if spool_instances already has rows, we skip entirely.
    This is idempotent: the table is created by create_all() in main.py
    before migrations run; we just populate it from the counter data.
    """
    if not _table_exists(conn, "spool_instances"):
        return

    existing = conn.execute(text("SELECT COUNT(*) FROM spool_instances")).scalar()
    if existing:
        return  # already migrated

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()

    colors = conn.execute(
        text(
            "SELECT id, quantity, quantity_used, quantity_refill, used_refill "
            "FROM color_stocks"
        )
    ).fetchall()

    created = 0
    for row in colors:
        cs_id, qty, qty_used, qty_refill, used_refill = row
        avail_spool = max(0, (qty or 0) - (qty_used or 0))
        avail_refill = max(0, (qty_refill or 0) - (used_refill or 0))

        for _ in range(avail_spool):
            uid = _generate_uid(conn)
            conn.execute(
                text(
                    "INSERT INTO spool_instances "
                    "(uid, color_stock_id, packaging, status, created_at, notes) "
                    "VALUES (:uid, :cs, 'spool', 'in_stock', :now, '')"
                ),
                {"uid": uid, "cs": cs_id, "now": now},
            )
            created += 1

        for _ in range(avail_refill):
            uid = _generate_uid(conn)
            conn.execute(
                text(
                    "INSERT INTO spool_instances "
                    "(uid, color_stock_id, packaging, status, created_at, notes) "
                    "VALUES (:uid, :cs, 'refill', 'in_stock', :now, '')"
                ),
                {"uid": uid, "cs": cs_id, "now": now},
            )
            created += 1

    # Migrate active tray assignments -> in_tray spool instances.
    active_assigns = conn.execute(
        text(
            "SELECT id, entity_id, color_stock_id, packaging "
            "FROM tray_assignments WHERE unassigned_at IS NULL"
        )
    ).fetchall()

    for arow in active_assigns:
        a_id, entity_id, cs_id, packaging = arow
        uid = _generate_uid(conn)
        conn.execute(
            text(
                "INSERT INTO spool_instances "
                "(uid, color_stock_id, packaging, status, tray_entity_id, "
                " tray_assignment_id, created_at, notes) "
                "VALUES (:uid, :cs, :pkg, 'in_tray', :eid, :aid, :now, '')"
            ),
            {"uid": uid, "cs": cs_id, "pkg": packaging, "eid": entity_id, "aid": a_id, "now": now},
        )
        created += 1

    _log.info("Spool migration: created %d SpoolInstance rows from counters", created)
