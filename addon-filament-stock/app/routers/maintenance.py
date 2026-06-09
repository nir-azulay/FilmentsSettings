from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import DateTime as _DT
from sqlalchemy.orm import Session

from ..addon_options import ADDON_VERSION
from ..color_merge import merge_duplicate_colors
from ..database import get_db
from ..models import (
    ColorStock,
    Filament,
    SpoolEvent,
    SpoolInstance,
    StapleAlertIgnore,
    StockEntry,
    TrayAssignment,
    UsageLog,
)

router = APIRouter(tags=["maintenance"])

# Ordered from leaf tables (no dependents) to root tables (most depended-on).
# Used for DELETE (this order) and INSERT (reversed).
_DELETE_ORDER = [
    UsageLog,
    SpoolEvent,
    SpoolInstance,
    TrayAssignment,
    StockEntry,
    StapleAlertIgnore,
    ColorStock,
    Filament,
]

_TABLE_KEY_MAP = {
    "filaments": Filament,
    "color_stocks": ColorStock,
    "stock_entries": StockEntry,
    "staple_alert_ignores": StapleAlertIgnore,
    "tray_assignments": TrayAssignment,
    "spool_instances": SpoolInstance,
    "spool_events": SpoolEvent,
    "usage_logs": UsageLog,
}

_DATETIME_COLS: dict[type, set[str]] = {
    model: {c.name for c in model.__table__.columns if isinstance(c.type, _DT)}
    for model in _TABLE_KEY_MAP.values()
}


def _serialize_row(row) -> dict:
    d = {}
    for c in row.__table__.columns:
        val = getattr(row, c.name)
        if isinstance(val, datetime):
            val = val.isoformat()
        d[c.name] = val
    return d


def _parse_datetimes(data: dict, model) -> dict:
    dt_cols = _DATETIME_COLS.get(model, set())
    for key in dt_cols:
        val = data.get(key)
        if isinstance(val, str):
            data[key] = datetime.fromisoformat(val)
        elif val is None:
            data[key] = None
    return data


@router.post("/maintenance/merge-duplicate-colors")
def merge_colors(db: Session = Depends(get_db)):
    return merge_duplicate_colors(db)


@router.get("/export")
def export_database(db: Session = Depends(get_db)):
    result = {
        "version": "1.0",
        "addon_version": ADDON_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }
    for key, model in _TABLE_KEY_MAP.items():
        rows = db.query(model).all()
        result[key] = [_serialize_row(r) for r in rows]
    return result


@router.post("/import")
def import_database(payload: dict = Body(...), db: Session = Depends(get_db)):
    version = payload.get("version", "")
    if not isinstance(version, str) or not version.startswith("1."):
        raise HTTPException(status_code=400, detail=f"Unsupported export version: {version!r}")

    try:
        for model in _DELETE_ORDER:
            db.query(model).delete()
        db.flush()

        # Insert in reverse FK order (root tables first).
        insert_order = list(reversed(_DELETE_ORDER))
        counts: dict[str, int] = {}
        for model in insert_order:
            key = model.__tablename__
            rows = payload.get(key, [])
            for row_data in rows:
                row_data = _parse_datetimes(dict(row_data), model)
                db.add(model(**row_data))
            counts[key] = len(rows)

        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "ok": True,
        "filaments": counts.get("filaments", 0),
        "colors": counts.get("color_stocks", 0),
        "spools": counts.get("spool_instances", 0),
    }
