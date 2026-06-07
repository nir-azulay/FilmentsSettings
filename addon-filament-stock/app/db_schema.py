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
        _filaments_temp_range_columns(conn)
        _upgrade_generic_abs_to_ys_filament(conn)
        _filaments_drying_columns(conn)
        _reset_zero_bed_temps(conn)
        _backfill_non_profile_filaments(conn)


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


def _filaments_temp_range_columns(conn) -> None:
    """0.16.4: add bed_temp_max and chamber_temp columns to filaments."""
    cols = _table_columns(conn, "filaments")
    for col in ("bed_temp_max", "chamber_temp"):
        if col not in cols:
            conn.execute(text(f"ALTER TABLE filaments ADD COLUMN {col} INTEGER"))
            _log.info("Added filaments.%s column", col)


def _reset_zero_bed_temps(conn) -> None:
    """NULL out bed_temp / bed_temp_max rows incorrectly set to 0.

    The old profile_sync included eng_plate_temp=0 in its min() calculation,
    setting bed_temp=0 for PLA/TPU filaments. profile_sync only fills NULL
    fields, so those zeroes would never be corrected without this migration.
    """
    result = conn.execute(
        text("UPDATE filaments SET bed_temp = NULL WHERE bed_temp = 0")
    )
    if result.rowcount:
        _log.info("Reset %d filament(s) with bed_temp=0 → NULL", result.rowcount)
    result2 = conn.execute(
        text("UPDATE filaments SET bed_temp_max = NULL WHERE bed_temp_max = 0")
    )
    if result2.rowcount:
        _log.info("Reset %d filament(s) with bed_temp_max=0 → NULL", result2.rowcount)


# Seed data for filaments that have no bundled BambuStudio profile so
# profile_sync cannot fill them automatically.
_NON_PROFILE_SEED: list[dict] = [
    {
        "brand": "Jayo", "material": "PLA Pro Cold White",
        "nozzle_temp_min": 200, "nozzle_temp_max": 230,
        "bed_temp": 35, "bed_temp_max": 65,
        "density": 1.24, "dry_temp": 65, "dry_time": 6,
    },
    {
        "brand": "Isanmate", "material": "PLA Pro",
        "nozzle_temp_min": 200, "nozzle_temp_max": 230,
        "bed_temp": 35, "bed_temp_max": 65,
        "density": 1.24, "dry_temp": 65, "dry_time": 6,
    },
    {
        "brand": "YS Filament", "material": "ABS",
        "nozzle_temp_min": 220, "nozzle_temp_max": 260,
        "bed_temp": 80, "bed_temp_max": 110,
        "chamber_temp": 60, "density": 1.05,
        "dry_temp": 80, "dry_time": 6,
    },
]


def _backfill_non_profile_filaments(conn) -> None:
    """Fill NULL fields on filaments that have no bundled BambuStudio profile.

    profile_sync skips these because bundle_for() returns None.  We patch
    them here so the label and UI always have useful data.  Only NULL fields
    are touched -- any value the user set manually is preserved.
    """
    for entry in _NON_PROFILE_SEED:
        brand = entry["brand"]
        material = entry["material"]
        row = conn.execute(
            text("SELECT id FROM filaments WHERE brand = :b AND material = :m LIMIT 1"),
            {"b": brand, "m": material},
        ).fetchone()
        if not row:
            continue
        fid = row[0]
        cols = _table_columns(conn, "filaments")
        updates = []
        params: dict = {"fid": fid}
        for col, val in entry.items():
            if col in ("brand", "material") or col not in cols:
                continue
            cur = conn.execute(
                text(f"SELECT {col} FROM filaments WHERE id = :fid"), {"fid": fid}
            ).scalar()
            if cur is None:
                updates.append(f"{col} = :{col}")
                params[col] = val
        if updates:
            conn.execute(
                text(f"UPDATE filaments SET {', '.join(updates)} WHERE id = :fid"),
                params,
            )
            _log.info("Backfilled %s %s: %s", brand, material, list(params.keys() - {"fid"}))


def _filaments_drying_columns(conn) -> None:
    """Add dry_temp and dry_time columns to filaments."""
    cols = _table_columns(conn, "filaments")
    for col in ("dry_temp", "dry_time"):
        if col not in cols:
            conn.execute(text(f"ALTER TABLE filaments ADD COLUMN {col} INTEGER"))
            _log.info("Added filaments.%s column", col)


def _upgrade_generic_abs_to_ys_filament(conn) -> None:
    """0.16.7: convert 'Generic ABS' filament to 'YS Filament ABS' with TDS data."""
    row = conn.execute(
        text("SELECT id FROM filaments WHERE brand = 'Generic' AND material = 'ABS' LIMIT 1")
    ).fetchone()
    if not row:
        return
    conn.execute(
        text(
            "UPDATE filaments SET "
            "brand = 'YS Filament', "
            "material = 'ABS', "
            "filament_type = 'ABS', "
            "nozzle_temp_min = 220, "
            "nozzle_temp_max = 260, "
            "bed_temp = 80, "
            "bed_temp_max = 110, "
            "chamber_temp = 60, "
            "density = 1.04, "
            "amazon_url = 'https://a.co/d/02OrrAfC' "
            "WHERE id = :fid"
        ),
        {"fid": row[0]},
    )
    _log.info("Upgraded Generic ABS (id=%s) to YS Filament ABS", row[0])
