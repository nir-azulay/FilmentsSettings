"""Generate printable label images for spool instances.

Target: Niimbot B21 Pro -- 300 DPI, 591px printhead width.
Label size: 50x30mm = 591x354 pixels at 300 DPI.

Layout:
  +------------------------------------------------------+
  |  [QR]   SUNLU PETG HS                               |
  |  [QR]   Cold White                  [color swatch]   |
  |  [QR]   Nozzle: 230-250°C                           |
  |         Bed: 70°C          SP-A1B2C3D4               |
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
QR_SIZE = 130
MARGIN = 12
TEXT_LEFT = MARGIN + QR_SIZE + 14
SWATCH_SIZE = 60


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
    color_name = color.color_name if color else "?"
    color_hex = color.color_hex if color else "#808080"
    nozzle_min = filament.nozzle_temp_min if filament else None
    nozzle_max = filament.nozzle_temp_max if filament else None
    bed_temp = filament.bed_temp if filament else None

    # QR code content
    if ha_url:
        qr_data = f"{ha_url.rstrip('/')}/filaments/#spool/{spool.uid}"
    else:
        qr_data = f"{brand} {material} - {color_name} [{spool.uid}]"

    img = Image.new("RGB", (LABEL_W, LABEL_H), "white")
    draw = ImageDraw.Draw(img)

    # Fonts
    font_brand = _get_font(28)
    font_material = _get_font(24)
    font_color = _get_font_regular(22)
    font_specs = _get_font_regular(18)
    font_uid = _get_font(16)

    # QR code
    qr_img = _make_qr(qr_data)
    qr_y = (LABEL_H - QR_SIZE) // 2
    img.paste(qr_img, (MARGIN, qr_y))

    # Color swatch (top-right)
    swatch_x = LABEL_W - MARGIN - SWATCH_SIZE
    swatch_y = MARGIN
    swatch_h = LABEL_H - 2 * MARGIN - 30
    draw.rounded_rectangle(
        [swatch_x, swatch_y, swatch_x + SWATCH_SIZE, swatch_y + swatch_h],
        radius=8,
        fill=color_hex,
        outline="#333333",
        width=2,
    )

    # Text area
    text_right = swatch_x - 10
    y = MARGIN + 8

    # Brand + Material
    draw.text((TEXT_LEFT, y), f"{brand} {material}", fill="black", font=font_brand)
    y += 38

    # Color name
    draw.text((TEXT_LEFT, y), color_name, fill="#555555", font=font_color)
    y += 32

    # Nozzle temp
    if nozzle_min and nozzle_max:
        temp_text = f"Nozzle: {nozzle_min}-{nozzle_max}\u00b0C"
    elif nozzle_min or nozzle_max:
        temp_text = f"Nozzle: {nozzle_min or nozzle_max}\u00b0C"
    else:
        temp_text = ""
    if temp_text:
        draw.text((TEXT_LEFT, y), temp_text, fill="#333333", font=font_specs)
        y += 26

    # Bed temp
    if bed_temp:
        draw.text((TEXT_LEFT, y), f"Bed: {bed_temp}\u00b0C", fill="#333333", font=font_specs)
        y += 26

    # UID (bottom area)
    uid_y = LABEL_H - MARGIN - 22
    draw.text((TEXT_LEFT, uid_y), spool.uid, fill="#999999", font=font_uid)

    # Packaging indicator (bottom-right)
    pkg_label = spool.packaging.upper()
    pkg_w = draw.textlength(pkg_label, font=font_uid)
    draw.text(
        (swatch_x + (SWATCH_SIZE - pkg_w) / 2, swatch_y + swatch_h + 6),
        pkg_label,
        fill="#666666",
        font=font_uid,
    )

    return img
