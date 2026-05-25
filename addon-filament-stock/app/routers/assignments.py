"""Tray-assignment endpoints (add-on 0.6.0).

Workflow:

  1. User loads a physical spool from their stock into an AMS tray.
  2. They click "Assign from stock" on that tray's card in the AMS panel.
  3. We:
     * decrement the chosen ColorStock's spool / refill counter,
     * write a TrayAssignment row linking (entity_id) -> (color_stock_id),
     * optionally call ``bambu_lab.set_filament`` so the printer's AMS
       display updates to match.
  4. Until the user un-assigns the tray (or assigns a different spool),
     the AMS panel overlays "from your stock: <brand> <material> <color>"
     on top of whatever ha-bambulab reports.

The "suggestions" endpoint backs the smart-default picker -- given a tray's
current material (PETG / PLA / ASA / ...) it returns the in-stock
filaments + colors sorted so the most likely choice is first.

Stock counter rule:

  * "spool" assignment decrements ColorStock.quantity_used  (increments used).
  * "refill" assignment decrements ColorStock.used_refill   (increments used).
  * Unassign reverses the same field.

We never let the counter go below 0 (defensive: if a row was edited
manually between assign and unassign we just stop at 0).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Path
from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..bambu_mapping import clamp_nozzle_temps, color_to_bambu_rgba, family_for
from ..database import get_db
from ..ha_client import HAClientError, call_service
from ..models import ColorStock, Filament, TrayAssignment

router = APIRouter(tags=["ams-assignments"])
_log = logging.getLogger("filament_stock.assignments")


# ── shared helpers ──────────────────────────────────────────────────────────


def _current_assignment(db: Session, entity_id: str) -> TrayAssignment | None:
    """Return the live (un-closed) assignment for an AMS entity, or None."""
    return (
        db.query(TrayAssignment)
        .filter(TrayAssignment.entity_id == entity_id)
        .filter(TrayAssignment.unassigned_at.is_(None))
        .order_by(desc(TrayAssignment.assigned_at))
        .first()
    )


def _serialize_assignment(a: TrayAssignment) -> dict[str, Any]:
    """Public shape returned to the frontend. Includes the joined color /
    filament info so the UI can render the overlay without a second fetch."""
    color = a.color_stock
    filament = color.filament if color else None
    return {
        "id": a.id,
        "entity_id": a.entity_id,
        "location_label": a.location_label or "",
        "color_stock_id": a.color_stock_id,
        "packaging": a.packaging,
        "pushed_to_printer": bool(a.pushed_to_printer),
        "push_error": a.push_error or "",
        "assigned_at": a.assigned_at.isoformat() if a.assigned_at else None,
        "unassigned_at": a.unassigned_at.isoformat() if a.unassigned_at else None,
        "notes": a.notes or "",
        "filament_db_id": filament.id if filament else None,
        "brand": filament.brand if filament else None,
        "material": filament.material if filament else None,
        "filament_type": filament.filament_type if filament else None,
        "color_name": color.color_name if color else None,
        "color_hex": color.color_hex if color else None,
    }


def _decrement_counter(color: ColorStock, packaging: str) -> None:
    """Mark one unit of the given packaging as used."""
    if packaging == "spool":
        color.quantity_used = (color.quantity_used or 0) + 1
    elif packaging == "refill":
        color.used_refill = (color.used_refill or 0) + 1
    else:
        raise HTTPException(
            status_code=400,
            detail=f"packaging must be 'spool' or 'refill', got {packaging!r}",
        )


def _increment_counter(color: ColorStock, packaging: str) -> None:
    """Reverse one unit of the given packaging when the user un-assigns."""
    if packaging == "spool":
        color.quantity_used = max(0, (color.quantity_used or 0) - 1)
    elif packaging == "refill":
        color.used_refill = max(0, (color.used_refill or 0) - 1)
    # No raise for unknown packaging on unassign -- legacy rows shouldn't
    # break the unassign flow. Just no-op.


def _available_count(color: ColorStock, packaging: str) -> int:
    if packaging == "spool":
        return max(0, (color.quantity or 0) - (color.quantity_used or 0))
    if packaging == "refill":
        return max(0, (color.quantity_refill or 0) - (color.used_refill or 0))
    return 0


def _normalise_material(raw: str | None) -> str:
    """Lowercase, strip spaces. Used for fuzzy-matching the tray's material
    against our filament_type / material fields when ranking suggestions."""
    return (raw or "").strip().lower()


# ── push-to-printer helper ──────────────────────────────────────────────────


async def _maybe_push_to_printer(
    *,
    entity_id: str,
    filament: Filament,
    color: ColorStock,
) -> tuple[bool, str]:
    """Call ``bambu_lab.set_filament`` for this assignment.

    Returns ``(pushed_ok, error_message)``. ``error_message`` is the empty
    string on success. Never raises -- we want the local stock decrement
    to commit even if the printer is offline; the UI surfaces the error
    instead.
    """
    family = family_for(filament.filament_type, filament.material)
    lo, hi = clamp_nozzle_temps(filament.nozzle_temp_min, filament.nozzle_temp_max)
    payload = {
        "entity_id": entity_id,
        "tray_info_idx": family.tray_info_idx,
        "tray_color": color_to_bambu_rgba(color.color_hex),
        "tray_type": family.tray_type,
        "nozzle_temp_min": lo,
        "nozzle_temp_max": hi,
    }
    _log.info("Pushing to printer via bambu_lab.set_filament: %s", payload)
    try:
        await call_service("bambu_lab", "set_filament", payload)
    except HAClientError as exc:
        _log.warning("bambu_lab.set_filament failed: %s", exc)
        return False, str(exc)
    return True, ""


# ── public model used in the AMS view ───────────────────────────────────────


def get_current_assignments_map(db: Session) -> dict[str, dict[str, Any]]:
    """Helper used by ams.py to attach the live assignment to each tray
    without doing one query per tray. Returns ``{entity_id: serialized}``.
    """
    rows = (
        db.query(TrayAssignment)
        .filter(TrayAssignment.unassigned_at.is_(None))
        .all()
    )
    return {a.entity_id: _serialize_assignment(a) for a in rows}


# ── routes ──────────────────────────────────────────────────────────────────


@router.get("/ams/trays/{entity_id}/suggestions")
def get_assignment_suggestions(
    entity_id: str = Path(...),
    material_hint: str | None = None,
    db: Session = Depends(get_db),
):
    """Return the smart-defaulted list of filaments+colors the user can
    assign to this tray.

    Each suggestion is a single (filament, color) pair so the UI can render
    a flat sorted list. Sort priority:

      1. Material matches the tray's current material (PETG tray -> PETG
         filaments first). Caller passes the tray's material via the
         ``material_hint`` query param; we tolerate missing / unknown.
      2. Color is in_stock with spools available (most common case).
      3. Color is in_stock with refills available.
      4. Anything else (ordered, out_of_stock, etc.).

    Within each tier, order by brand then color_name for predictability.
    """
    hint = _normalise_material(material_hint)

    filaments = db.query(Filament).all()
    suggestions: list[dict[str, Any]] = []
    for f in filaments:
        f_haystack = f"{_normalise_material(f.filament_type)} {_normalise_material(f.material)}"
        material_match = bool(hint) and hint in f_haystack
        for c in f.colors:
            spool_avail = max(0, (c.quantity or 0) - (c.quantity_used or 0))
            refill_avail = max(0, (c.quantity_refill or 0) - (c.used_refill or 0))
            status = c.status or "in_stock"
            if status != "in_stock" and spool_avail == 0 and refill_avail == 0:
                # Don't surface "ordered, none on hand" rows in the picker;
                # the user can't physically place that spool in the tray yet.
                # We still include in_stock rows with 0 available so the user
                # can record a placement that drives the counter negative
                # via the UI's "out of stock" warning if they really want.
                continue

            # Tier values: lower is "shown first".
            if material_match and spool_avail > 0:
                tier = 0
            elif material_match and refill_avail > 0:
                tier = 1
            elif spool_avail > 0:
                tier = 2
            elif refill_avail > 0:
                tier = 3
            else:
                tier = 4

            suggestions.append(
                {
                    "filament_db_id": f.id,
                    "color_stock_id": c.id,
                    "brand": f.brand,
                    "material": f.material,
                    "filament_type": f.filament_type,
                    "color_name": c.color_name,
                    "color_hex": c.color_hex,
                    "available_spool": spool_avail,
                    "available_refill": refill_avail,
                    "status": status,
                    "material_match": material_match,
                    "tier": tier,
                }
            )

    suggestions.sort(
        key=lambda s: (
            s["tier"],
            (s["brand"] or "").lower(),
            (s["color_name"] or "").lower(),
        )
    )
    return {
        "entity_id": entity_id,
        "material_hint": material_hint,
        "current_assignment": (
            _serialize_assignment(_current_assignment(db, entity_id))
            if _current_assignment(db, entity_id) else None
        ),
        "suggestions": suggestions,
    }


@router.post("/ams/trays/{entity_id}/assign", status_code=201)
async def assign_tray(
    entity_id: str = Path(...),
    payload: dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
):
    """Mark a tray as holding a specific spool from local stock.

    Body::

        {
          "color_stock_id": 17,
          "packaging": "spool" | "refill",
          "push_to_printer": true,        // optional, default false
          "location_label": "AMS 2 Pro #1 · Slot 3",  // optional, free-text
          "notes": ""                     // optional
        }

    Returns the new assignment row + the updated ColorStock counters.

    Side effects:
      * Closes any prior live assignment on this tray (and reverses its
        counter so the stock total doesn't drift).
      * Decrements the requested counter on the chosen color.
      * If ``push_to_printer`` is true, also calls
        ``bambu_lab.set_filament`` with the new metadata. A push failure
        does NOT roll back the local assignment -- we record the error
        on the assignment row instead so the user can retry.
    """
    color_stock_id = payload.get("color_stock_id")
    packaging = (payload.get("packaging") or "spool").strip().lower()
    push_to_printer = bool(payload.get("push_to_printer"))
    location_label = (payload.get("location_label") or "").strip()
    notes = (payload.get("notes") or "").strip()

    if not isinstance(color_stock_id, int):
        raise HTTPException(status_code=400, detail="color_stock_id (int) is required")

    color = db.query(ColorStock).filter(ColorStock.id == color_stock_id).first()
    if color is None:
        raise HTTPException(status_code=404, detail="ColorStock not found")
    filament = color.filament
    if filament is None:
        raise HTTPException(status_code=500, detail="ColorStock has no parent Filament -- DB inconsistency")

    if packaging not in ("spool", "refill"):
        raise HTTPException(
            status_code=400,
            detail=f"packaging must be 'spool' or 'refill', got {packaging!r}",
        )
    if _available_count(color, packaging) <= 0:
        raise HTTPException(
            status_code=409,
            detail=(
                f"No {packaging}s of {filament.brand} {filament.material} "
                f"({color.color_name}) available in stock. Record a purchase "
                "before assigning, or pick a different packaging."
            ),
        )

    # Close any prior live assignment on this tray and reverse its counter.
    prior = _current_assignment(db, entity_id)
    if prior is not None:
        prior_color = prior.color_stock
        if prior_color is not None:
            _increment_counter(prior_color, prior.packaging)
        prior.unassigned_at = datetime.now(timezone.utc)

    _decrement_counter(color, packaging)

    assignment = TrayAssignment(
        entity_id=entity_id,
        location_label=location_label,
        color_stock_id=color.id,
        packaging=packaging,
        pushed_to_printer=0,
        push_error="",
        notes=notes,
    )
    db.add(assignment)
    db.flush()  # populate assignment.id before potential printer push

    pushed_ok = False
    push_error = ""
    if push_to_printer:
        pushed_ok, push_error = await _maybe_push_to_printer(
            entity_id=entity_id,
            filament=filament,
            color=color,
        )
        assignment.pushed_to_printer = 1 if pushed_ok else 0
        assignment.push_error = push_error

    db.commit()
    db.refresh(assignment)
    db.refresh(color)

    return {
        "assignment": _serialize_assignment(assignment),
        "color": {
            "id": color.id,
            "filament_id": color.filament_id,
            "color_name": color.color_name,
            "color_hex": color.color_hex,
            "quantity": color.quantity,
            "quantity_used": color.quantity_used,
            "quantity_refill": color.quantity_refill,
            "used_refill": color.used_refill,
            "available_spool": _available_count(color, "spool"),
            "available_refill": _available_count(color, "refill"),
            "available_total": _available_count(color, "spool") + _available_count(color, "refill"),
        },
        "push_to_printer": {
            "requested": push_to_printer,
            "ok": pushed_ok if push_to_printer else None,
            "error": push_error if push_to_printer else "",
        },
    }


@router.post("/ams/trays/{entity_id}/unassign")
def unassign_tray(
    entity_id: str = Path(...),
    db: Session = Depends(get_db),
):
    """Close the live assignment for this tray and reverse its counter.

    No-op (returns ``{"ok": true, "had_assignment": false}``) if there
    is no live assignment.

    We do NOT clear the tray on the printer side -- the slot keeps whatever
    metadata it has. If the user wants to push an "empty" state they can
    assign a different spool with push_to_printer=true.
    """
    live = _current_assignment(db, entity_id)
    if live is None:
        return {"ok": True, "had_assignment": False}

    color = live.color_stock
    if color is not None:
        _increment_counter(color, live.packaging)
    live.unassigned_at = datetime.now(timezone.utc)
    db.commit()
    return {
        "ok": True,
        "had_assignment": True,
        "closed_assignment": _serialize_assignment(live),
    }


@router.get("/ams/trays/{entity_id}/assignment-history")
def assignment_history(
    entity_id: str = Path(...),
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """List recent assignments on this tray, newest first.

    Useful for "what did I last load here?" answers and for debugging the
    counter math.
    """
    limit = max(1, min(100, limit))
    rows = (
        db.query(TrayAssignment)
        .filter(TrayAssignment.entity_id == entity_id)
        .order_by(desc(TrayAssignment.assigned_at))
        .limit(limit)
        .all()
    )
    return {"entity_id": entity_id, "history": [_serialize_assignment(a) for a in rows]}
