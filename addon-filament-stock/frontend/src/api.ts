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
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
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

// ─── BambuStudio profile bundle ────────────────────────────────────────────
// Each value in `summary` is a 1- or 2-element string array (Standard
// extruder, optional High Flow extruder) as stored in Bambu profile JSON.

export interface ProfileNozzleEntry {
  nozzle_mm: string;       // "0.2" | "0.4" | "0.6" | "0.8"
  layer_height_mm: string; // "0.10" | "0.20" | "0.30" | "0.40"
  file_name: string;
  info_file: string | null;
}

export interface ProfileMetadata {
  available: boolean;
  product: string;
  files: string[];
  base_file?: string | null;
  base_info?: string | null;
  preset_file?: string | null;
  preset_info?: string | null;
  nozzles: ProfileNozzleEntry[];
  summary: Record<string, string[] | string | null>;
}

export async function fetchProfileMetadata(filamentId: number): Promise<ProfileMetadata> {
  const res = await fetch(`${BASE}/filaments/${filamentId}/profile`);
  return res.json();
}

/** Browser-friendly download URLs (resolved against document.baseURI so they
 *  work behind HA Ingress just like the API calls). */
export function profileFileUrl(filamentId: number, fileName: string): string {
  return `${BASE}/filaments/${filamentId}/profile/file/${encodeURIComponent(fileName)}`;
}
export function profileZipUrl(filamentId: number): string {
  return `${BASE}/filaments/${filamentId}/profile/zip`;
}

// ─── AMS tray view ─────────────────────────────────────────────────────────
// Each AmsTray represents one Bambu AMS slot (or the external spool) as seen
// by the ha-bambulab integration. `stock` is the local Filament/ColorStock
// match the backend computed for us so the UI doesn't have to cross-reference.

export interface AmsTrayStockMatched {
  matched: true;
  filament_db_id: number;
  brand: string;
  material: string;
  filament_type: string;
  filament_total_available: number;
  color_matched: boolean;
  color_stock_id?: number;
  color_name?: string;
  color_hex?: string;
  available_spool?: number;
  available_refill?: number;
  available_total?: number;
  status?: ColorStatus;
  color_reason?: string;
  filament_color_count?: number;
}

export interface AmsTrayStockUnmatched {
  matched: false;
  reason: "tray_empty" | "no_filament_id" | "filament_id_not_in_stock";
  filament_id?: string;
}

export type AmsTrayStock = AmsTrayStockMatched | AmsTrayStockUnmatched;

/** A user-declared "I loaded this spool from my stock into this tray" link.
 *  Added in add-on 0.6.0. The same object is returned from /assign,
 *  attached to each tray in /ams/trays, and listed by /assignment-history. */
export interface TrayAssignment {
  id: number;
  entity_id: string;
  location_label: string;
  color_stock_id: number;
  packaging: PackagingType;
  pushed_to_printer: boolean;
  push_error: string;
  assigned_at: string | null;
  unassigned_at: string | null;
  notes: string;
  /** Joined-in filament/color info for convenient UI rendering. */
  filament_db_id: number | null;
  brand: string | null;
  material: string | null;
  filament_type: string | null;
  color_name: string | null;
  color_hex: string | null;
}

export interface AmsTray {
  entity_id: string;
  /** Raw printer prefix derived from entity_id (kept for grouping fallback). */
  printer: string;
  /** Friendly printer name from the HA device registry. e.g. "H2S 3D Printer".
   *  Falls back to a prettified `printer` when the registry lookup is unavailable. */
  printer_label?: string;
  /** Hardware model from the HA device registry, normalised to a short label.
   *  e.g. "AMS", "AMS 2 Pro", "AMS HT", "External spool". */
  model_label?: string;
  /** The AMS unit's full label including instance suffix when multiple of the
   *  same model exist on the printer. e.g. "AMS 2 Pro #1", "AMS HT #2",
   *  "External spool". Use this as the grouping key. */
  unit_label?: string;
  /** Friendly name of the AMS hardware device itself (rarely needed by the UI). */
  device_name?: string;
  /** Disambiguator HA assigns when multiple devices want the same entity_id
   *  slug (1 = no suffix, 2 = `_2`, 3 = `_3`, ...). Used internally to tell
   *  two AMS 2 Pros apart since their tray entity_ids only differ by this. */
  instance_idx?: number;
  /** Raw `friendly_name` attribute from HA, e.g. "AMS 2 Pro #1 Tray 1". */
  friendly_name?: string;
  kind: "ams" | "external";
  ams_idx: number | null;
  tray_idx: number;
  location_label: string;
  loaded: boolean;
  raw_state: string | null;
  filament_id: string | null;
  color_hex: string | null;
  material: string | null;
  name: string | null;
  remain_pct: number | null;
  last_updated: string | null;
  stock: AmsTrayStock;
  /** Set when the user has assigned a spool from local stock to this tray
   *  via the add-on. Null when no assignment is live. Added in 0.6.0. */
  assignment?: TrayAssignment | null;
}

