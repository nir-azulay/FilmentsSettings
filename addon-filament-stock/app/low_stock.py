"""Low-stock alerts only for staple materials and black/white colors."""

from collections import defaultdict

from .color_merge import normalize_color_name
from .models import ColorStock, Filament

MONITORED_FILAMENT_TYPES = frozenset({"PLA", "PETG", "ASA"})

MONITORED_COLOR_KEYS = frozenset({"black", "white"})


def is_monitored_filament_type(filament_type: str) -> bool:
    return (filament_type or "").strip().upper() in MONITORED_FILAMENT_TYPES


def is_monitored_color_name(color_name: str) -> bool:
    return normalize_color_name(color_name) in MONITORED_COLOR_KEYS


def color_available_qty(color: ColorStock) -> int:
    """Total available units for a color: spools left + refills left.

    Refills count toward stock-on-hand just like spools do for the purposes of
    "do I have material to print with" checks.
    """
    if (color.status or "in_stock") != "in_stock":
        return 0
    spool_left = max(0, (color.quantity or 0) - (color.quantity_used or 0))
    refill_left = max(0, (getattr(color, "quantity_refill", 0) or 0) - (getattr(color, "used_refill", 0) or 0))
    return spool_left + refill_left


def staple_pool_key(filament_type: str, color_name: str) -> tuple[str, str]:
    return (filament_type.strip().upper(), normalize_color_name(color_name))


def build_staple_pools(filaments: list[Filament]) -> dict[tuple[str, str], int]:
    """Total available black/white spools per material type (PLA/PETG/ASA), all brands."""
    pools: dict[tuple[str, str], int] = defaultdict(int)
    for filament in filaments:
        if not is_monitored_filament_type(filament.filament_type):
            continue
        for color in filament.colors:
            if not is_monitored_color_name(color.color_name):
                continue
            key = staple_pool_key(filament.filament_type, color.color_name)
            pools[key] += color_available_qty(color)
    return dict(pools)


def load_ignored_staple_keys(ignored_rows: list) -> set[tuple[str, str]]:
    return {(row.filament_type.strip().upper(), row.color_key) for row in ignored_rows}


def iter_low_stock_colors(
    filament: Filament,
    pools: dict[tuple[str, str], int] | None = None,
    ignored: set[tuple[str, str]] | None = None,
):
    if not is_monitored_filament_type(filament.filament_type):
        return
    threshold = filament.low_stock_threshold or 1
    for color in filament.colors:
        if not is_monitored_color_name(color.color_name):
            continue
        avail = color_available_qty(color)
        if avail > threshold:
            continue
        key = staple_pool_key(filament.filament_type, color.color_name)
        if ignored and key in ignored:
            continue
        if pools is not None and pools.get(key, 0) > threshold:
            # Same material + color stocked under another brand (e.g. SUNLU PETG vs Inslogic PETG Pro)
            continue
        yield color, avail, threshold
