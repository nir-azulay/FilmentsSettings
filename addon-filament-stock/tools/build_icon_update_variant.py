"""Bake a 'update available' badge onto icon.png.

Produces ``icon_update.png`` next to ``icon.png`` in the add-on root. The
add-on's runtime icon swapper copies one or the other over the live
``icon.png`` depending on whether Supervisor reports an update is available.

Why a pre-baked PNG instead of compositing at runtime?

* The badge needs to look identical on every install -- no font / Pillow
  version skew.
* Keeps the runtime swapper trivial: just ``shutil.copyfile``.
* The PR-review surface for the visual change lives in this script + the
  two PNGs committed to git, not in scattered runtime code.

Run from the repo root::

    python3 addon-filament-stock/tools/build_icon_update_variant.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "icon.png"
DST = REPO_ROOT / "icon_update.png"

# Badge geometry, all expressed as a fraction of the icon side length so this
# scales cleanly if we ever bump from 256x256. Bottom-right corner with a
# small inset; ~38% of the side length so the badge reads as "obviously an
# update indicator" even when HA renders the tile at ~64x64 in the Apps grid.
BADGE_FRAC = 0.46
INSET_FRAC = 0.02
# Home Assistant's "update available" orange. Matches the mdiArrowUpBoldCircle
# tint the frontend uses for the corner overlay on iconless add-ons -- so the
# baked badge feels native rather than rogue branding.
BADGE_FILL = (255, 152, 0, 255)
BADGE_STROKE = (255, 255, 255, 255)
ARROW_FILL = (255, 255, 255, 255)


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"icon source missing: {SRC}")

    base = Image.open(SRC).convert("RGBA")
    side = base.size[0]
    if base.size[0] != base.size[1]:
        raise SystemExit(f"icon.png must be square, got {base.size}")

    badge_size = int(side * BADGE_FRAC)
    inset = int(side * INSET_FRAC)
    # Bottom-right corner. (x0, y0, x1, y1) of the badge bounding box.
    x1 = side - inset
    y1 = side - inset
    x0 = x1 - badge_size
    y0 = y1 - badge_size

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    # White stroke ring first (slightly larger), then the orange disc on top,
    # so the badge stays readable against any spool color or transparency.
    stroke_w = max(2, badge_size // 14)
    draw.ellipse(
        (x0 - stroke_w, y0 - stroke_w, x1 + stroke_w, y1 + stroke_w),
        fill=BADGE_STROKE,
    )
    draw.ellipse((x0, y0, x1, y1), fill=BADGE_FILL)

    # Bold up-arrow inside the disc. Built from a polygon so we don't have to
    # ship a font with the repo.
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    r = badge_size / 2
    # Tip of the arrow ~70% of the way up from center.
    tip_y = cy - r * 0.55
    base_y = cy + r * 0.40
    shaft_half = r * 0.18
    head_half = r * 0.42
    head_y = cy - r * 0.05
    arrow = [
        (cx, tip_y),
        (cx + head_half, head_y),
        (cx + shaft_half, head_y),
        (cx + shaft_half, base_y),
        (cx - shaft_half, base_y),
        (cx - shaft_half, head_y),
        (cx - head_half, head_y),
    ]
    draw.polygon(arrow, fill=ARROW_FILL)

    out = Image.alpha_composite(base, overlay)
    out.save(DST, format="PNG", optimize=True)
    print(f"wrote {DST} ({DST.stat().st_size} bytes, {out.size[0]}x{out.size[1]} RGBA)")


if __name__ == "__main__":
    main()