export interface AmsTraysResponse {
  available: boolean;
  /** Set when available=false to explain why (e.g. Supervisor unreachable). */
  error?: string;
  trays: AmsTray[];
}

// ─── AMS tray assignment (add-on 0.6.0) ───────────────────────────────────
// Lets the UI tell the backend "I just loaded this spool from my stock into
// this AMS tray". The backend decrements the corresponding ColorStock
// counter and (optionally) calls bambu_lab.set_filament so the printer's
// AMS display updates too.

export interface AssignSuggestion {
  filament_db_id: number;
  color_stock_id: number;
  brand: string;
  material: string;
  filament_type: string;
  color_name: string;
  color_hex: string;
  available_spool: number;
  available_refill: number;
  status: ColorStatus;
  /** True when this filament's type/material contains the tray's current
   *  material substring (e.g. tray is PETG and filament is "PETG HS"). The
   *  backend already sorted by this so the UI doesn't need to re-sort, but
   *  it's exposed so we can render a "match" hint on the first few rows. */
  material_match: boolean;
  /** Lower = shown earlier. Tier 0 = material match with spools available,
   *  Tier 1 = material match with refills, Tier 2 = spools, Tier 3 = refills,
   *  Tier 4 = ordered/etc. */
  tier: number;
}

export interface AssignSuggestionsResponse {
  entity_id: string;
  material_hint: string | null;
  current_assignment: TrayAssignment | null;
  suggestions: AssignSuggestion[];
}

export interface AssignTrayRequest {
  color_stock_id: number;
  packaging: PackagingType;
  push_to_printer?: boolean;
  return_prior_to_stock?: boolean;
  location_label?: string;
  notes?: string;
}

export interface AssignTrayResponse {
  assignment: TrayAssignment;
  color: {
    id: number;
    filament_id: number;
    color_name: string;
    color_hex: string;
    quantity: number;
    quantity_used: number;
    quantity_refill: number;
    used_refill: number;
    available_spool: number;
    available_refill: number;
    available_total: number;
  };
  push_to_printer: {
    requested: boolean;
    /** null when push wasn't requested, true on success, false on failure. */
    ok: boolean | null;
    error: string;
  };
}

export async function fetchAssignSuggestions(
  entityId: string,
  materialHint?: string | null,
): Promise<AssignSuggestionsResponse> {
  const params = new URLSearchParams();
  if (materialHint) params.set("material_hint", materialHint);
  const qs = params.toString();
  const url =
    `${BASE}/ams/trays/${encodeURIComponent(entityId)}/suggestions` +
    (qs ? `?${qs}` : "");
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to load suggestions (HTTP ${res.status})`);
  }
  return res.json();
}

export async function assignTray(
  entityId: string,
  data: AssignTrayRequest,
): Promise<AssignTrayResponse> {
  const res = await fetch(
    `${BASE}/ams/trays/${encodeURIComponent(entityId)}/assign`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    },
  );
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body?.detail ?? detail;
    } catch {
      // ignore body parse errors
    }
    throw new Error(detail);
  }
  return res.json();
}

export async function unassignTray(
  entityId: string,
): Promise<{ ok: boolean; had_assignment: boolean }> {
  const res = await fetch(
    `${BASE}/ams/trays/${encodeURIComponent(entityId)}/unassign`,
    { method: "POST" },
  );
  if (!res.ok) {
    throw new Error(`Failed to unassign (HTTP ${res.status})`);
  }
  return res.json();
}

export async function fetchAmsTrays(): Promise<AmsTraysResponse> {
  const res = await fetch(`${BASE}/ams/trays`);
  if (res.status === 404) {
    // Backend returns 404 with a helpful message when no AMS sensors exist
    // in HA. Turn it into a structured "no trays" response so the UI can
    // distinguish from a hard error.
    let detail = "";
    try {
      const body = await res.json();
      detail = body?.detail ?? "";
    } catch {
      // ignore body parse errors
    }
    return { available: true, trays: [], error: detail };
  }
  return res.json();
}
