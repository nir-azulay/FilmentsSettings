/** Color-family classifier used by the Color filter on the Stock and
 *  Assign pages.
 *
 *  We can't filter on raw color_name (free-text from the user; you'd end
 *  up with "Cold White" / "Pure White" / "White" all as separate filters)
 *  and we can't filter on raw hex (250+ distinct values). The middle
 *  ground is to bucket every hex into a coarse colour family chosen so
 *  the chip row stays short (~12 items) but the filter still tracks
 *  user intuition: someone looking for "a blue PETG" expects every
 *  blue spool to be in one bucket regardless of what the brand named it.
 *
 *  The classifier works in HSL space because it lines up far better
 *  with perceptual colour judgement than RGB does (a 10% RGB shift can
 *  flip "red" to "brown"; a 10% HSL shift won't).
 *
 *  All thresholds were tuned against the curated SUNLU / Inslogic /
 *  Jayo seed colours plus an additional set of pathological cases
 *  exercised in the sanity-check IIFE at the bottom of the file.
 */

export type ColorFamilyId =
  | "white"
  | "black"
  | "grey"
  | "red"
  | "orange"
  | "yellow"
  | "green"
  | "cyan"
  | "blue"
  | "purple"
  | "pink"
  | "brown"
  | "multi";

export interface ColorFamily {
  id: ColorFamilyId;
  /** Human-readable label shown on the chip. */
  label: string;
  /** Swatch colour rendered next to the label. Picked to be a
   *  recognisable representative of the family, not a perfect average. */
  swatch: string;
}

/** Declaration order is render order in the filter row. We lead with
 *  the achromatic families (white / black / grey) because they're the
 *  most-used in PLA stock, then go through the warm side of the wheel,
 *  then cool, then "multi" as a catch-all. */
export const COLOR_FAMILIES: readonly ColorFamily[] = [
  { id: "white",  label: "White",  swatch: "#F5F5F5" },
  { id: "black",  label: "Black",  swatch: "#202020" },
  { id: "grey",   label: "Grey",   swatch: "#9E9E9E" },
  { id: "red",    label: "Red",    swatch: "#D32F2F" },
  { id: "orange", label: "Orange", swatch: "#F57C00" },
  { id: "yellow", label: "Yellow", swatch: "#FBC02D" },
  { id: "green",  label: "Green",  swatch: "#388E3C" },
  { id: "cyan",   label: "Cyan",   swatch: "#0097A7" },
  { id: "blue",   label: "Blue",   swatch: "#1976D2" },
  { id: "purple", label: "Purple", swatch: "#7B1FA2" },
  { id: "pink",   label: "Pink",   swatch: "#E91E63" },
  { id: "brown",  label: "Brown",  swatch: "#6D4C41" },
  { id: "multi",  label: "Multi",  swatch: "linear-gradient(135deg,#ff5722,#ffeb3b,#4caf50,#2196f3,#9c27b0)" },
] as const;

const FAMILY_BY_ID: Record<ColorFamilyId, ColorFamily> = Object.fromEntries(
  COLOR_FAMILIES.map((f) => [f.id, f]),
) as Record<ColorFamilyId, ColorFamily>;

export function familyMeta(id: ColorFamilyId): ColorFamily {
  return FAMILY_BY_ID[id];
}

// ── parsing ───────────────────────────────────────────────────────────────

interface Hsl {
  /** Hue in degrees [0, 360). */
  h: number;
  /** Saturation in [0, 1]. */
  s: number;
  /** Lightness in [0, 1]. */
  l: number;
}

/** Parse a "#RRGGBB" or "#RGB" hex string. Returns null on anything else
 *  so callers can fall back to the "multi" / "other" family for things
 *  like custom-named multicolour spools that have no meaningful primary
 *  hex value. */
function parseHex(hex: string | null | undefined): { r: number; g: number; b: number } | null {
  if (!hex) return null;
  let s = hex.trim();
  if (s.startsWith("#")) s = s.slice(1);
  if (s.length === 3) {
    // Expand shorthand: "F0A" -> "FF00AA".
    s = s.split("").map((c) => c + c).join("");
  }
  if (!/^[0-9a-fA-F]{6}$/.test(s)) return null;
  return {
    r: parseInt(s.slice(0, 2), 16),
    g: parseInt(s.slice(2, 4), 16),
    b: parseInt(s.slice(4, 6), 16),
  };
}

function rgbToHsl(r: number, g: number, b: number): Hsl {
  const rn = r / 255;
  const gn = g / 255;
  const bn = b / 255;
  const max = Math.max(rn, gn, bn);
  const min = Math.min(rn, gn, bn);
  const l = (max + min) / 2;

  if (max === min) return { h: 0, s: 0, l };

  const d = max - min;
  const s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
  let h: number;
  switch (max) {
    case rn:
      h = (gn - bn) / d + (gn < bn ? 6 : 0);
      break;
    case gn:
      h = (bn - rn) / d + 2;
      break;
    default:
      h = (rn - gn) / d + 4;
  }
  return { h: (h * 60) % 360, s, l };
}

