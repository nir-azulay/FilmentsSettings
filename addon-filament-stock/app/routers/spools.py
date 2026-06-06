"""Spool-instance endpoints (add-on 0.15.0).

Individual spool/refill tracking with unique scannable UIDs.
Lifecycle: in_stock -> in_tray -> empty.
"""

from __future__ import annotations

import io
import logging
import secrets
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..addon_options import get_options
from ..database import get_db
from ..models import ColorStock, Filament, SpoolInstance, TrayAssignment

router = APIRouter(tags=["spools"])
_log = logging.getLogger("filament_stock.spools")


def _generate_uid(db: Session) -> str:
    for _ in range(20):
        uid = "SP-" + secrets.token_hex(4).upper()
        if not db.query(SpoolInstance).filter(SpoolInstance.uid == uid).first():
            return uid
    raise RuntimeError("Failed to generate unique spool UID")


def _serialize_spool(s: SpoolInstance) -> dict[str, Any]:
    color = s.color_stock
    filament = color.filament if color else None
    return {
        "id": s.id,
        "uid": s.uid,
        "color_stock_id": s.color_stock_id,
        "packaging": s.packaging,
        "status": s.status,
        "tray_entity_id": s.tray_entity_id,
        "tray_assignment_id": s.tray_assignment_id,
        "remain_pct": s.remain_pct,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "assigned_at": s.assigned_at.isoformat() if s.assigned_at else None,
        "emptied_at": s.emptied_at.isoformat() if s.emptied_at else None,
        "notes": s.notes or "",
        "brand": filament.brand if filament else None,
        "material": filament.material if filament else None,
        "filament_type": filament.filament_type if filament else None,
        "color_name": color.color_name if color else None,
        "color_hex": color.color_hex if color else None,
        "nozzle_temp_min": filament.nozzle_temp_min if filament else None,
        "nozzle_temp_max": filament.nozzle_temp_max if filament else None,
        "bed_temp": filament.bed_temp if filament else None,
    }


def _get_spool_or_404(db: Session, uid: str) -> SpoolInstance:
    spool = db.query(SpoolInstance).filter(SpoolInstance.uid == uid).first()
    if not spool:
        raise HTTPException(status_code=404, detail=f"Spool {uid} not found")
    return spool


# ── CRUD ────────────────────────────────────────────────────────────────────


