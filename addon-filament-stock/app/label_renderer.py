"""Generate printable label images for spool instances.

Target: Niimbot B21 Pro -- 300 DPI, 591px printhead width.
Label size: 50x30mm = 591x354 pixels at 300 DPI.
Black & white only (thermal printer).

Layout (QR on right):
  +------------------------------------------------------+
  |  PETG                                         [QR]   |
  |  SUNLU PETG HS                                [QR]   |
  |  Cold White                                   [QR]   |
  |  Nozzle: 230-250°C   Bed: 70-90°C                   |
  |  Chamber: 50°C   Density: 1.24 g/cm³               |
  |  ────────────────────────────────────────────        |
  |  SP-A1B2C3D4                           SPOOL         |
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
    bed_temp_max = filament.bed_temp_max if filament else None
    chamber_temp = filament.chamber_temp if filament else None
    density = filament.density if filament else None

    if ha_url:
        qr_data = f"{ha_url.rstrip('/')}/filaments/#spool/{spool.uid}"
    else:
        qr_data = f"{brand} {material} - {color_name} [{spool.uid}]"

    img = Image.new("RGB", (LABEL_W, LABEL_H), "white")
    draw = ImageDraw.Draw(img)

    font_type = _get_font(34)
    font_title = _get_font(30)
    font_color = _get_font(26)
    font_specs = _get_font_regular(20)
    font_uid = _get_font(16)
    font_small = _get_font_regular(17)

    # QR code -- right side, vertically centered
    qr_img = _make_qr(qr_data)
    qr_x = LABEL_W - MARGIN - QR_SIZE
    qr_y = (LABEL_H - QR_SIZE) // 2
    img.paste(qr_img, (qr_x, qr_y))

    text_left = MARGIN + 4
    text_right = qr_x - 12
    y = MARGIN

    # Row 1: Filament type (big bold, e.g. "PETG")
    if filament_type:
        draw.text((text_left, y), filament_type, fill="black", font=font_type)
        y += 40

    # Row 2: Brand + Material
    draw.text((text_left, y), f"{brand} {material}", fill="black", font=font_title)
    y += 36

    # Row 3: Color name
    draw.text((text_left, y), color_name, fill="black", font=font_color)
    y += 34

    # Row 4: Nozzle + Bed temperature on same line
    row4_parts: list[str] = []
    if nozzle_min and nozzle_max:
        row4_parts.append(f"Nozzle: {nozzle_min}-{nozzle_max}\u00b0C")
    elif nozzle_min or nozzle_max:
        row4_parts.append(f"Nozzle: {nozzle_min or nozzle_max}\u00b0C")
    if bed_temp and bed_temp_max and bed_temp != bed_temp_max:
        row4_parts.append(f"Bed: {bed_temp}-{bed_temp_max}\u00b0C")
    elif bed_temp:
        row4_parts.append(f"Bed: {bed_temp}\u00b0C")
    if row4_parts:
        draw.text((text_left, y), "   ".join(row4_parts), fill="black", font=font_specs)
    y += 24

    # Row 5: Chamber temperature + density on same line
    row5_parts: list[str] = []
    if chamber_temp:
        row5_parts.append(f"Chamber: {chamber_temp}\u00b0C")
    if density:
        row5_parts.append(f"Density: {density} g/cm\u00b3")
    if row5_parts:
        draw.text((text_left, y), "   ".join(row5_parts), fill="black", font=font_specs)
    y += 24

    # Thin separator line
    sep_y = LABEL_H - MARGIN - 28
    draw.line([(text_left, sep_y), (text_right, sep_y)], fill="#aaaaaa", width=1)

    # Bottom row: UID on left, packaging on right
    bottom_y = LABEL_H - MARGIN - 22
    draw.text((text_left, bottom_y), spool.uid, fill="#555555", font=font_uid)

    pkg_label = spool.packaging.upper()
    pkg_w = draw.textlength(pkg_label, font=font_uid)
    draw.text((text_right - pkg_w, bottom_y), pkg_label, fill="#555555", font=font_uid)

    return img
