import { useEffect, useMemo, useState, type Dispatch, type SetStateAction } from "react";
import {
  AddonConfig,
  AmsTray,
  AssignSuggestion,
  AssignSuggestionsResponse,
  DEFAULT_ADDON_CONFIG,
  assignTray,
  fetchAddonConfig,
  fetchAssignSuggestions,
  PackagingType,
} from "../api";
import { ColorFamilyId, familyFor } from "../colorFamilies";
import ColorFilter from "./ColorFilter";
import { SpoolIcon } from "./SpoolIcon";

// Local helper so multi-select chip toggles read cleanly. Identical
// pattern to the one in Dashboard.tsx -- if we add a third consumer,
// promote it into a hook.
function toggleInSet<T>(setter: Dispatch<SetStateAction<Set<T>>>, value: T) {
  setter((prev) => {
    const next = new Set(prev);
    if (next.has(value)) next.delete(value);
    else next.add(value);
    return next;
  });
}

/** Modal dialog: pick a filament+color from local stock to "assign" to an
 *  AMS tray. Smart-defaults the picker by the tray's current material and
 *  lets the user opt-in to pushing the metadata to the printer via
 *  bambu_lab.set_filament. */

interface Props {
  tray: AmsTray;
  onClose: () => void;
  /** Called after a successful assignment so the parent can refresh the
   *  /ams/trays poll (and any filament cards whose counters changed). */
  onAssigned: () => void;
}