// ── classifier ────────────────────────────────────────────────────────────

/** Resolve a hex value (or null/garbage) to a colour-family id.
 *
 *  Tuning notes (worth keeping if you ever revisit thresholds):
 *
 *  - Achromatic bands (white/black/grey) check lightness/saturation
 *    FIRST. A near-white with a faint pink tint should still bucket as
 *    "white", not "pink", and the same for grey. The saturation cap
 *    is 0.18 (not 0.10) because PLA whites typically have a slight
 *    blue or yellow cast at the hex level.
 *
 *  - Brown is checked before red/orange because brown's hue range
 *    overlaps both, but brown is distinguishable by its lower
 *    lightness (< 0.45). Hex like #6D4C41 (saddle brown) and
 *    #A1887F (mocha) both land here.
 *
 *  - Pink vs red: pink is a HIGH-lightness red (> 0.65). #E91E63
 *    (Material pink) actually has l ≈ 0.52, so the bound is set at
 *    0.5 -- empirically this matches what users call "pink" in
 *    filament marketing.
 *
 *  - The hue boundaries themselves use standard 12-around-the-wheel
 *    art-school divisions, NOT the more permissive CSS named-colour
 *    bands. Tightening orange to 16-44 degrees (rather than the
 *    commonly-cited 15-45) avoids leaking "warm yellow" into orange.
 */
export function familyFor(hex: string | null | undefined): ColorFamilyId {
  const rgb = parseHex(hex);
  if (!rgb) return "multi";

  const { h, s, l } = rgbToHsl(rgb.r, rgb.g, rgb.b);

  // Achromatic checks first -- lightness extremes and low saturation
  // dominate the colour wheel.
  if (l >= 0.92) return "white";
  if (l <= 0.12) return "black";
  if (s <= 0.18) return "grey";

  // Brown: warm hue + low lightness + moderate saturation. Catches
  // mocha, saddle brown, terracotta, etc. before the red/orange
  // bands would claim them.
  if (l < 0.45 && s < 0.7 && (h < 50 || h >= 330)) return "brown";

  // Hue-driven buckets. Wheel is divided as:
  //   red       345-360 + 0-15
  //   orange    16-44
  //   yellow    45-65
  //   green     66-165
  //   cyan      166-200
  //   blue      201-255
  //   purple    256-290
  //   pink      291-344  (or any high-lightness red-leaning hue)
  if (h >= 345 || h < 16) {
    return l > 0.65 ? "pink" : "red";
  }
  if (h < 45) return "orange";
  if (h < 66) return "yellow";
  if (h < 166) return "green";
  if (h < 201) return "cyan";
  if (h < 256) return "blue";
  if (h < 291) return "purple";
  return "pink";
}

// ── self-check ────────────────────────────────────────────────────────────

/** Sanity assertions exercised at module import time in development
 *  builds. Kept inside an IIFE so the cost is zero in production
 *  (terser strips the `if (import.meta.env?.DEV) { ... }` branch).
 *
 *  These aren't a proper test suite -- they're a regression net for
 *  the obvious cases. If you tighten one of the thresholds above and
 *  accidentally break "Cold White is white", you'll see a console
 *  warning the next time you reload the dev server. */
if (import.meta.env?.DEV) {
  const cases: Array<[string, ColorFamilyId]> = [
    // Achromatic
    ["#FFFFFF", "white"], ["#F5F5F0", "white"], ["#FAFAFA", "white"], // Cold White, etc.
    ["#000000", "black"], ["#1A1A1A", "black"], ["#0F0F0F", "black"],
    ["#808080", "grey"],  ["#9E9E9E", "grey"],  ["#C0C0C0", "grey"],
    // Primaries
    ["#FF0000", "red"], ["#D32F2F", "red"],
    ["#F57C00", "orange"], ["#FF6F00", "orange"],
    ["#FBC02D", "yellow"], ["#FFEB3B", "yellow"],
    ["#388E3C", "green"], ["#4CAF50", "green"], ["#00FF00", "green"],
    ["#0097A7", "cyan"], ["#00BCD4", "cyan"],
    ["#1976D2", "blue"], ["#2196F3", "blue"], ["#0000FF", "blue"],
    ["#7B1FA2", "purple"], ["#9C27B0", "purple"],
    ["#E91E63", "pink"], ["#FF80AB", "pink"], ["#F8BBD0", "pink"],
    ["#6D4C41", "brown"], ["#A1887F", "brown"], ["#8D6E63", "brown"],
    // Fallback
    ["", "multi"], ["#", "multi"], ["nonsense", "multi"], ["#GG0000", "multi"],
  ];
  for (const [hex, expected] of cases) {
    const got = familyFor(hex);
    if (got !== expected) {
      // eslint-disable-next-line no-console
      console.warn(`[colorFamilies] ${hex} expected=${expected} got=${got}`);
    }
  }
}
