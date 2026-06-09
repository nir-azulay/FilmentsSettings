import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ColorStock, Filament, UsageLog

_log = logging.getLogger("filament_stock")
router = APIRouter(tags=["analytics"])


def _serialize_row(row):
    """Convert a SQLAlchemy row to dict with ISO dates."""
    d = {c.name: getattr(row, c.name) for c in row.__table__.columns}
    for k, v in d.items():
        if isinstance(v, datetime):
            d[k] = v.isoformat()
    return d


@router.get("/analytics/usage")
def get_usage(
    period: str = Query("30d", pattern="^(7d|30d|90d|all)$"),
    group_by: str = Query("material", pattern="^(brand|material|color)$"),
    db: Session = Depends(get_db),
):
    """Aggregated usage data for charts."""
    now = datetime.now(timezone.utc)
    if period == "all":
        cutoff = datetime(2000, 1, 1, tzinfo=timezone.utc)
    else:
        days = int(period.replace("d", ""))
        cutoff = now - timedelta(days=days)

    query = (
        db.query(UsageLog)
        .join(ColorStock, UsageLog.color_stock_id == ColorStock.id)
        .join(Filament, ColorStock.filament_id == Filament.id)
        .filter(UsageLog.logged_at >= cutoff)
    )

    logs = query.all()

    # Group by the requested dimension
    groups = {}
    for log in logs:
        cs = log.color_stock
        fil = cs.filament
        if group_by == "brand":
            key = fil.brand
        elif group_by == "material":
            key = fil.material
        else:
            key = f"{cs.color_name} ({fil.brand} {fil.material})"

        if key not in groups:
            groups[key] = {"label": key, "total_grams": 0, "count": 0}
        groups[key]["total_grams"] += log.grams_used
        groups[key]["count"] += 1

    # Time series (weekly buckets)
    weeks = {}
    for log in logs:
        week_start = log.logged_at.strftime("%Y-W%W")
        if week_start not in weeks:
            weeks[week_start] = 0
        weeks[week_start] += log.grams_used

    timeline = [{"week": k, "grams": v} for k, v in sorted(weeks.items())]

    return {
        "period": period,
        "group_by": group_by,
        "groups": sorted(groups.values(), key=lambda g: g["total_grams"], reverse=True),
        "timeline": timeline,
        "total_grams": sum(g["total_grams"] for g in groups.values()),
    }


@router.get("/analytics/predictions")
def get_predictions(db: Session = Depends(get_db)):
    """Predict when each active color will run out based on rolling average usage."""
    now = datetime.now(timezone.utc)
    cutoff_30d = now - timedelta(days=30)

    colors = db.query(ColorStock).filter(ColorStock.status == "in_stock").all()

    predictions = []
    for cs in colors:
        fil = cs.filament
        available = cs.available_total
        if available <= 0:
            continue

        usage_30d = (
            db.query(func.sum(UsageLog.grams_used))
            .filter(
                UsageLog.color_stock_id == cs.id,
                UsageLog.logged_at >= cutoff_30d,
            )
            .scalar() or 0
        )

        if usage_30d <= 0:
            continue

        grams_per_unit = (fil.density or 1.24) * 1000 / 1.24
        total_grams_available = available * 1000

        daily_rate = usage_30d / 30
        days_remaining = total_grams_available / daily_rate if daily_rate > 0 else 999

        predictions.append({
            "color_stock_id": cs.id,
            "brand": fil.brand,
            "material": fil.material,
            "color_name": cs.color_name,
            "color_hex": cs.color_hex,
            "available_units": available,
            "usage_30d_grams": round(usage_30d, 1),
            "daily_rate_grams": round(daily_rate, 1),
            "days_remaining": round(days_remaining),
            "estimated_runout": (now + timedelta(days=days_remaining)).isoformat() if days_remaining < 365 else None,
        })

    predictions.sort(key=lambda p: p["days_remaining"])
    return {"predictions": predictions}


@router.post("/analytics/log-usage")
def log_usage(
    payload: dict,
    db: Session = Depends(get_db),
):
    """Manually log filament usage."""
    log = UsageLog(
        spool_instance_id=payload.get("spool_instance_id"),
        color_stock_id=payload["color_stock_id"],
        grams_used=payload["grams_used"],
        source=payload.get("source", "manual"),
        print_name=payload.get("print_name", ""),
        notes=payload.get("notes", ""),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return _serialize_row(log)


@router.get("/analytics/logs")
def get_logs(
    color_stock_id: int = Query(None),
    spool_instance_id: int = Query(None),
    limit: int = Query(50),
    db: Session = Depends(get_db),
):
    """Get recent usage logs, optionally filtered."""
    query = db.query(UsageLog).order_by(UsageLog.logged_at.desc())
    if color_stock_id:
        query = query.filter(UsageLog.color_stock_id == color_stock_id)
    if spool_instance_id:
        query = query.filter(UsageLog.spool_instance_id == spool_instance_id)
    logs = query.limit(limit).all()
    return [_serialize_row(log) for log in logs]
