"""Auto-populate filament DB fields from bundled BambuStudio profiles.

Runs on every startup. For each filament in the database that has a matching
bundled profile, reads the base profile JSON and fills in any NULL fields
(nozzle temps, bed temps, density). Never overwrites user-set values.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Filament
from .profile_bundle import PROFILES_ROOT, bundle_for

_log = logging.getLogger("filament_stock.profile_sync")


def _int_from_profile(value) -> int | None:
    """Extract an integer from a BambuStudio profile field value.
    Values are stored as string arrays like ["270", "270"]."""
    if isinstance(value, list) and value:
        try:
            return int(value[0])
        except (ValueError, TypeError):
            return None
    if isinstance(value, str):
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    return None


def _float_from_profile(value) -> float | None:
    if isinstance(value, list) and value:
        try:
            return float(value[0])
        except (ValueError, TypeError):
            return None
    if isinstance(value, str):
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    return None


def _read_base_profile(path: Path) -> dict | None:
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        _log.warning("Failed to read profile %s: %s", path, exc)
        return None


def sync_filaments_from_profiles() -> int:
    """Fill missing filament fields from bundled profiles. Returns count updated."""
    if not PROFILES_ROOT.is_dir():
        _log.info("No profiles directory found, skipping sync")
        return 0

    db: Session = SessionLocal()
    updated = 0
    try:
        for filament in db.query(Filament).all():
            bundle = bundle_for(filament.brand, filament.material)
            if not bundle or not bundle.base_file:
                continue

            base_path = PROFILES_ROOT / bundle.base_file
            data = _read_base_profile(base_path)
            if not data:
                continue

            changed = False

            nozzle_low = _int_from_profile(data.get("nozzle_temperature_range_low"))
            nozzle_high = _int_from_profile(data.get("nozzle_temperature_range_high"))
            nozzle_default = _int_from_profile(data.get("nozzle_temperature"))
            if filament.nozzle_temp_min is None:
                filament.nozzle_temp_min = nozzle_low or nozzle_default
                if filament.nozzle_temp_min is not None:
                    changed = True
            if filament.nozzle_temp_max is None:
                filament.nozzle_temp_max = nozzle_high or nozzle_default
                if filament.nozzle_temp_max is not None:
                    changed = True

            # Bed temp: take the max across all plate types for the range
            hot = _int_from_profile(data.get("hot_plate_temp"))
            textured = _int_from_profile(data.get("textured_plate_temp"))
            eng = _int_from_profile(data.get("eng_plate_temp"))
            plate_temps = [t for t in (hot, textured, eng) if t is not None]

            if plate_temps:
                bed_min = min(plate_temps)
                bed_max = max(plate_temps)
                if filament.bed_temp is None:
                    filament.bed_temp = bed_min
                    changed = True
                if filament.bed_temp_max is None and bed_max > bed_min:
                    filament.bed_temp_max = bed_max
                    changed = True
                elif filament.bed_temp_max is None:
                    filament.bed_temp_max = bed_max
                    changed = True

            density = _float_from_profile(data.get("filament_density"))
            if filament.density is None and density is not None:
                filament.density = density
                changed = True

            if changed:
                updated += 1
                _log.info(
                    "Auto-filled %s %s: nozzle=%s/%s bed=%s/%s density=%s",
                    filament.brand, filament.material,
                    filament.nozzle_temp_min, filament.nozzle_temp_max,
                    filament.bed_temp, filament.bed_temp_max,
                    filament.density,
                )

        if updated:
            db.commit()
        _log.info("Profile sync: updated %d filament(s)", updated)
    except Exception:
        db.rollback()
        _log.exception("Profile sync failed")
    finally:
        db.close()

    return updated
