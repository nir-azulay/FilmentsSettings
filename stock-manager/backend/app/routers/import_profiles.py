import json
import os
import re
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Filament

router = APIRouter(tags=["import"])

PROFILES_ROOT = os.environ.get("PROFILES_ROOT", "/profiles")


@router.post("/import")
def import_profiles(db: Session = Depends(get_db)):
    """Scan profile JSONs and READMEs to import filament data."""
    root = Path(PROFILES_ROOT)
    if not root.exists():
        return {"imported": 0, "skipped": 0, "error": f"Profiles root not found: {root}"}

    imported = 0
    skipped = 0

    brand_dirs = [d for d in root.iterdir() if d.is_dir() and d.name not in ("DeployPack", ".cursor", ".git")]

    for brand_dir in brand_dirs:
        for material_dir in brand_dir.iterdir():
            if not material_dir.is_dir():
                continue

            base_profiles = list(material_dir.glob("my-*@Bambu Lab H2S 0.4 nozzle.json"))
            if not base_profiles:
                base_profiles = list(material_dir.glob("my-*@Bambu Lab H2S*.json"))

            if not base_profiles:
                continue

            profile_path = base_profiles[0]
            data = _load_json(profile_path)
            if not data:
                continue

            brand = _extract_str(data, "filament_vendor", brand_dir.name)
            material = _material_from_path(material_dir.name)
            filament_type = _extract_str(data, "filament_type", "")
            filament_id_val = data.get("filament_id", "")
            if isinstance(filament_id_val, list):
                filament_id_val = filament_id_val[0] if filament_id_val else ""

            existing = db.query(Filament).filter(Filament.filament_id == filament_id_val).first()
            if existing:
                skipped += 1
                continue

            density = _extract_float(data, "filament_density")
            nozzle_temps = _extract_int_pair(data, "nozzle_temperature")
            nozzle_range_low = _extract_int(data, "nozzle_temperature_range_low")
            nozzle_range_high = _extract_int(data, "nozzle_temperature_range_high")
            bed_temp = _extract_int(data, "hot_plate_temp")

            amazon_url = _extract_amazon_url(material_dir)

            filament = Filament(
                brand=brand,
                material=material,
                filament_type=filament_type,
                filament_id=filament_id_val,
                density=density,
                nozzle_temp_min=nozzle_range_low or (nozzle_temps[0] if nozzle_temps else None),
                nozzle_temp_max=nozzle_range_high or (nozzle_temps[1] if nozzle_temps else None),
                bed_temp=bed_temp,
                amazon_url=amazon_url,
                notes=f"Imported from {profile_path.name}",
            )
            db.add(filament)
            imported += 1

    db.commit()
    return {"imported": imported, "skipped": skipped}


def _load_json(path: Path) -> dict | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _extract_str(data: dict, key: str, default: str = "") -> str:
    val = data.get(key, default)
    if isinstance(val, list):
        return val[0] if val else default
    return str(val) if val else default


def _extract_float(data: dict, key: str) -> float | None:
    val = data.get(key)
    if isinstance(val, list):
        val = val[0] if val else None
    try:
        return float(val) if val else None
    except (ValueError, TypeError):
        return None


def _extract_int(data: dict, key: str) -> int | None:
    val = data.get(key)
    if isinstance(val, list):
        val = val[0] if val else None
    try:
        return int(val) if val else None
    except (ValueError, TypeError):
        return None


def _extract_int_pair(data: dict, key: str) -> tuple[int, int] | None:
    val = data.get(key)
    if isinstance(val, list) and len(val) >= 1:
        try:
            first = int(val[0])
            second = int(val[1]) if len(val) > 1 else first
            return (min(first, second), max(first, second))
        except (ValueError, TypeError):
            return None
    return None


def _material_from_path(folder_name: str) -> str:
    return folder_name.replace("-", " ")


def _extract_amazon_url(material_dir: Path) -> str:
    readme = material_dir / "README.md"
    if not readme.exists():
        return ""
    try:
        content = readme.read_text(encoding="utf-8")
        match = re.search(r"https?://(?:www\.)?amazon\.[^\s)]+", content)
        return match.group(0) if match else ""
    except OSError:
        return ""
