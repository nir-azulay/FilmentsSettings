import type { ColorStock, Filament } from "./api";

/** Legacy QNAP API omits status; treat missing as in_stock. */
export function colorStatus(c: ColorStock): string {
  return c.status ?? "in_stock";
}

export function isInStockColor(c: ColorStock): boolean {
  const s = colorStatus(c);
  return s === "in_stock";
}

export function isOrderedColor(c: ColorStock): boolean {
  return colorStatus(c) === "ordered";
}

export function availableQty(c: ColorStock): number {
  return Math.max(0, (c.quantity ?? 0) - (c.quantity_used ?? 0));
}

export function filamentInStockQty(colors: ColorStock[]): number {
  return colors.filter(isInStockColor).reduce((s, c) => s + availableQty(c), 0);
}

export function filamentOrderedQty(colors: ColorStock[]): number {
  return colors.filter(isOrderedColor).reduce((s, c) => s + (c.quantity ?? 0), 0);
}

/** Matches per-card badges and color-row "remaining" spools. */
export function filamentAvailableSpools(filament: Filament): number {
  return filamentInStockQty(filament.colors);
}

export function totalAvailableSpools(filaments: Filament[]): number {
  return filaments.reduce((sum, f) => sum + filamentAvailableSpools(f), 0);
}

export function totalOnOrderSpools(filaments: Filament[]): number {
  return filaments.reduce((sum, f) => sum + filamentOrderedQty(f.colors), 0);
}

const LOW_STOCK_MATERIAL_TYPES = new Set(["PLA", "PETG", "ASA"]);

export function isLowStockMonitoredFilament(filament: Filament): boolean {
  return LOW_STOCK_MATERIAL_TYPES.has(filament.filament_type);
}

export function isLowStockMonitoredColorName(colorName: string): boolean {
  const key = colorName.trim().toLowerCase().replace(/\s+/g, " ");
  return key === "black" || key === "white";
}

export function staplePoolKey(filamentType: string, colorName: string): string {
  const color = colorName.trim().toLowerCase().replace(/\s+/g, " ");
  return `${filamentType}|${color}`;
}

/** Black/white totals per PLA/PETG/ASA across all brands. */
export function buildStaplePools(filaments: Filament[]): Map<string, number> {
  const pools = new Map<string, number>();
  for (const f of filaments) {
    if (!isLowStockMonitoredFilament(f)) continue;
    for (const c of f.colors) {
      if (!isLowStockMonitoredColorName(c.color_name) || !isInStockColor(c)) continue;
      const key = staplePoolKey(f.filament_type, c.color_name);
      pools.set(key, (pools.get(key) ?? 0) + availableQty(c));
    }
  }
  return pools;
}

export function buildIgnoredStapleKeys(ignores: { filament_type: string; color_key: string }[]): Set<string> {
  const s = new Set<string>();
  for (const row of ignores) {
    s.add(staplePoolKey(row.filament_type, row.color_key));
  }
  return s;
}

/** Low-stock warning only if no other brand covers the same material type + color. */
export function filamentHasLowStock(
  filament: Filament,
  staplePools: Map<string, number>,
  ignoredStaples: Set<string> = new Set(),
): boolean {
  if (!isLowStockMonitoredFilament(filament)) return false;
  const threshold = filament.low_stock_threshold ?? 1;
  return filament.colors.some((c) => {
    if (!isLowStockMonitoredColorName(c.color_name) || !isInStockColor(c)) return false;
    if (availableQty(c) > threshold) return false;
    const key = staplePoolKey(filament.filament_type, c.color_name);
    if (ignoredStaples.has(key)) return false;
    if ((staplePools.get(key) ?? 0) > threshold) return false;
    return true;
  });
}
