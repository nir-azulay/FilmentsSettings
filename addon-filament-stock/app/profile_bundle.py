"""BambuStudio profile bundle lookup.

The add-on image bakes deployment-ready BambuStudio profiles into
`/app/profiles/` at build time (see Dockerfile). Each filament in the DB is
matched to its bundle by exact `"<brand> <material>"` prefix, e.g. a row with
brand="SUNLU" material="PETG HS" matches files starting with `"SUNLU PETG HS "`
or `"SUNLU PETG HS@"` -- never `"SUNLU PETG "` (a different product).

Each bundle for a Bambu Lab H2S filament typically contains 12 files:

  - 4 process JSONs (per nozzle size): `<product> 0.NNmm @H2S 0.X nozzle.json`
  - 4 matching `.info` sidecars
  - 1 base filament JSON: `<product> @Bambu Lab H2S.json` (one file lists all
    nozzle sizes in compatible_printers)
  - 1 matching `.info` sidecar
  - 1 user preset JSON: `<product> @Bambu Lab H2S.preset.json`
  - 1 matching `.info` sidecar

(TPU 95A is a 10-file exception -- no 0.2mm nozzle.)
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

# Resolved relative to this file so it works both inside the container
# (/app/app/profile_bundle.py + /app/profiles/) and during local dev.
PROFILES_ROOT = Path(__file__).resolve().parent.parent / "profiles"

_NOZZLE_RE = re.compile(r"\s(0\.[0-9]+)mm @H2S (0\.[0-9]+) nozzle\.json$")
_BASE_SUFFIX = " @Bambu Lab H2S.json"
_PRESET_SUFFIX = " @Bambu Lab H2S.preset.json"


@dataclass
class NozzleEntry:
    """One process preset file (per nozzle size)."""
    layer_height_mm: str  # "0.10" / "0.20" / "0.30" / "0.40"
    nozzle_mm: str        # "0.2" / "0.4" / "0.6" / "0.8"
    file_name: str        # bare filename, e.g. "SUNLU PETG HS 0.20mm @H2S 0.4 nozzle.json"
    info_file: str | None  # matching .info sidecar if present


@dataclass
class ProfileBundle:
    """All files bundled for one filament product."""
    product: str          # exact prefix used to match, e.g. "SUNLU PETG HS"
    files: list[str]      # all bundled file names (sorted)
    base_file: str | None    # "<product> @Bambu Lab H2S.json", if present
    base_info: str | None
    preset_file: str | None  # "<product> @Bambu Lab H2S.preset.json", if present
    preset_info: str | None
    nozzles: list[NozzleEntry]  # one per nozzle size present
    # Pulled out of base_file for quick display in the UI.
    summary: dict


def bundle_for(brand: str, material: str) -> ProfileBundle | None:
    """Return the bundle for `<brand> <material>` or None if nothing matches.

    `product` must be an exact match against a product whose base profile
    (`<product> @Bambu Lab H2S.json`) exists on disk. Two products that share
    a prefix (e.g. "SUNLU PETG" and "SUNLU PETG HS") are kept apart this way.
    """
    if not PROFILES_ROOT.is_dir():
        return None
    product = f"{(brand or '').strip()} {(material or '').strip()}".strip()
    if not product:
        return None

    known = set(all_bundled_products())
    if product not in known:
        return None

    files = sorted(_files_for_product(product, known))
    if not files:
        return None

    base_file = _exact_one(files, f"{product}{_BASE_SUFFIX}")
    preset_file = _exact_one(files, f"{product}{_PRESET_SUFFIX}")
    base_info = _exact_one(files, f"{product} @Bambu Lab H2S.info") if base_file else None
    preset_info = _exact_one(files, f"{product} @Bambu Lab H2S.preset.info") if preset_file else None

    nozzles: list[NozzleEntry] = []
    nozzle_prefix = f"{product} "
    for name in files:
        if not name.startswith(nozzle_prefix):
            continue
        m = _NOZZLE_RE.search(name)
        if not m:
            continue
        nozzles.append(
            NozzleEntry(
                layer_height_mm=m.group(1),
                nozzle_mm=m.group(2),
                file_name=name,
                info_file=_exact_one(files, name[:-5] + ".info"),
            )
        )
    nozzles.sort(key=lambda n: float(n.nozzle_mm))

    summary = _summarize_base(PROFILES_ROOT / base_file) if base_file else {}

    return ProfileBundle(
        product=product,
        files=files,
        base_file=base_file,
        base_info=base_info,
        preset_file=preset_file,
        preset_info=preset_info,
        nozzles=nozzles,
        summary=summary,
    )


def file_path(brand: str, material: str, name: str) -> Path | None:
    """Validated path lookup for a single file download.

    Refuses anything that isn't part of the bundle (prevents `../` escapes and
    cross-product downloads via a guessed filename).
    """
    bundle = bundle_for(brand, material)
    if not bundle or name not in bundle.files:
        return None
    p = PROFILES_ROOT / name
    # Resolve and re-check that we did not escape PROFILES_ROOT.
    try:
        rp = p.resolve(strict=True)
        if PROFILES_ROOT.resolve() not in rp.parents:
            return None
    except (FileNotFoundError, RuntimeError):
        return None
    return p


def all_bundled_products() -> list[str]:
    """Diagnostic: list of all distinct product prefixes present on disk."""
    if not PROFILES_ROOT.is_dir():
        return []
    seen: set[str] = set()
    for name in os.listdir(PROFILES_ROOT):
        if name.endswith(_BASE_SUFFIX):
            seen.add(name[: -len(_BASE_SUFFIX)])
    return sorted(seen)


# ---------------------------------------------------------------------------
# internals
# ---------------------------------------------------------------------------


def _files_for_product(product: str, known_products: set[str]) -> Iterable[str]:
    """Yield filenames belonging to exactly this product.

    `"SUNLU PETG"` must NOT pick up `"SUNLU PETG HS ..."` files. We compute
    the "claimed" product for each filename as the longest known product that
    prefixes it -- only files whose claimed product equals `product` belong
    to this bundle.
    """
    # Longest-first so we always match the most specific product.
    by_length = sorted(known_products, key=len, reverse=True)
    for name in os.listdir(PROFILES_ROOT):
        for candidate in by_length:
            if name.startswith(candidate):
                # Boundary check still required so e.g. "SUNLU PLA" wouldn't
                # match a hypothetical "SUNLU PLAUSIBLE" with no separator.
                tail = name[len(candidate):]
                if tail and tail[0] in (" ", "@", "."):
                    if candidate == product:
                        yield name
                    break


def _exact_one(files: list[str], wanted: str) -> str | None:
    return wanted if wanted in files else None


# Fields we surface from the base filament JSON so the UI doesn't have to.
# Each Bambu base profile stores values as one- or two-element string arrays
# (Standard extruder, optional High Flow extruder); we keep them as-is.
_SUMMARY_FIELDS = (
    "filament_density",
    "filament_diameter",
    "nozzle_temperature",
    "nozzle_temperature_initial_layer",
    "hot_plate_temp",
    "textured_plate_temp",
    "eng_plate_temp",
    "filament_max_volumetric_speed",
    "filament_retraction_length",
    "filament_retraction_speed",
    "filament_deretraction_speed",
    "temperature_vitrification",
    "filament_extruder_variant",
    "compatible_printers",
)


def _summarize_base(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}
    return {key: data[key] for key in _SUMMARY_FIELDS if key in data}
