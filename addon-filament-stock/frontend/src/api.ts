// Relative API base so the bundle works behind Home Assistant Ingress, which
// mounts the add-on under a per-session path like
// /api/hassio_ingress/<TOKEN>/. fetch("api/filaments") resolves against
// document.baseURI -> the Ingress prefix.
const BASE = "api";

export type ColorStatus = "in_stock" | "ordered" | "out_of_stock";

/** Per-color packaging counters were introduced in add-on 0.3.0. Older APIs
 *  return only quantity/quantity_used; treat the new fields as 0 if absent. */
export interface ColorStock {
  id: number;
  filament_id: number;
  color_name: string;
  color_hex: string;
  /** Spool count (the full bagged-on-plastic-spool form). */
  quantity: number;
  quantity_used: number;
  /** Refill count (Bambu-style inner cardboard core, no plastic spool). */
  quantity_refill?: number;
  used_refill?: number;
  /** Server-computed convenience values. */
  available_spool?: number;
  available_refill?: number;
  available_total?: number;
  /** Omitted on older deployed APIs; UI treats missing as in_stock */
  status?: ColorStatus;
  order_id: string | null;
  created_at: string;
}

/** Per-action discriminator used for service calls and UI controls. */
export type PackagingType = "spool" | "refill";

export interface Filament {
  id: number;
  brand: string;
  material: string;
  filament_type: string;
  filament_id: string | null;
  density: number | null;
  nozzle_temp_min: number | null;
  nozzle_temp_max: number | null;
  bed_temp: number | null;
  amazon_url: string;
  brand_logo_url: string;
  notes: string;
  low_stock_threshold: number;
  current_stock: number;
  colors: ColorStock[];
  created_at: string;
}

export interface StockEntry {
  id: number;
  filament_id: number;
  color_stock_id: number | null;
  quantity: number;
  event_type: string;
  notes: string;
  created_at: string;
}

export interface Alert {
  filament_id: number;
  color_stock_id: number;
  brand: string;
  material: string;
  filament_type: string;
  color_name: string;
  current_stock: number;
  threshold: number;
}

export interface StapleAlertIgnore {
  id: number;
  filament_type: string;
  color_name: string;
  color_key: string;
  created_at: string;
}

export async function fetchFilaments(): Promise<Filament[]> {
  const res = await fetch(`${BASE}/filaments`);
  return res.json();
}

export async function createFilament(data: Partial<Filament>): Promise<Filament> {
  const res = await fetch(`${BASE}/filaments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function updateFilament(id: number, data: Partial<Filament>): Promise<Filament> {
  const res = await fetch(`${BASE}/filaments/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function deleteFilament(id: number): Promise<void> {
  await fetch(`${BASE}/filaments/${id}`, { method: "DELETE" });
}

export async function addColor(
  filamentId: number,
  data: {
    color_name: string;
    color_hex: string;
    quantity?: number;
    quantity_refill?: number;
    status?: string;
  },
): Promise<ColorStock> {
  const res = await fetch(`${BASE}/filaments/${filamentId}/colors`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function updateColor(colorId: number, data: Partial<ColorStock>): Promise<ColorStock> {
  const res = await fetch(`${BASE}/colors/${colorId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function deleteColor(colorId: number): Promise<void> {
  await fetch(`${BASE}/colors/${colorId}`, { method: "DELETE" });
}

export async function fetchHistory(filamentId: number): Promise<StockEntry[]> {
  const res = await fetch(`${BASE}/filaments/${filamentId}/history`);
  return res.json();
}

export async function addStockEvent(
  filamentId: number,
  data: { quantity: number; event_type: string; color_stock_id?: number | null; notes: string }
): Promise<StockEntry> {
  const res = await fetch(`${BASE}/stock/${filamentId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function fetchAlerts(): Promise<Alert[]> {
  const res = await fetch(`${BASE}/alerts`);
  return res.json();
}

export async function fetchAlertIgnores(): Promise<StapleAlertIgnore[]> {
  const res = await fetch(`${BASE}/alert-ignores`);
  return res.json();
}

export async function ignoreStapleAlert(filamentType: string, colorName: string): Promise<StapleAlertIgnore> {
  const res = await fetch(`${BASE}/alert-ignores`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filament_type: filamentType, color_name: colorName }),
  });
  return res.json();
}

export async function deleteAlertIgnore(ignoreId: number): Promise<void> {
  await fetch(`${BASE}/alert-ignores/${ignoreId}`, { method: "DELETE" });
}

export async function importProfiles(): Promise<{ imported: number; skipped: number }> {
  const res = await fetch(`${BASE}/import`, { method: "POST" });
  return res.json();
}