export default function AssignTrayDialog({ tray, onClose, onAssigned }: Props) {
  const [data, setData] = useState<AssignSuggestionsResponse | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  // Multi-select to match the main Stock page. Empty Set = no filter,
  // i.e. show all types / brands / colours.
  const [filterTypes, setFilterTypes] = useState<Set<string>>(() => new Set());
  const [filterBrands, setFilterBrands] = useState<Set<string>>(() => new Set());
  const [filterColors, setFilterColors] = useState<Set<ColorFamilyId>>(() => new Set());
  const [selectedColorId, setSelectedColorId] = useState<number | null>(null);
  const [packaging, setPackaging] = useState<PackagingType>("spool");

  const selectColor = (colorStockId: number) => {
    setSelectedColorId(colorStockId);
    const suggestion = data?.suggestions.find((s) => s.color_stock_id === colorStockId);
    if (suggestion) {
      setPackaging(suggestion.available_refill > 0 ? "refill" : "spool");
    }
  };
  // Initial value mirrors the compiled-in fallback; the real default
  // arrives with /api/config and is applied below (only if the user
  // hasn't manually toggled the checkbox yet, so we never override an
  // explicit user choice mid-dialog).
  const [pushToPrinter, setPushToPrinter] = useState(
    DEFAULT_ADDON_CONFIG.default_push_to_printer,
  );
  const [pushToPrinterTouched, setPushToPrinterTouched] = useState(false);
  const [returnPriorToStock, setReturnPriorToStock] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  // User-configurable add-on options (e.g. whether to ask about the
  // replaced spool). Defaults to the compiled-in fallback while the
  // /api/config fetch is in flight so the UI never blocks on it.
  const [config, setConfig] = useState<AddonConfig>(DEFAULT_ADDON_CONFIG);

  // Initial load + whenever the tray entity changes.
  useEffect(() => {
    let cancelled = false;
    setData(null);
    setLoadError(null);
    setSelectedColorId(null);
    // New tray -> fresh checkbox state; config will re-seed it below.
    setPushToPrinterTouched(false);
    // Suggestions and add-on config are independent -- fire them in parallel.
    void fetchAddonConfig().then((c) => {
      if (cancelled) return;
      setConfig(c);
      // Apply the configured default for the push-to-printer checkbox.
      // Safe to set unconditionally here because we just reset the
      // touched flag above for this fresh dialog session.
      setPushToPrinter(c.default_push_to_printer);
    });
    fetchAssignSuggestions(tray.entity_id, tray.material)
      .then((d) => {
        if (cancelled) return;
        setData(d);
        if (d.suggestions.length > 0) {
          setSelectedColorId(d.suggestions[0].color_stock_id);
          const first = d.suggestions[0];
          setPackaging(
            first.available_refill > 0 ? "refill" : "spool",
          );
        }
      })
      .catch((err: Error) => {
        if (!cancelled) setLoadError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, [tray.entity_id, tray.material]);

  const uniqueTypes = useMemo(() => {
    if (!data) return [] as string[];
    return [...new Set(data.suggestions.map((s) => s.filament_type))].sort();
  }, [data]);

  const uniqueBrands = useMemo(() => {
    if (!data) return [] as string[];
    // Narrow the brand list to whatever's relevant under the currently
    // selected types (if any). Mirrors the previous single-select
    // behaviour where picking a type also reset the brand pool.
    const pool =
      filterTypes.size > 0
        ? data.suggestions.filter((s) => filterTypes.has(s.filament_type))
        : data.suggestions;
    return [...new Set(pool.map((s) => s.brand))].sort();
  }, [data, filterTypes]);

  // Set of colour-family ids actually present in the assign suggestions
  // (after type/brand narrowing). Feeds the ColorFilter's `available`
  // prop so we don't render empty colour chips.
  const colorFamiliesInData = useMemo(() => {
    const set = new Set<ColorFamilyId>();
    if (!data) return set;
    const pool = data.suggestions.filter((s) => {
      if (filterTypes.size > 0 && !filterTypes.has(s.filament_type)) return false;
      if (filterBrands.size > 0 && !filterBrands.has(s.brand)) return false;
      return true;
    });
    for (const s of pool) set.add(familyFor(s.color_hex));
    return set;
  }, [data, filterTypes, filterBrands]);

  const filtered = useMemo(() => {
    if (!data) return [] as AssignSuggestion[];
    let list = data.suggestions;
    if (filterTypes.size > 0) {
      list = list.filter((s) => filterTypes.has(s.filament_type));
    }
    if (filterBrands.size > 0) {
      list = list.filter((s) => filterBrands.has(s.brand));
    }
    if (filterColors.size > 0) {
      list = list.filter((s) => filterColors.has(familyFor(s.color_hex)));
    }
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      list = list.filter(
        (s) =>
          s.brand.toLowerCase().includes(q) ||
          s.material.toLowerCase().includes(q) ||
          s.color_name.toLowerCase().includes(q),
      );
    }
    return list;
  }, [data, search, filterTypes, filterBrands, filterColors]);

  const selected = useMemo(
    () =>
      data?.suggestions.find((s) => s.color_stock_id === selectedColorId) ?? null,
    [data, selectedColorId],
  );

  const availableForSelected =
    selected && packaging === "spool"
      ? selected.available_spool
      : selected?.available_refill ?? 0;
  const canSubmit = !submitting && selected !== null && availableForSelected > 0;

  async function handleSubmit() {
    if (!selected) return;
    setSubmitting(true);
    setSubmitError(null);
    try {
      const resp = await assignTray(tray.entity_id, {
        color_stock_id: selected.color_stock_id,
        packaging,
        push_to_printer: pushToPrinter,
        return_prior_to_stock: returnPriorToStock,
        location_label: tray.location_label,
      });
      if (
        resp.push_to_printer.requested &&
        resp.push_to_printer.ok === false
      ) {
        // Local assignment succeeded but the printer push failed. Keep the
        // dialog open and show the error so the user can decide whether to
        // close (local-only assignment) or retry once the printer is online.
        setSubmitError(
          `Saved locally, but the printer push failed: ${resp.push_to_printer.error}`,
        );
        // Still let the parent refresh -- the local stock did change.
        onAssigned();
        return;
      }
      onAssigned();
      onClose();
    } catch (err) {
      setSubmitError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  const current = data?.current_assignment;

  return (
    <div style={backdrop} onClick={onClose}>
      <div style={dialog} onClick={(e) => e.stopPropagation()}>
        <header style={dialogHeader}>
          <div>
            <h3 style={dialogTitle}>Assign filament to tray</h3>
            <p style={dialogSubtitle}>
              {tray.location_label}
              {tray.material && (
                <>
                  {" · "}
                  <code style={{ fontSize: 11 }}>{tray.material}</code>{" "}
                  tray
                </>
              )}
            </p>
          </div>
          <button type="button" onClick={onClose} style={closeBtn} aria-label="Close">
            ×
          </button>
        </header>

        <div style={scrollBody}>
          {current && (
            <div style={currentBox}>
              <span style={{ fontSize: 11, color: "var(--ha-secondary-text)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
                Currently assigned
              </span>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 4 }}>
                <SpoolIcon colorHex={current.color_hex ?? "#9e9e9e"} size={24} />
                <span style={{ fontSize: 13, fontWeight: 600 }}>
                  {current.brand} {current.material} · {current.color_name}
                </span>
                <span style={{ fontSize: 11, color: "var(--ha-secondary-text)" }}>
                  ({current.packaging})
                </span>
              </div>
              {config.ask_if_replaced_spool_empty ? (
                <div style={priorChoiceRow}>
                  <span style={{ fontSize: 12, color: "var(--ha-primary-text)" }}>
                    Is the replaced {current.packaging} empty?
                  </span>
                  <div style={priorToggle}>
                    <button
                      type="button"
                      onClick={() => setReturnPriorToStock(false)}
                      style={!returnPriorToStock ? priorBtnActive : priorBtn}
                    >
                      Yes, it's empty
                    </button>
                    <button
                      type="button"
                      onClick={() => setReturnPriorToStock(true)}
                      style={returnPriorToStock ? priorBtnActive : priorBtn}
                    >
                      No, return to stock
                    </button>
                  </div>
                </div>
              ) : (
                <p style={priorAutoNote}>
                  The replaced {current.packaging} will be returned to your stock.
                  Toggle this in the add-on's Configuration tab if you'd rather
                  be asked each time.
                </p>
              )}
            </div>
          )}

          {loadError && (
            <div style={errorBox}>
              <strong>Could not load suggestions.</strong>
              <p style={{ marginTop: 4, fontSize: 12 }}>{loadError}</p>
            </div>
          )}

          {!loadError && !data && <p style={emptyText}>Loading filaments…</p>}

          {data && (
            <>
              <input
                type="text"
                value={search}
                placeholder="Search by brand, material, or color…"
                onChange={(e) => setSearch(e.target.value)}
                style={searchInput}
              />

              {uniqueTypes.length > 1 && (
                <div style={chipRow}>
                  <span style={chipRowLabel}>Type</span>
                  <button
                    type="button"
                    onClick={() => {
                      // Clearing types also clears brands: brand pool
                      // is type-scoped so a brand chip selected under
                      // "PETG" wouldn't make sense without that type.
                      setFilterTypes(new Set());
                      setFilterBrands(new Set());
                    }}
                    style={filterTypes.size === 0 ? chipActive : chip}
                  >
                    All
                  </button>
                  {uniqueTypes.map((t) => (
                    <button
                      key={t}
                      type="button"
                      onClick={() => {
                        toggleInSet(setFilterTypes, t);
                        // Same rationale as above: a previously
                        // selected brand might be excluded under the
                        // new type set, so reset it for clarity.
                        setFilterBrands(new Set());
                      }}
                      style={filterTypes.has(t) ? chipActive : chip}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              )}

              {uniqueBrands.length > 1 && (
                <div style={chipRow}>
                  <span style={chipRowLabel}>Brand</span>
                  <button
                    type="button"
                    onClick={() => setFilterBrands(new Set())}
                    style={filterBrands.size === 0 ? chipActive : chip}
                  >
                    All
                  </button>
                  {uniqueBrands.map((b) => (
                    <button
                      key={b}
                      type="button"
                      onClick={() => toggleInSet(setFilterBrands, b)}
                      style={filterBrands.has(b) ? chipActive : chip}
                    >
                      {b}
                    </button>
                  ))}
                </div>
              )}

              {colorFamiliesInData.size > 1 && (
                <ColorFilter
                  available={colorFamiliesInData}
                  selected={filterColors}
                  onToggle={(id) => toggleInSet(setFilterColors, id)}
                  onClear={() => setFilterColors(new Set())}
                  label="Colour"
                />
              )}

              <div style={listWrap}>
                {filtered.length === 0 && (
                  <p style={emptyText}>
                    {search
                      ? "No filaments match your search."
                      : "Nothing in stock to assign. Mark a purchase first."}
                  </p>
                )}
                {filtered.map((s) => (
                  <SuggestionRow
                    key={s.color_stock_id}
                    s={s}
                    selected={s.color_stock_id === selectedColorId}
                    onSelect={() => selectColor(s.color_stock_id)}
                  />
                ))}
              </div>

              {submitError && (
                <div style={errorBox}>
                  <strong>Heads up.</strong>
                  <p style={{ marginTop: 4, fontSize: 12 }}>{submitError}</p>
                </div>
              )}
            </>
          )}
        </div>

        {data && (
          <div style={stickyFooter}>
            <div style={controlsRow}>
              <div style={packagingGroup}>
                <PackagingRadio
                  current={packaging}
                  value="spool"
                  count={selected?.available_spool ?? 0}
                  onSelect={() => setPackaging("spool")}
                />
                <PackagingRadio
                  current={packaging}
                  value="refill"
                  count={selected?.available_refill ?? 0}
                  onSelect={() => setPackaging("refill")}
                />
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                <label style={pushLabel}>
                  <input
                    type="checkbox"
                    checked={pushToPrinter}
                    onChange={(e) => {
                      setPushToPrinter(e.target.checked);
                      setPushToPrinterTouched(true);
                    }}
                  />
                  Also update the printer's AMS display
                </label>
                <span style={pushDisclaimer}>
                  Requires LAN mode. Does not work in Cloud-only mode.
                </span>
              </div>
            </div>

            <footer style={footer}>
              <button type="button" onClick={onClose} style={cancelBtn}>
                Cancel
              </button>
              <button
                type="button"
                onClick={() => void handleSubmit()}
                disabled={!canSubmit}
                style={primaryBtn(canSubmit)}
                title={
                  !selected
                    ? "Pick a filament first"
                    : availableForSelected <= 0
                    ? `No ${packaging}s of this color in stock`
                    : ""
                }
              >
                {submitting ? "Assigning…" : "Assign"}
              </button>
            </footer>
          </div>
        )}
      </div>
    </div>
  );
}

function SuggestionRow({
  s,
  selected,
  onSelect,
}: {
  s: AssignSuggestion;
  selected: boolean;
  onSelect: () => void;
}) {
  const totalAvail = s.available_spool + s.available_refill;
  return (
    <div
      role="button"
      onClick={onSelect}
      style={{
        ...row,
        ...(selected ? rowSelected : null),
        opacity: totalAvail === 0 ? 0.6 : 1,
      }}
    >
      <SpoolIcon colorHex={s.color_hex} size={28} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={rowTitle}>
          {s.brand} {s.material}
          {s.material_match && <span style={matchPill}>match</span>}
        </div>
        <div style={rowMeta}>
          {s.color_name}
          {" · "}
          <span style={{ fontFamily: "monospace" }}>{s.color_hex}</span>
        </div>
      </div>
      <div style={countCol}>
        <span style={countPill(s.available_spool > 0)}>
          {s.available_spool} spool{s.available_spool === 1 ? "" : "s"}
        </span>
        <span style={countPill(s.available_refill > 0)}>
          {s.available_refill} refill{s.available_refill === 1 ? "" : "s"}
        </span>
      </div>
    </div>
  );
}

function PackagingRadio({
  current,
  value,
  count,
  onSelect,
}: {
  current: PackagingType;
  value: PackagingType;
  count: number;
  onSelect: () => void;
}) {
  const isSelected = current === value;
  const disabled = count <= 0;
  return (
    <button
      type="button"
      onClick={onSelect}
      disabled={disabled}
      style={{
        ...packagingBtn,
        ...(isSelected ? packagingBtnSelected : null),
        opacity: disabled ? 0.45 : 1,
        cursor: disabled ? "not-allowed" : "pointer",
      }}
    >
      <span style={{ textTransform: "capitalize" }}>{value}</span>
      <span style={packagingBtnCount}>{count}</span>
    </button>
  );
}

// ── Styles ──────────────────────────────────────────────────────────────────

const backdrop: React.CSSProperties = {
  position: "fixed",
  inset: 0,
  background: "rgba(0,0,0,0.45)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  zIndex: 1000,
  padding: 16,
};
const dialog: React.CSSProperties = {
  background: "var(--ha-card-bg, #fff)",
  borderRadius: 12,
  width: "100%",
  maxWidth: 560,
  maxHeight: "85vh",
  display: "flex",
  flexDirection: "column",
  boxShadow: "0 18px 60px rgba(0,0,0,0.3)",
  overflow: "hidden",
};
const dialogHeader: React.CSSProperties = {
  display: "flex",
  alignItems: "flex-start",
  justifyContent: "space-between",
  gap: 12,
  padding: "16px 20px",
  borderBottom: "1px solid var(--ha-divider)",
  flexShrink: 0,
};
const scrollBody: React.CSSProperties = {
  flex: 1,
  overflowY: "auto",
  padding: "12px 20px",
  display: "flex",
  flexDirection: "column",
  gap: 12,
};
const stickyFooter: React.CSSProperties = {
  padding: "12px 20px",
  borderTop: "1px solid var(--ha-divider)",
  flexShrink: 0,
  display: "flex",
  flexDirection: "column",
  gap: 10,
  background: "var(--ha-card-bg, #fff)",
};
const dialogTitle: React.CSSProperties = {
  fontSize: 16,
  fontWeight: 600,
  color: "var(--ha-primary-text)",
};
const dialogSubtitle: React.CSSProperties = {
  marginTop: 2,
  fontSize: 12,
  color: "var(--ha-secondary-text)",
};
const closeBtn: React.CSSProperties = {
  background: "transparent",
  border: "none",
  fontSize: 22,
  lineHeight: 1,
  cursor: "pointer",
  color: "var(--ha-secondary-text)",
  padding: 0,
  width: 28,
  height: 28,
};
const currentBox: React.CSSProperties = {
  padding: "8px 10px",
  borderRadius: 8,
  background: "rgba(3,169,244,0.08)",
  border: "1px solid rgba(3,169,244,0.25)",
};
const errorBox: React.CSSProperties = {
  padding: "8px 10px",
  borderRadius: 8,
  background: "var(--ha-error-bg)",
  color: "var(--ha-error)",
  fontSize: 13,
};
const emptyText: React.CSSProperties = {
  fontSize: 12,
  color: "var(--ha-secondary-text)",
  padding: "12px 0",
  textAlign: "center",
};
const searchInput: React.CSSProperties = {
  padding: "8px 10px",
  fontSize: 13,
  border: "1px solid var(--ha-divider)",
  borderRadius: 6,
  background: "var(--ha-input-bg, #fff)",
  color: "var(--ha-primary-text)",
};
const listWrap: React.CSSProperties = {
  minHeight: 80,
  display: "flex",
  flexDirection: "column",
  gap: 4,
  border: "1px solid var(--ha-divider)",
  borderRadius: 8,
  padding: 4,
};
const row: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 10,
  padding: "8px 10px",
  borderRadius: 6,
  cursor: "pointer",
  border: "1px solid transparent",
};
const rowSelected: React.CSSProperties = {
  background: "rgba(3,169,244,0.12)",
  borderColor: "rgba(3,169,244,0.4)",
};
const rowTitle: React.CSSProperties = {
  fontSize: 13,
  fontWeight: 600,
  color: "var(--ha-primary-text)",
  display: "flex",
  alignItems: "center",
  gap: 6,
};
const rowMeta: React.CSSProperties = {
  fontSize: 11,
  color: "var(--ha-secondary-text)",
  marginTop: 2,
};
const matchPill: React.CSSProperties = {
  fontSize: 9,
  fontWeight: 700,
  padding: "1px 5px",
  borderRadius: 4,
  background: "rgba(76,175,80,0.18)",
  color: "#2e7d32",
  textTransform: "uppercase",
  letterSpacing: "0.05em",
};
const countCol: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  alignItems: "flex-end",
  gap: 2,
};
const countPill = (hasStock: boolean): React.CSSProperties => ({
  fontSize: 10,
  fontWeight: 600,
  padding: "1px 6px",
  borderRadius: 8,
  background: hasStock ? "rgba(76,175,80,0.12)" : "rgba(0,0,0,0.05)",
  color: hasStock ? "#2e7d32" : "var(--ha-secondary-text)",
  whiteSpace: "nowrap",
});
const controlsRow: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: 12,
  flexWrap: "wrap",
};
const packagingGroup: React.CSSProperties = {
  display: "flex",
  gap: 4,
  padding: 2,
  background: "rgba(0,0,0,0.04)",
  borderRadius: 8,
};
const packagingBtn: React.CSSProperties = {
  padding: "6px 12px",
  fontSize: 12,
  fontWeight: 500,
  background: "transparent",
  color: "var(--ha-primary-text)",
  border: "none",
  borderRadius: 6,
  display: "flex",
  alignItems: "center",
  gap: 6,
};
const packagingBtnSelected: React.CSSProperties = {
  background: "var(--ha-card-bg, #fff)",
  boxShadow: "0 1px 3px rgba(0,0,0,0.12)",
};
const packagingBtnCount: React.CSSProperties = {
  fontSize: 10,
  fontWeight: 700,
  padding: "1px 5px",
  borderRadius: 8,
  background: "rgba(3,169,244,0.15)",
  color: "#0277bd",
};
const priorChoiceRow: React.CSSProperties = {
  marginTop: 8,
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: 8,
  flexWrap: "wrap",
};
const priorToggle: React.CSSProperties = {
  display: "flex",
  gap: 0,
  borderRadius: 6,
  overflow: "hidden",
  border: "1px solid var(--ha-divider)",
};
const priorBtn: React.CSSProperties = {
  padding: "5px 12px",
  fontSize: 11,
  fontWeight: 500,
  background: "transparent",
  color: "var(--ha-secondary-text)",
  border: "none",
  cursor: "pointer",
};
const priorBtnActive: React.CSSProperties = {
  ...priorBtn,
  background: "var(--ha-primary-color)",
  color: "#fff",
  fontWeight: 600,
};
const priorAutoNote: React.CSSProperties = {
  marginTop: 8,
  fontSize: 11,
  color: "var(--ha-secondary-text)",
  fontStyle: "italic",
  lineHeight: 1.4,
};
const pushLabel: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 6,
  fontSize: 12,
  color: "var(--ha-primary-text)",
  cursor: "pointer",
};
const pushDisclaimer: React.CSSProperties = {
  fontSize: 10,
  color: "var(--ha-secondary-text)",
  paddingLeft: 22,
};
const footer: React.CSSProperties = {
  display: "flex",
  gap: 8,
  justifyContent: "flex-end",
};
const cancelBtn: React.CSSProperties = {
  padding: "8px 16px",
  fontSize: 13,
  fontWeight: 500,
  background: "transparent",
  color: "var(--ha-primary-text)",
  border: "1px solid var(--ha-divider)",
  borderRadius: 6,
  cursor: "pointer",
};
const primaryBtn = (enabled: boolean): React.CSSProperties => ({
  padding: "8px 18px",
  fontSize: 13,
  fontWeight: 600,
  background: enabled ? "var(--ha-primary-color)" : "rgba(0,0,0,0.12)",
  color: enabled ? "#fff" : "var(--ha-disabled-text)",
  border: "none",
  borderRadius: 6,
  cursor: enabled ? "pointer" : "not-allowed",
});
const chipRow: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 6,
  flexWrap: "wrap",
};
const chipRowLabel: React.CSSProperties = {
  fontSize: 10,
  fontWeight: 600,
  color: "var(--ha-secondary-text)",
  textTransform: "uppercase",
  letterSpacing: "0.06em",
  minWidth: 36,
};
const chip: React.CSSProperties = {
  padding: "4px 10px",
  fontSize: 11,
  fontWeight: 500,
  background: "rgba(0,0,0,0.05)",
  color: "var(--ha-primary-text)",
  border: "1px solid var(--ha-divider)",
  borderRadius: 14,
  cursor: "pointer",
};
const chipActive: React.CSSProperties = {
  ...chip,
  background: "rgba(3,169,244,0.15)",
  color: "var(--ha-primary-color)",
  borderColor: "rgba(3,169,244,0.4)",
  fontWeight: 600,
};
