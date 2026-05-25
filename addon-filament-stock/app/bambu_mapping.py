"""Map our local Filament / ColorStock rows to the payload shape that
``bambu_lab.set_filament`` expects on the printer side.

Bambu's printer firmware identifies filaments by a short ``tray_info_idx``
code (e.g. ``GFL99`` = Generic PLA Silk, ``GFG99`` = Generic PETG). When we
push an assignment to the printer we send a Bambu-recognised generic ID so
the AMS display shows a known filament family -- the link back to our
specific brand stays in the local DB via the TrayAssignment row.

The mapping is deliberately small and conservative:

  * Material families we actually stock get a real GF code.
  * Anything unrecognised falls back to ``GFL99`` (Generic PLA) plus tray
    type "PLA" -- safe because Bambu treats it as a generic spool and won't
    refuse to print, the user just gets a different display label.

Extend ``_FAMILY_RULES`` below as you add new material families.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BambuFamily:
    """The minimum set of fields ``bambu_lab.set_filament`` needs."""

    tray_info_idx: str  # e.g. "GFL99"
    tray_type: str  # e.g. "PLA" / "PETG" / "ASA" / "PA" / "TPU"
    label: str  # human description, used in UI tooltips


# Generic Bambu filament IDs taken from the Bambu Studio filament library.
# We deliberately pick the *generic* variants (not the branded "Bambu PLA Basic"
# IDs) so the printer treats the spool as a generic filament with our
# user-supplied min/max temps rather than insisting on Bambu's curated profile.
_GENERIC_PLA = BambuFamily("GFL99", "PLA", "Generic PLA")
_GENERIC_PETG = BambuFamily("GFG99", "PETG", "Generic PETG")
_GENERIC_ASA = BambuFamily("GFB99", "ASA", "Generic ASA")
_GENERIC_PA = BambuFamily("GFN99", "PA", "Generic PA")
_GENERIC_TPU = BambuFamily("GFU99", "TPU", "Generic TPU")
_GENERIC_ABS = BambuFamily("GFB98", "ABS", "Generic ABS")
_GENERIC_PC = BambuFamily("GFC99", "PC", "Generic PC")


# Substring-based family rules. First match wins. Substrings are matched
# case-insensitively against the lowercase concatenation of
# ``f"{filament_type} {material}"`` -- e.g. "petg petg hs", "pla pla matte".
_FAMILY_RULES: tuple[tuple[str, BambuFamily], ...] = (
    # Order matters: check the more specific multi-word variants first.
    ("petg", _GENERIC_PETG),  # covers "PETG", "PETG HS", "PETG Pro"
    ("asa", _GENERIC_ASA),
    ("tpu", _GENERIC_TPU),
    # Nylon family -- match "pa" as a word boundary token to avoid catching
    # "para" or other coincidences. We rely on the leading space we built
    # in below.
    (" pa ", _GENERIC_PA),
    ("nylon", _GENERIC_PA),
    ("abs", _GENERIC_ABS),
    (" pc ", _GENERIC_PC),
    # PLA last because "pla" is a substring of many things (e.g. "Plain").
    # The combined string we test is "<type> <material>" -- both sides
    # already start with the family keyword in our data, so this is fine.
    ("pla", _GENERIC_PLA),
)


def family_for(filament_type: str | None, material: str | None) -> BambuFamily:
    """Pick the closest generic Bambu family for one of our filaments.

    Always returns a family -- the fallback is Generic PLA so the
    push-to-printer flow is never silently skipped.
    """
    haystack = f" {(filament_type or '').strip().lower()} {(material or '').strip().lower()} "
    for needle, fam in _FAMILY_RULES:
        if needle in haystack:
            return fam
    return _GENERIC_PLA


def color_to_bambu_rgba(color_hex: str | None) -> str:
    """Convert ``#RRGGBB`` (our DB format) to ``RRGGBBFF`` (what Bambu wants).

    Bambu's ``tray_color`` is RGBA with no leading ``#``. We always send a
    fully-opaque color (``FF`` alpha) because the AMS display only ever shows
    solid swatches. Falls back to gray (``808080FF``) on any input we can't
    parse so the service call never fails on a bad hex.
    """
    if not color_hex:
        return "808080FF"
    s = color_hex.strip().lstrip("#")
    # Accept #RRGGBB or already-RRGGBBAA; normalise to RRGGBB then add FF alpha.
    if len(s) >= 6 and all(c in "0123456789abcdefABCDEF" for c in s[:6]):
        return s[:6].upper() + "FF"
    return "808080FF"


# Bambu firmware accepts nozzle temperatures only in 160..300. If our local
# filament has values outside that window (e.g. unset / 0 / a wildly high
# experimental value) we clamp to keep the service call from failing.
_NOZZLE_MIN_BOUND = 160
_NOZZLE_MAX_BOUND = 300
# Conservative defaults when the filament row has no nozzle temps at all.
_DEFAULT_NOZZLE_MIN = 200
_DEFAULT_NOZZLE_MAX = 240


def clamp_nozzle_temps(min_temp: int | None, max_temp: int | None) -> tuple[int, int]:
    """Return ``(min, max)`` clamped to Bambu's accepted 160..300 range and
    guaranteed ``min <= max``. Used directly as ``nozzle_temp_min`` /
    ``nozzle_temp_max`` arguments to ``bambu_lab.set_filament``.
    """
    lo = min_temp if isinstance(min_temp, int) else _DEFAULT_NOZZLE_MIN
    hi = max_temp if isinstance(max_temp, int) else _DEFAULT_NOZZLE_MAX
    lo = max(_NOZZLE_MIN_BOUND, min(_NOZZLE_MAX_BOUND, lo))
    hi = max(_NOZZLE_MIN_BOUND, min(_NOZZLE_MAX_BOUND, hi))
    if lo > hi:
        lo, hi = hi, lo
    return lo, hi
