import base64
import io
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ColorStock, Filament

_log = logging.getLogger("filament_stock")
router = APIRouter(tags=["sharing"])


def _filament_to_share_payload(fil: Filament, db: Session) -> dict:
    """Build a self-contained shareable payload for a filament."""
    colors = db.query(ColorStock).filter(ColorStock.filament_id == fil.id).all()
    return {
        "share_version": "1.0",
        "shared_at": datetime.now(timezone.utc).isoformat(),
        "filament": {
            "brand": fil.brand,
            "material": fil.material,
            "filament_type": fil.filament_type,
            "filament_id": fil.filament_id,
            "density": fil.density,
            "nozzle_temp_min": fil.nozzle_temp_min,
            "nozzle_temp_max": fil.nozzle_temp_max,
            "bed_temp": fil.bed_temp,
            "bed_temp_max": fil.bed_temp_max,
            "chamber_temp": fil.chamber_temp,
            "dry_temp": fil.dry_temp,
            "dry_time": fil.dry_time,
            "amazon_url": fil.amazon_url,
            "notes": fil.notes,
        },
        "colors": [
            {"color_name": c.color_name, "color_hex": c.color_hex}
            for c in colors
        ],
    }


@router.get("/filaments/{filament_id}/share")
def share_filament(filament_id: int, db: Session = Depends(get_db)):
    fil = db.query(Filament).filter(Filament.id == filament_id).first()
    if not fil:
        raise HTTPException(404, "Filament not found")
    payload = _filament_to_share_payload(fil, db)
    encoded = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode()
    ).decode()
    return {
        "payload": payload,
        "encoded": encoded,
    }


@router.get("/filaments/{filament_id}/share/qr")
def share_filament_qr(filament_id: int, db: Session = Depends(get_db)):
    """Return a QR code PNG containing the share payload."""
    fil = db.query(Filament).filter(Filament.id == filament_id).first()
    if not fil:
        raise HTTPException(404, "Filament not found")
    payload = _filament_to_share_payload(fil, db)
    data_str = json.dumps(payload, separators=(",", ":"))

    import qrcode

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=2,
    )
    qr.add_data(data_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    from fastapi.responses import StreamingResponse

    return StreamingResponse(buf, media_type="image/png")


@router.post("/filaments/import-shared")
def import_shared_filament(payload: dict = Body(...), db: Session = Depends(get_db)):
    """Import a shared filament profile into the local database."""
    if "encoded" in payload and "filament" not in payload:
        try:
            decoded = json.loads(base64.urlsafe_b64decode(payload["encoded"]))
            payload = decoded
        except Exception:
            raise HTTPException(400, "Invalid encoded payload")

    fil_data = payload.get("filament") or payload
    if not fil_data.get("brand") or not fil_data.get("material"):
        raise HTTPException(400, "Missing brand or material")

    existing = (
        db.query(Filament)
        .filter(Filament.brand == fil_data["brand"], Filament.material == fil_data["material"])
        .first()
    )
    if existing:
        raise HTTPException(
            409, f"Filament '{fil_data['brand']} {fil_data['material']}' already exists"
        )

    fil = Filament(
        brand=fil_data["brand"],
        material=fil_data["material"],
        filament_type=fil_data.get("filament_type", fil_data.get("material", "PLA")),
        filament_id=fil_data.get("filament_id"),
        density=fil_data.get("density"),
        nozzle_temp_min=fil_data.get("nozzle_temp_min"),
        nozzle_temp_max=fil_data.get("nozzle_temp_max"),
        bed_temp=fil_data.get("bed_temp"),
        bed_temp_max=fil_data.get("bed_temp_max"),
        chamber_temp=fil_data.get("chamber_temp"),
        dry_temp=fil_data.get("dry_temp"),
        dry_time=fil_data.get("dry_time"),
        amazon_url=fil_data.get("amazon_url", ""),
        notes=fil_data.get("notes", ""),
    )
    db.add(fil)
    db.flush()

    colors_added = 0
    for cd in payload.get("colors", []):
        cs = ColorStock(
            filament_id=fil.id,
            color_name=cd.get("color_name", "Unknown"),
            color_hex=cd.get("color_hex", "#808080"),
        )
        db.add(cs)
        colors_added += 1

    db.commit()
    return {"ok": True, "filament_id": fil.id, "colors_added": colors_added}
