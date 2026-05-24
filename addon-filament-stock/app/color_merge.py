"""One stock row per (filament, color name) — orders are not tracked separately."""

from sqlalchemy.orm import Session

from .models import ColorStock, StockEntry


def normalize_color_name(name: str) -> str:
    return " ".join((name or "").strip().split()).casefold()


def pick_status(statuses: list[str]) -> str:
    if any(s == "in_stock" for s in statuses):
        return "in_stock"
    if any(s == "ordered" for s in statuses):
        return "ordered"
    return "out_of_stock"


def find_color_by_name(db: Session, filament_id: int, color_name: str) -> ColorStock | None:
    key = normalize_color_name(color_name)
    for c in db.query(ColorStock).filter(ColorStock.filament_id == filament_id).all():
        if normalize_color_name(c.color_name) == key:
            return c
    return None


def merge_duplicate_colors(db: Session) -> dict:
    """Merge rows that share the same filament + color name."""
    merged_groups = 0
    removed_rows = 0
    filament_ids = [row[0] for row in db.query(ColorStock.filament_id).distinct().all()]

    for filament_id in filament_ids:
        rows = db.query(ColorStock).filter(ColorStock.filament_id == filament_id).all()
        buckets: dict[str, list[ColorStock]] = {}
        for row in rows:
            buckets.setdefault(normalize_color_name(row.color_name), []).append(row)

        for _key, group in buckets.items():
            if len(group) < 2:
                continue
            merged_groups += 1
            group.sort(key=lambda r: r.id)
            keep = group[0]
            extras = group[1:]

            keep.quantity = sum(r.quantity or 0 for r in group)
            keep.quantity_used = sum(r.quantity_used or 0 for r in group)
            keep.status = pick_status([(r.status or "in_stock") for r in group])
            keep.order_id = None

            for extra in extras:
                db.query(StockEntry).filter(StockEntry.color_stock_id == extra.id).update(
                    {StockEntry.color_stock_id: keep.id}
                )
                db.delete(extra)
                removed_rows += 1

    db.commit()
    return {"merged_groups": merged_groups, "removed_rows": removed_rows}