@router.get("/spools")
def list_spools(
    color_stock_id: int | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(SpoolInstance)
    if color_stock_id is not None:
        q = q.filter(SpoolInstance.color_stock_id == color_stock_id)
    if status:
        q = q.filter(SpoolInstance.status == status)
    rows = q.order_by(SpoolInstance.created_at.desc()).all()
    return [_serialize_spool(s) for s in rows]


@router.get("/spools/{uid}")
def get_spool(uid: str = Path(...), db: Session = Depends(get_db)):
    return _serialize_spool(_get_spool_or_404(db, uid))


@router.post("/spools", status_code=201)
def create_spool(
    payload: dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
):
    color_stock_id = payload.get("color_stock_id")
    packaging = (payload.get("packaging") or "spool").strip().lower()
    notes = (payload.get("notes") or "").strip()

    if not isinstance(color_stock_id, int):
        raise HTTPException(400, "color_stock_id (int) is required")
    if packaging not in ("spool", "refill"):
        raise HTTPException(400, f"packaging must be 'spool' or 'refill', got {packaging!r}")

    color = db.query(ColorStock).filter(ColorStock.id == color_stock_id).first()
    if not color:
        raise HTTPException(404, "ColorStock not found")

    uid = _generate_uid(db)
    spool = SpoolInstance(
        uid=uid,
        color_stock_id=color_stock_id,
        packaging=packaging,
        status="in_stock",
        notes=notes,
    )
    db.add(spool)

    if packaging == "spool":
        color.quantity = (color.quantity or 0) + 1
    else:
        color.quantity_refill = (color.quantity_refill or 0) + 1

    db.commit()
    db.refresh(spool)
    _log.info("Created spool %s for color_stock %d (%s)", uid, color_stock_id, packaging)
    return _serialize_spool(spool)


@router.put("/spools/{uid}")
def update_spool(
    uid: str = Path(...),
    payload: dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
):
    spool = _get_spool_or_404(db, uid)
    if "notes" in payload:
        spool.notes = str(payload["notes"])
    if "remain_pct" in payload:
        val = payload["remain_pct"]
        spool.remain_pct = max(0, min(100, int(val))) if val is not None else None
    db.commit()
    db.refresh(spool)
    return _serialize_spool(spool)


@router.delete("/spools/{uid}")
def delete_spool(uid: str = Path(...), db: Session = Depends(get_db)):
    spool = _get_spool_or_404(db, uid)
    if spool.status == "in_tray":
        raise HTTPException(409, "Cannot delete a spool that is currently in a tray. Unassign it first.")

    color = spool.color_stock
    if color and spool.status == "in_stock":
        if spool.packaging == "spool":
            color.quantity = max(0, (color.quantity or 0) - 1)
        else:
            color.quantity_refill = max(0, (color.quantity_refill or 0) - 1)

    db.delete(spool)
    db.commit()
    return {"ok": True, "uid": uid}


# ── Lifecycle ───────────────────────────────────────────────────────────────


@router.post("/spools/{uid}/assign")
async def assign_spool_to_tray(
    uid: str = Path(...),
    payload: dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
):
    """Assign a specific spool to an AMS tray."""
    from ..bambu_mapping import clamp_nozzle_temps, color_to_bambu_rgba, family_for
    from ..ha_client import HAClientError, call_service

    spool = _get_spool_or_404(db, uid)
    entity_id = payload.get("entity_id")
    push_to_printer = bool(payload.get("push_to_printer"))
    location_label = (payload.get("location_label") or "").strip()
    return_prior_to_stock = payload.get("return_prior_to_stock", True)
    notes = (payload.get("notes") or "").strip()

    if not entity_id:
        raise HTTPException(400, "entity_id is required")
    if spool.status not in ("in_stock",):
        raise HTTPException(409, f"Spool {uid} status is '{spool.status}', must be 'in_stock' to assign")

    color = spool.color_stock
    filament = color.filament if color else None
    if not filament:
        raise HTTPException(500, "Spool has no parent filament")

    # Close any prior live assignment on this tray.
    prior = (
        db.query(TrayAssignment)
        .filter(TrayAssignment.entity_id == entity_id)
        .filter(TrayAssignment.unassigned_at.is_(None))
        .first()
    )
    if prior is not None:
        if return_prior_to_stock:
            prior_color = prior.color_stock
            if prior_color:
                if prior.packaging == "spool":
                    prior_color.quantity_used = max(0, (prior_color.quantity_used or 0) - 1)
                elif prior.packaging == "refill":
                    prior_color.used_refill = max(0, (prior_color.used_refill or 0) - 1)
            # If there's a linked SpoolInstance on the prior assignment, return it to stock
            if prior.spool_instance and prior.spool_instance.uid != uid:
                prior.spool_instance.status = "in_stock"
                prior.spool_instance.tray_entity_id = None
                prior.spool_instance.tray_assignment_id = None
        prior.unassigned_at = datetime.now(timezone.utc)

    # Decrement counter on the color
    if spool.packaging == "spool":
        color.quantity_used = (color.quantity_used or 0) + 1
    else:
        color.used_refill = (color.used_refill or 0) + 1

    # Create tray assignment
    now = datetime.now(timezone.utc)
    assignment = TrayAssignment(
        entity_id=entity_id,
        location_label=location_label,
        color_stock_id=color.id,
        packaging=spool.packaging,
        pushed_to_printer=0,
        push_error="",
        notes=notes,
    )
    db.add(assignment)
    db.flush()

    # Update spool instance
    spool.status = "in_tray"
    spool.tray_entity_id = entity_id
    spool.tray_assignment_id = assignment.id
    spool.assigned_at = now

    pushed_ok = False
    push_error = ""
    if push_to_printer:
        family = family_for(filament.filament_type, filament.material)
        lo, hi = clamp_nozzle_temps(filament.nozzle_temp_min, filament.nozzle_temp_max)
        svc_payload = {
            "entity_id": entity_id,
            "tray_info_idx": family.tray_info_idx,
            "tray_color": color_to_bambu_rgba(color.color_hex),
            "tray_type": family.tray_type,
            "nozzle_temp_min": lo,
            "nozzle_temp_max": hi,
        }
        try:
            await call_service("bambu_lab", "set_filament", svc_payload)
            pushed_ok = True
        except HAClientError as exc:
            push_error = str(exc)
        assignment.pushed_to_printer = 1 if pushed_ok else 0
        assignment.push_error = push_error

    db.commit()
    db.refresh(spool)
    return {
        "ok": True,
        "spool": _serialize_spool(spool),
        "push_to_printer": {
            "requested": push_to_printer,
            "ok": pushed_ok if push_to_printer else None,
            "error": push_error,
        },
    }


@router.post("/spools/{uid}/unassign")
def unassign_spool(uid: str = Path(...), db: Session = Depends(get_db)):
    spool = _get_spool_or_404(db, uid)
    if spool.status != "in_tray":
        raise HTTPException(409, f"Spool {uid} is not in a tray (status: {spool.status})")

    color = spool.color_stock
    if color:
        if spool.packaging == "spool":
            color.quantity_used = max(0, (color.quantity_used or 0) - 1)
        else:
            color.used_refill = max(0, (color.used_refill or 0) - 1)

    # Close the tray assignment
    if spool.tray_assignment_id:
        assignment = db.query(TrayAssignment).get(spool.tray_assignment_id)
        if assignment and assignment.unassigned_at is None:
            assignment.unassigned_at = datetime.now(timezone.utc)

    spool.status = "in_stock"
    spool.tray_entity_id = None
    spool.tray_assignment_id = None
    db.commit()
    db.refresh(spool)
    return {"ok": True, "spool": _serialize_spool(spool)}


@router.post("/spools/{uid}/empty")
def mark_spool_empty(uid: str = Path(...), db: Session = Depends(get_db)):
    spool = _get_spool_or_404(db, uid)
    if spool.status == "empty":
        return {"ok": True, "spool": _serialize_spool(spool)}

    was_in_tray = spool.status == "in_tray"

    # If it was in a tray, close the assignment but do NOT return to stock
    if was_in_tray and spool.tray_assignment_id:
        assignment = db.query(TrayAssignment).get(spool.tray_assignment_id)
        if assignment and assignment.unassigned_at is None:
            assignment.unassigned_at = datetime.now(timezone.utc)

    # If it was in_stock, decrement the counter (mark as used)
    color = spool.color_stock
    if not was_in_tray and color:
        if spool.packaging == "spool":
            color.quantity_used = (color.quantity_used or 0) + 1
        else:
            color.used_refill = (color.used_refill or 0) + 1

    spool.status = "empty"
    spool.emptied_at = datetime.now(timezone.utc)
    spool.tray_entity_id = None
    spool.tray_assignment_id = None
    db.commit()
    db.refresh(spool)
    return {"ok": True, "spool": _serialize_spool(spool)}


# ── Label generation ────────────────────────────────────────────────────────


@router.get("/spools/{uid}/label")
def get_spool_label(uid: str = Path(...), db: Session = Depends(get_db)):
    spool = _get_spool_or_404(db, uid)
    opts = get_options()
    ha_url = getattr(opts, "ha_external_url", "") or None

    from ..label_renderer import render_label
    img = render_label(spool, ha_url)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={
            "Content-Disposition": f'inline; filename="{uid}.png"',
            "Cache-Control": "no-cache",
        },
    )


@router.post("/spools/{uid}/print")
async def print_spool_label(uid: str = Path(...), db: Session = Depends(get_db)):
    spool = _get_spool_or_404(db, uid)
    opts = get_options()
    ha_url = getattr(opts, "ha_external_url", "") or None
    printer_addr = getattr(opts, "niimbot_address", "") or ""

    if not printer_addr:
        raise HTTPException(400, "Niimbot printer address not configured. Set niimbot_address in add-on options.")

    from ..label_renderer import render_label
    from ..niimbot_client import print_to_niimbot

    img = render_label(spool, ha_url)
    result = await print_to_niimbot(img, printer_addr)
    return result
