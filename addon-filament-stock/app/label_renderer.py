"""Generate printable label images for spool instances.

Target: Niimbot B21 Pro -- 300 DPI, 591px printhead width.
Label size: 50x30mm = 591x354 pixels at 300 DPI.
Black & white only (thermal printer).

Layout:
  +------------------------------------------------------+
  |  [QR]   SUNLU PETG HS                               |
  |  [QR]   Cold White                                   |
  |  [QR]   PLA  |  Nozzle 230-250°C  |  Bed 70°C       |
  |         Density: 1.24 g/cm³       SP-A1B2C3D4  SPOOL |
  +------------------------------------------------------+
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont
import qrcode
from qrcode.image.pil import PilImage

if TYPE_CHECKING:
    from .models import SpoolInstance

_log = logging.getLogger("filament_stock.label")

LABEL_W = 591
LABEL_H = 354
QR_SIZE = 150
MARGIN = 10
TEXT_LEFT = MARGIN + QR_SIZE + 12


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _get_font_regular(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _make_qr(data: str) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img: PilImage = qr.make_image(fill_color="black", back_color="white")
    return img.get_image().resize((QR_SIZE, QR_SIZE), Image.NEAREST)


def render_label(spool: SpoolInstance, ha_url: str | None = None) -> Image.Image:
    color = spool.color_stock
    filament = color.filament if color else None

    brand = filament.brand if filament else "?"
    material = filament.material if filament else "?"
    filament_type = filament.filament_type if filament else ""
    color_name = color.color_name if color else "?"
    nozzle_min = filament.nozzle_temp_min if filament else None
    nozzle_max = filament.nozzle_temp_max if filament else None
    bed_temp = filament.bed_temp if filament else None
    density = filament.density if filament else None

    if ha_url:
        qr_data = f"{ha_url.rstrip('/')}/filaments/#spool/{spool.uid}"
    else:
        qr_data = f"{brand} {material} - {color_name} [{spool.uid}]"

    img = Image.new("RGB", (LABEL_W, LABEL_H), "white")
    draw = ImageDraw.Draw(img)

    font_title = _get_font(36)
    font_color = _get_font(30)
    font_specs = _get_font_regular(20)
    font_uid = _get_font(18)
    font_small = _get_font_regular(16)

    # QR code -- vertically centered
    qr_img = _make_qr(qr_data)
    qr_y = (LABEL_H - QR_SIZE) // 2
    img.paste(qr_img, (MARGIN, qr_y))

    text_right = LABEL_W - MARGIN
    y = MARGIN + 4

    # Row 1: Brand + Material (large bold)
    draw.text((TEXT_LEFT, y), f"{brand} {material}", fill="black", font=font_title)
    y += 46

    # Row 2: Color name (large)
    draw.text((TEXT_LEFT, y), color_name, fill="black", font=font_color)
    y += 40

    # Row 3: Specs line (type | nozzle temp | bed temp)
    specs_parts: list[str] = []
    if filament_type:
        specs_parts.append(filament_type)
    if nozzle_min and nozzle_max:
        specs_parts.append(f"Nozzle {nozzle_min}-{nozzle_max}\u00b0C")
    elif nozzle_min or nozzle_max:
        specs_parts.append(f"Nozzle {nozzle_min or nozzle_max}\u00b0C")
    if bed_temp:
        specs_parts.append(f"Bed {bed_temp}\u00b0C")
    if specs_parts:
        draw.text((TEXT_LEFT, y), "  \u2502  ".join(specs_parts), fill="black", font=font_specs)
    y += 28

    # Row 4: Density
    if density:
        draw.text((TEXT_LEFT, y), f"Density: {density} g/cm\u00b3", fill="#333333", font=font_small)
    y += 24

    # Bottom row: UID on left, packaging on right
    bottom_y = LABEL_H - MARGIN - 24
    draw.text((TEXT_LEFT, bottom_y), spool.uid, fill="#666666", font=font_uid)

    pkg_label = spool.packaging.upper()
    pkg_w = draw.textlength(pkg_label, font=font_uid)
    draw.text((text_right - pkg_w, bottom_y), pkg_label, fill="#666666", font=font_uid)

    # Thin separator line above bottom row
    draw.line(
        [(TEXT_LEFT, bottom_y - 6), (text_right, bottom_y - 6)],
        fill="#cccccc", width=1,
    )

    return img
