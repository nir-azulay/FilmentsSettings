"""Low-stock alerts only for staple materials and black/white colors."""

from .color_merge import normalize_color_name
from .models import ColorStock, Filament

MONITORED_FILAMENT_TYPES = frozenset({"PLA", "PETG", "ASA"})

MONITORED_COLOR_KEYS = frozenset({"black", "white"})


def is_monitored_filament_type(filament_type: str) -> bool:
    return (filament_type or "").strip().upper() in MONITORED_FILAMENT_TYPES


def is_monitored_color_name(color_name: str) -> bool:
    return normalize_color_name(color_name) in MONITORED_COLOR_KEYS


def color_available_qty(color: ColorStock) -> int:
    if (color.status or "in_stock") != "in_stock":
        return 0
    return max(0, (color.quantity or 0) - (color.quantity_used or 0))


def iter_low_stock_colors(filament: Filament):
    if not is_monitored_filament_type(filament.filament_type):
        return
    threshold = filament.low_stock_threshold or 1
    for color in filament.colors:
        if not is_monitored_color_name(color.color_name):
            continue
        avail = color_available_qty(color)
        if avail <= threshold:
            yield color, avail, threshold
