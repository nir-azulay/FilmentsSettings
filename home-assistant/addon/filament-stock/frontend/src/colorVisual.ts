/** Tint and contrast helpers for filament color UI */

function parseHex(hex: string): { r: number; g: number; b: number } | null {
  const h = (hex || "").trim().replace(/^#/, "");
  if (h.length === 3) {
    return {
      r: parseInt(h[0] + h[0], 16),
      g: parseInt(h[1] + h[1], 16),
      b: parseInt(h[2] + h[2], 16),
    };
  }
  if (h.length === 6) {
    return {
      r: parseInt(h.slice(0, 2), 16),
      g: parseInt(h.slice(2, 4), 16),
      b: parseInt(h.slice(4, 6), 16),
    };
  }
  return null;
}

function clamp(n: number): number {
  return Math.max(0, Math.min(255, Math.round(n)));
}

export function normalizeHex(hex: string, fallback = "#808080"): string {
  const rgb = parseHex(hex);
  if (!rgb) return fallback;
  const to2 = (n: number) => clamp(n).toString(16).padStart(2, "0");
  return `#${to2(rgb.r)}${to2(rgb.g)}${to2(rgb.b)}`;
}

export function isLightColor(hex: string): boolean {
  const rgb = parseHex(hex);
  if (!rgb) return false;
  const lum = (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b) / 255;
  return lum > 0.62;
}

export function darkenHex(hex: string, amount = 0.28): string {
  const rgb = parseHex(hex);
  if (!rgb) return "#505050";
  const f = 1 - amount;
  return `#${clamp(rgb.r * f).toString(16).padStart(2, "0")}${clamp(rgb.g * f).toString(16).padStart(2, "0")}${clamp(rgb.b * f).toString(16).padStart(2, "0")}`;
}

export function colorTint(hex: string, alpha: number): string {
  const rgb = parseHex(hex);
  if (!rgb) return `rgba(128,128,128,${alpha})`;
  return `rgba(${rgb.r},${rgb.g},${rgb.b},${alpha})`;
}

export type ColorVisual = {
  hex: string;
  accent: string;
  rim: string;
  bg: string;
  bgHover: string;
  border: string;
};

export function getColorVisual(hex: string, muted = false): ColorVisual {
  const h = normalizeHex(hex);
  const a = muted ? 0.12 : 0.28;
  const aHover = muted ? 0.18 : 0.38;
  return {
    hex: h,
    accent: h,
    rim: darkenHex(h, 0.35),
    bg: colorTint(h, a),
    bgHover: colorTint(h, aHover),
    border: colorTint(h, muted ? 0.35 : 0.55),
  };
}
