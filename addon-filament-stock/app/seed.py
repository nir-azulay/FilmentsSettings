"""Idempotent seed data — adds filaments + colors if they don't already exist."""

import logging

from .addon_options import get_options
from .database import SessionLocal
from .models import ColorStock, Filament

_log = logging.getLogger("filament_stock.seed")

SEED_FILAMENTS = [
    {
        "filament": {
            "brand": "Jayo",
            "material": "PLA Pro Cold White",
            "filament_type": "PLA",
            "brand_logo_url": "/logos/logo-jayo.png",
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
            "brand_logo_url": "/logos/logo-isanmate.png",
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
    {
        "filament": {
            "brand": "YS Filament",
            "material": "ABS",
            "filament_type": "ABS",
            "nozzle_temp_min": 220,
            "nozzle_temp_max": 260,
            "bed_temp": 80,
            "bed_temp_max": 110,
            "chamber_temp": 60,
            "density": 1.04,
            "amazon_url": "https://a.co/d/02OrrAfC",
        },
        "colors": [
            {"color_name": "Black", "color_hex": "#1A1A1A", "quantity": 3},
        ],
    },
]


def _run_seed(*, log_prefix: str = "Seed") -> dict[str, int]:
    """Insert any missing rows from SEED_FILAMENTS. Returns counters.

    Caller is responsible for deciding whether to run at all (the auto
    startup call respects the user's add-on option; the on-demand
    endpoint always runs).
    """
    added = 0
    skipped = 0
    updated_logos = 0
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
                if info.get("brand_logo_url") and existing.brand_logo_url != info["brand_logo_url"]:
                    existing.brand_logo_url = info["brand_logo_url"]
                    db.commit()
                    updated_logos += 1
                    _log.info("%s updated logo: %s %s", log_prefix, info["brand"], info["material"])
                else:
                    skipped += 1
                    _log.info("%s skip (exists): %s %s", log_prefix, info["brand"], info["material"])
                continue

            filament = Filament(**info)
            db.add(filament)
            db.flush()

            for c in entry["colors"]:
                color = ColorStock(filament_id=filament.id, **c)
                db.add(color)

            db.commit()
            added += 1
            _log.info(
                "%s added: %s %s with %d color(s)",
                log_prefix, info["brand"], info["material"], len(entry["colors"]),
            )
    except Exception:
        db.rollback()
        _log.exception("%s failed", log_prefix)
    finally:
        db.close()
    return {"added": added, "skipped_existing": skipped, "updated_logos": updated_logos}


def seed_filaments() -> None:
    """Startup seed -- respects the user's add-on preference."""
    if not get_options().seed_demo_filaments_on_first_run:
        _log.info(
            "Skipping demo-filament seeding because"
            " 'seed_demo_filaments_on_first_run' is disabled in add-on options."
        )
        return
    _run_seed(log_prefix="Seed")


def seed_filaments_force() -> dict[str, int]:
    """On-demand seed -- bypasses the user's preference.

    Reachable via POST /api/seed-now and meant for the empty-state UI's
    "Try our sample list" button. Returns the {added, skipped_existing,
    updated_logos} counters so the UI can show a toast like
    "Added 4 sample filaments." even when some rows already existed.
    """
    return _run_seed(log_prefix="Seed (on-demand)")
