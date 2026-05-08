const BASE = "/api";

export interface ColorStock {
  id: number;
  filament_id: number;
  color_name: string;
  color_hex: string;
  quantity: number;
  created_at: string;
}

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
  brand: string;
  material: string;
  current_stock: number;
  threshold: number;
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

export async function addColor(filamentId: number, data: { color_name: string; color_hex: string; quantity: number }): Promise<ColorStock> {
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

export async function importProfiles(): Promise<{ imported: number; skipped: number }> {
  const res = await fetch(`${BASE}/import`, { method: "POST" });
  return res.json();
}
