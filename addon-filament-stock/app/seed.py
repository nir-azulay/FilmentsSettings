"""Idempotent seed data — adds filaments + colors if they don't already exist."""

import logging

from .database import SessionLocal
from .models import ColorStock, Filament

_log = logging.getLogger("filament_stock.seed")

SEED_FILAMENTS = [
    {
        "filament": {
            "brand": "Jayo",
            "material": "PLA Pro Cold White",
            "filament_type": "PLA",
        },
        "colors": [
            {"color_name": "Cold White", "color_hex": "#F5F5F0", "quantity": 2},
        ],
    },
    {
        "filament": {
            "brand": "Isanmate",
            "material": "PLA Pro",
            "filament_type": "PLA",
        },
        "colors": [
            {"color_name": "Black", "color_hex": "#1A1A1A", "quantity": 2},
        ],
    },
    {
        "filament": {
            "brand": "Inslogic",
            "material": "ABS-GF",
            "filament_type": "ABS",
        },
        "colors": [
            {"color_name": "White", "color_hex": "#FFFFFF", "quantity": 1},
        ],
    },
]


def seed_filaments() -> None:
    db = SessionLocal()
    try:
        for entry in SEED_FILAMENTS:
            info = entry["filament"]
            existing = (
                db.query(Filament)
                .filter(Filament.brand == info["brand"], Filament.material == info["material"])
                .first()
            )
            if existing:
                _log.info("Seed skip (exists): %s %s", info["brand"], info["material"])
                continue

            filament = Filament(**info)
            db.add(filament)
            db.flush()

            for c in entry["colors"]:
                color = ColorStock(filament_id=filament.id, **c)
                db.add(color)

            db.commit()
            _log.info("Seed added: %s %s with %d color(s)", info["brand"], info["material"], len(entry["colors"]))
    except Exception:
        db.rollback()
        _log.exception("Seed failed")
    finally:
        db.close()
