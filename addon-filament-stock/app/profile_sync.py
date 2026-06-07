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


from dataclasses import dataclass, field


@dataclass
class _GenericDefaults:
    nozzle_temp_min: int | None = None
    nozzle_temp_max: int | None = None
    bed_temp: int | None = None
    bed_temp_max: int | None = None
    chamber_temp: int | None = None
    density: float | None = None
    dry_temp: int | None = None
    dry_time: int | None = None


# Generic defaults by material-type keyword (matched case-insensitively,
# first match wins).  Values mirror the Bambu Studio Generic profiles for
# each material family on the H2S.
_GENERIC_DEFAULTS: list[tuple[str, _GenericDefaults]] = [
    # More-specific variants first so "PETG HS" doesn't match just "PLA".
    ("ASA",   _GenericDefaults(240, 270,  90, 100, 60, 1.07, 65,  8)),
    ("ABS",   _GenericDefaults(230, 270,  80, 110, 60, 1.05, 80,  6)),
    ("PC",    _GenericDefaults(260, 300, 100, 120, 70, 1.20, 80,  8)),
    ("PA",    _GenericDefaults(250, 280,  50,  80, 60, 1.15, 80, 12)),  # Nylon
    ("PETG",  _GenericDefaults(230, 260,  70,  85,  None, 1.27, 65,  8)),
    ("TPU",   _GenericDefaults(210, 240,  35,  45,  None, 1.22, 65,  8)),
    ("TPE",   _GenericDefaults(210, 240,  35,  45,  None, 1.22, 65,  8)),
    ("PLA",   _GenericDefaults(190, 230,  35,  65,  None, 1.24, 65,  6)),
]


def _generic_defaults_for(filament_type: str | None) -> _GenericDefaults | None:
    if not filament_type:
        return None
    upper = filament_type.strip().upper()
    for keyword, defaults in _GENERIC_DEFAULTS:
        if keyword in upper:
            return defaults
    return None


def _chamber_temp_for_type(filament_type: str | None) -> int | None:
    d = _generic_defaults_for(filament_type)
    return d.chamber_temp if d else None


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

            # Bed temp: collect all plate types, exclude 0 (= "not recommended
            # for this plate" in BambuStudio), then take min/max of the range.
            plate_raw = (
                _int_from_profile(data.get("cool_plate_temp")),
                _int_from_profile(data.get("hot_plate_temp")),
                _int_from_profile(data.get("textured_plate_temp")),
                _int_from_profile(data.get("eng_plate_temp")),
                _int_from_profile(data.get("supertack_plate_temp")),
            )
            plate_temps = [t for t in plate_raw if t is not None and t > 0]

            if plate_temps:
                bed_min = min(plate_temps)
                bed_max = max(plate_temps)
                if filament.bed_temp is None:
                    filament.bed_temp = bed_min
                    changed = True
                if filament.bed_temp_max is None:
                    filament.bed_temp_max = bed_max
                    changed = True

            density = _float_from_profile(data.get("filament_density"))
            if filament.density is None and density is not None:
                filament.density = density
                changed = True

            # Chamber temp: not stored in filament profiles (always 0); derive
            # from the material family instead.
            if filament.chamber_temp is None:
                chamber = _chamber_temp_for_type(filament.filament_type)
                if chamber is not None:
                    filament.chamber_temp = chamber
                    changed = True

            dry_temp = _int_from_profile(data.get("filament_dev_ams_drying_temperature"))
            if filament.dry_temp is None and dry_temp is not None:
                filament.dry_temp = dry_temp
                changed = True

            dry_time = _int_from_profile(data.get("filament_dev_ams_drying_time"))
            if filament.dry_time is None and dry_time is not None:
                filament.dry_time = dry_time
                changed = True

            if changed:
                updated += 1
                _log.info(
                    "Auto-filled %s %s: nozzle=%s/%s bed=%s/%s density=%s dry=%s°C/%sh",
                    filament.brand, filament.material,
                    filament.nozzle_temp_min, filament.nozzle_temp_max,
                    filament.bed_temp, filament.bed_temp_max,
                    filament.density, filament.dry_temp, filament.dry_time,
                )

        # Second pass: filaments with no bundled profile — fill from generic
        # material-type defaults so they still get useful values on the label.
        for filament in db.query(Filament).all():
            bundle = bundle_for(filament.brand, filament.material)
            if bundle:
                continue  # already handled above

            defaults = _generic_defaults_for(filament.filament_type)
            if not defaults:
                continue

            changed = False
            for attr in (
                "nozzle_temp_min", "nozzle_temp_max",
                "bed_temp", "bed_temp_max",
                "chamber_temp", "density",
                "dry_temp", "dry_time",
            ):
                if getattr(filament, attr) is None:
                    val = getattr(defaults, attr)
                    if val is not None:
                        setattr(filament, attr, val)
                        changed = True

            if changed:
                updated += 1
                _log.info(
                    "Generic-filled %s %s (%s): nozzle=%s/%s bed=%s/%s "
                    "chamber=%s density=%s dry=%s°C/%sh",
                    filament.brand, filament.material, filament.filament_type,
                    filament.nozzle_temp_min, filament.nozzle_temp_max,
                    filament.bed_temp, filament.bed_temp_max,
                    filament.chamber_temp, filament.density,
                    filament.dry_temp, filament.dry_time,
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
