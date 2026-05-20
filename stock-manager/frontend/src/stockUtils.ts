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

/** Low-stock warning: PLA/PETG/ASA only, black/white colors only. */
export function filamentHasLowStock(filament: Filament): boolean {
  if (!isLowStockMonitoredFilament(filament)) return false;
  const threshold = filament.low_stock_threshold ?? 1;
  return filament.colors.some(
    (c) =>
      isLowStockMonitoredColorName(c.color_name) &&
      isInStockColor(c) &&
      availableQty(c) <= threshold,
  );
}
