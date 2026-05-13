import { useRef, useState } from "react";
import { ColorStatus, ColorStock, Filament, addColor, deleteColor, updateColor } from "../api";
import { getColorSuggestions, lookupColorHex } from "../colorMap";

interface Props {
  filament: Filament;
  onManageStock: () => void;
  onUpdate: () => Promise<void>;
}

/** Brand background colors to match their actual logos */
const BRAND_BG: Record<string, string> = {
  SUNLU:      "#00a8a8",
  Inslogic:   "#ffffff",
  "Bambu Lab": "#ffffff",
  Bambu:      "#ffffff",
  GolGeo:     "#f5e400",
};

function BrandLogo({ url, brand }: { url: string; brand: string }) {
  const [failed, setFailed] = useState(false);
  const bg = BRAND_BG[brand] ?? "#2a2a2c";

  if (!url || failed) {
    return (
      <div style={{ ...logoWrap, background: bg }}>
        <span style={{ fontSize: 10, fontWeight: 700, color: "#fff", letterSpacing: "0.03em" }}>
          {brand.slice(0, 2).toUpperCase()}
        </span>
      </div>
    );
  }

  return (
    <div style={{ ...logoWrap, background: bg }}>
      <img
        src={url}
        alt={brand}
        style={{ width: "100%", height: "100%", objectFit: "contain", padding: 4 }}
        onError={() => setFailed(true)}
      />
    </div>
  );
}

const logoWrap: React.CSSProperties = {
  width: 36,
  height: 36,
  borderRadius: 8,
  flexShrink: 0,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  overflow: "hidden",
};

function getMaterialColor(type: string): string {
  const map: Record<string, string> = {
    PLA: "#4caf50", PETG: "#03a9f4", ASA: "#ff9800",
    ABS: "#f44336", PA: "#9c27b0", TPU: "#e91e63", PLA_CF: "#00bcd4",
  };
  return map[type] ?? "#607d8b";
}

export default function FilamentCard({ filament, onManageStock, onUpdate }: Props) {
  const inStockQty  = filament.colors.filter(c => c.status === "in_stock").reduce((s, c) => s + (c.quantity - (c.quantity_used ?? 0)), 0);
  const orderedQty  = filament.colors.filter(c => c.status === "ordered").reduce((s, c) => s + c.quantity, 0);
  const isLow       = inStockQty <= filament.low_stock_threshold;
  const matColor    = getMaterialColor(filament.filament_type);

  return (
    <div className="ha-card" style={cardWrap}>
      {/* colored top strip */}
      <div style={{ height: 3, background: matColor }} />

      {/* header */}
      <div style={headerRow}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <BrandLogo url={filament.brand_logo_url} brand={filament.brand} />
          <div>
            <p style={cardTitle}>
              {filament.brand} <span style={{ color: matColor }}>{filament.material}</span>
            </p>
            <p style={cardSubtitle}>{filament.filament_type}</p>
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 4, alignItems: "flex-end" }}>
          {/* In Stock */}
          <div style={stockChip(isLow)}>
            {isLow && inStockQty === 0 ? null : isLow && <span style={{ fontSize: 9 }}>⚠ </span>}
            <span style={{ fontSize: 18, fontWeight: 300, lineHeight: 1 }}>{inStockQty}</span>
            <span style={{ fontSize: 9, opacity: 0.7 }}>in stock</span>
          </div>
          {/* Ordered */}
          {orderedQty > 0 && (
            <div style={orderedChip}>
              <span style={{ fontSize: 9 }}>⏳</span>
              <span style={{ fontSize: 13, fontWeight: 400, lineHeight: 1 }}>{orderedQty}</span>
              <span style={{ fontSize: 9, opacity: 0.7 }}>ordered</span>
            </div>
          )}
        </div>
      </div>

      {/* specs */}
      <div style={specsRow}>
        <SpecBadge label={filament.filament_type} color={matColor} />
        {filament.nozzle_temp_min && filament.nozzle_temp_max &&
          <SpecBadge label={`${filament.nozzle_temp_min}–${filament.nozzle_temp_max}°C`} />}
        {filament.bed_temp && <SpecBadge label={`Bed ${filament.bed_temp}°C`} />}
        {filament.density && <SpecBadge label={`${filament.density} g/cm³`} />}
      </div>

      {/* ── Inline color rows ── */}
      <div style={colorsSection}>
        <div style={colorsSectionHeader}>
          <span style={sectionLabel}>Colors in Stock</span>
        </div>

        {filament.colors.length === 0 && (
          <p style={noColorsText}>No colors added</p>
        )}

        {filament.colors.map((c) => (
          <ColorRow key={c.id} color={c} onUpdate={onUpdate} />
        ))}

        <AddColorInline filamentId={filament.id} onUpdate={onUpdate} />
      </div>

      {/* actions */}
      <div style={actionRow}>
        <button onClick={onManageStock} style={manageBtn}>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 20V10M6 20V14M18 20V4" />
          </svg>
          History & Log
        </button>
        {filament.amazon_url && (
          <a href={filament.amazon_url} target="_blank" rel="noopener" style={buyBtn}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
              <polyline points="15 3 21 3 21 9" /><line x1="10" y1="14" x2="21" y2="3" />
            </svg>
            Buy
          </a>
        )}
      </div>
    </div>
  );
}

const STATUS_CFG: Record<ColorStatus, { label: string; color: string; bg: string }> = {
  in_stock:    { label: "In Stock",    color: "#4caf50", bg: "rgba(76,175,80,0.15)"  },
  ordered:     { label: "Ordered",     color: "#03a9f4", bg: "rgba(3,169,244,0.15)"  },
  out_of_stock:{ label: "Out of Stock",color: "#f44336", bg: "rgba(244,67,54,0.15)"  },
};

/* ── Editable color entity row ────────────────────────────────────────────── */
function ColorRow({ color, onUpdate }: { color: ColorStock; onUpdate: () => Promise<void> }) {
  const [hovered, setHovered] = useState(false);
  const [qty, setQty] = useState(color.quantity);
  const [qtyUsed, setQtyUsed] = useState(color.quantity_used ?? 0);
  const [status, setStatus] = useState<ColorStatus>(color.status ?? "in_stock");
  const [orderId, setOrderId] = useState(color.order_id ?? "");
  const [editingOrderId, setEditingOrderId] = useState(false);
  const [saving, setSaving] = useState(false);

  const remaining = qty - qtyUsed;

  const handleQtyChange = async (newQty: number) => {
    setQty(newQty);
    setSaving(true);
    await updateColor(color.id, { quantity: newQty });
    await onUpdate();
    setSaving(false);
  };

  const handleMarkUsed = async () => {
    const newUsed = Math.min(qtyUsed + 1, qty);
    setQtyUsed(newUsed);
    setSaving(true);
    await updateColor(color.id, { quantity_used: newUsed });
    if (newUsed >= qty) {
      setStatus("out_of_stock");
      await updateColor(color.id, { quantity_used: newUsed, status: "out_of_stock" });
    }
    await onUpdate();
    setSaving(false);
  };

  const handleUndoUsed = async () => {
    const newUsed = Math.max(qtyUsed - 1, 0);
    setQtyUsed(newUsed);
    setSaving(true);
    if (status === "out_of_stock" && newUsed < qty) {
      setStatus("in_stock");
      await updateColor(color.id, { quantity_used: newUsed, status: "in_stock" });
    } else {
      await updateColor(color.id, { quantity_used: newUsed });
    }
    await onUpdate();
    setSaving(false);
  };

  const handleReceive = async () => {
    setStatus("in_stock");
    await updateColor(color.id, { status: "in_stock" });
    await onUpdate();
  };

  const handleMarkOrdered = async () => {
    setStatus("ordered");
    await updateColor(color.id, { status: "ordered" });
    await onUpdate();
  };

  const handleMarkOutOfStock = async () => {
    setStatus("out_of_stock");
    await updateColor(color.id, { status: "out_of_stock" });
    await onUpdate();
  };

  const handleOrderIdSave = async () => {
    setEditingOrderId(false);
    await updateColor(color.id, { order_id: orderId || null } as never);
    await onUpdate();
  };

  const handleDelete = async () => {
    if (!confirm(`Remove "${color.color_name}"?`)) return;
    await deleteColor(color.id);
    await onUpdate();
  };

  const cfg = STATUS_CFG[status];
  const amazonUrl = orderId ? `https://www.amazon.com/your-orders/order-details?orderID=${orderId}` : null;

  return (
    <div
      className="ha-entity-row"
      style={{ ...colorEntityRow, flexWrap: "wrap", background: hovered ? "rgba(0,0,0,0.025)" : "transparent", transition: "background 0.15s" }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <div style={{ display: "flex", alignItems: "center", width: "100%", gap: 0, minHeight: 44 }}>
        {/* color swatch */}
        <div style={{ ...dot, background: color.color_hex }} />

        {/* name */}
        <span style={{ flex: 1, fontSize: 13, fontWeight: 500 }}>{color.color_name}</span>

        {/* ══ IN STOCK layout ══ */}
        {status === "in_stock" && (
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            {/* remaining spools — big */}
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", minWidth: 36 }}>
              <span style={{
                fontSize: 22, fontWeight: 700, lineHeight: 1,
                color: remaining <= 0 ? "var(--ha-error)" : saving ? "var(--ha-secondary-text)" : "var(--ha-primary-text)",
              }}>
                {remaining}
              </span>
              <span style={{ fontSize: 9, color: "var(--ha-secondary-text)", marginTop: 1 }}>
                {remaining === 1 ? "spool" : "spools"}
              </span>
            </div>

            {/* used progress bar — always rendered */}
            <div style={{ display: "flex", flexDirection: "column", gap: 3, alignItems: "flex-end" }}>
              <div style={{ width: 64, height: 4, borderRadius: 2, background: "rgba(0,0,0,0.08)", overflow: "hidden" }}>
                <div style={{
                  height: "100%", borderRadius: 2,
                  width: `${qty > 0 ? (qtyUsed / qty) * 100 : 0}%`,
                  background: qtyUsed >= qty ? "var(--ha-error)" : "var(--ha-warning)",
                  transition: "width 0.3s",
                }} />
              </div>
              <span style={{ fontSize: 9, color: "var(--ha-secondary-text)" }}>
                {qtyUsed}/{qty} used
              </span>
            </div>

            {/* action buttons — always visible */}
            <div style={{ display: "flex", gap: 4, opacity: hovered ? 1 : 0.45, transition: "opacity 0.15s" }}>
              <button
                onClick={handleUndoUsed}
                disabled={qtyUsed <= 0}
                style={{ ...undoBtn, opacity: qtyUsed <= 0 ? 0.3 : 1, cursor: qtyUsed <= 0 ? "default" : "pointer" }}
                title="Undo last use"
              >↩</button>
              <button
                onClick={handleMarkUsed}
                disabled={remaining <= 0}
                style={{ ...useBtn, opacity: remaining <= 0 ? 0.4 : 1, cursor: remaining <= 0 ? "not-allowed" : "pointer" }}
                title="Mark 1 spool as used"
              >− Use</button>
            </div>

            {/* delete — fades in on hover */}
            <button onClick={handleDelete} style={{ ...deleteBtn, opacity: hovered ? 1 : 0, transition: "opacity 0.15s" }} title="Remove">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="3 6 5 6 21 6" /><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
              </svg>
            </button>
          </div>
        )}

        {/* ══ ORDERED layout ══ */}
        {status === "ordered" && (
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            {/* qty stepper — always visible, dimmed when not hovered */}
            <div style={{ display: "flex", alignItems: "center", gap: 4, opacity: hovered ? 1 : 0.6, transition: "opacity 0.15s" }}>
              <button onClick={() => handleQtyChange(Math.max(0, qty - 1))} style={stepBtn}>−</button>
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", minWidth: 32 }}>
                <span style={{ fontSize: 18, fontWeight: 700, lineHeight: 1 }}>{qty}</span>
                <span style={{ fontSize: 9, color: "var(--ha-secondary-text)" }}>ordered</span>
              </div>
              <button onClick={() => handleQtyChange(qty + 1)} style={stepBtn}>+</button>
            </div>
            {/* Arrived button — always visible */}
            <button onClick={handleReceive} style={receiveBtn}>
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              Arrived
            </button>
            <button onClick={handleDelete} style={{ ...deleteBtn, opacity: hovered ? 1 : 0, transition: "opacity 0.15s" }} title="Remove">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="3 6 5 6 21 6" /><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
              </svg>
            </button>
          </div>
        )}

        {/* ══ OUT OF STOCK layout ══ */}
        {status === "out_of_stock" && (
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 11, color: "var(--ha-error)", fontWeight: 600 }}>Out of stock</span>
            <button onClick={handleMarkOrdered} style={reorderBtn}>↺ Reorder</button>
            <button onClick={handleDelete} style={{ ...deleteBtn, opacity: hovered ? 1 : 0, transition: "opacity 0.15s" }} title="Remove">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="3 6 5 6 21 6" /><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
              </svg>
            </button>
          </div>
        )}
      </div>

      {/* ── Order ID sub-row (ordered only) ── */}
      {status === "ordered" && (
        <div style={{ display: "flex", alignItems: "center", gap: 5, paddingLeft: 22, paddingBottom: 6, width: "100%" }}>
          {editingOrderId ? (
            <>
              <input
                autoFocus
                value={orderId}
                onChange={(e) => setOrderId(e.target.value)}
                onBlur={handleOrderIdSave}
                onKeyDown={(e) => { if (e.key === "Enter") handleOrderIdSave(); if (e.key === "Escape") setEditingOrderId(false); }}
                placeholder="Order # e.g. 113-1234567-8901234"
                style={{ ...addInput, flex: 1, fontSize: 10, padding: "2px 6px" }}
              />
              <button onMouseDown={handleOrderIdSave} style={{ ...addSubmitBtn, fontSize: 10, padding: "2px 7px" }}>Save</button>
            </>
          ) : orderId ? (
            <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
              <span style={{ fontSize: 9, color: "var(--ha-secondary-text)" }}>Order:</span>
              {amazonUrl ? (
                <a href={amazonUrl} target="_blank" rel="noopener" style={{ fontSize: 10, color: "var(--ha-primary-color)", fontFamily: "monospace", textDecoration: "none" }}>
                  {orderId}
                </a>
              ) : (
                <span style={{ fontSize: 10, color: "var(--ha-secondary-text)", fontFamily: "monospace" }}>{orderId}</span>
              )}
              <button onClick={() => setEditingOrderId(true)} style={{ background: "none", border: "none", color: "var(--ha-secondary-text)", cursor: "pointer", fontSize: 11, padding: "0 2px", opacity: hovered ? 1 : 0, transition: "opacity 0.15s" }}>✎</button>
            </div>
          ) : (
            <button onClick={() => setEditingOrderId(true)} style={{ background: "none", border: "none", color: "var(--ha-secondary-text)", cursor: "pointer", fontSize: 10, padding: 0, display: "flex", alignItems: "center", gap: 3, opacity: hovered ? 0.7 : 0.3, transition: "opacity 0.15s" }}>
              + Add order #
            </button>
          )}
        </div>
      )}
    </div>
  );
}

/* ── Add color inline row ─────────────────────────────────────────────────── */
function AddColorInline({ filamentId, onUpdate }: { filamentId: number; onUpdate: () => Promise<void> }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [hex, setHex] = useState("#808080");
  const [qty, setQty] = useState(1);
  const [suggestions, setSuggestions] = useState<Array<{ name: string; hex: string }>>([]);
  const [showSug, setShowSug] = useState(false);
  const [saving, setSaving] = useState(false);
  const sugRef = useRef<HTMLDivElement>(null);

  const handleNameChange = (v: string) => {
    setName(v);
    const found = lookupColorHex(v);
    if (found) setHex(found);
    const sugg = getColorSuggestions(v);
    setSuggestions(sugg);
    setShowSug(sugg.length > 0 && v.length > 0);
  };

  const pickSuggestion = (n: string, h: string) => {
    setName(n.charAt(0).toUpperCase() + n.slice(1));
    setHex(h);
    setShowSug(false);
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    await addColor(filamentId, { color_name: name, color_hex: hex, quantity: qty, status: "in_stock" });
    setName(""); setHex("#808080"); setQty(1); setOpen(false);
    await onUpdate();
    setSaving(false);
  };

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} style={addRowBtn}>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        Add color
      </button>
    );
  }

  return (
    <form onSubmit={handleAdd} style={addForm}>
      {/* color picker dot */}
      <label style={{ cursor: "pointer", flexShrink: 0 }}>
        <div style={{ ...dot, background: hex, cursor: "pointer", border: "2px solid rgba(255,255,255,0.3)" }} />
        <input type="color" value={hex} onChange={(e) => setHex(e.target.value)} style={{ display: "none" }} />
      </label>

      {/* name input with suggestions */}
      <div style={{ position: "relative", flex: 1 }}>
        <input
          type="text" value={name} onChange={(e) => handleNameChange(e.target.value)}
          onFocus={() => suggestions.length > 0 && setShowSug(true)}
          onBlur={() => setTimeout(() => setShowSug(false), 150)}
          placeholder="Color name…"
          style={addInput} autoFocus required
        />
        {showSug && (
          <div ref={sugRef} style={sugBox}>
            {suggestions.map((s) => (
              <div key={s.name} style={sugItem} onMouseDown={() => pickSuggestion(s.name, s.hex)}>
                <div style={{ width: 10, height: 10, borderRadius: 2, background: s.hex, border: "1px solid rgba(255,255,255,0.15)", flexShrink: 0 }} />
                <span style={{ flex: 1 }}>{s.name}</span>
                <span style={{ opacity: 0.4, fontSize: 10, fontFamily: "monospace" }}>{s.hex}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* qty */}
      <input type="number" min={0} value={qty} onChange={(e) => setQty(Number(e.target.value))}
        style={{ ...addInput, width: 44, textAlign: "center" }} />

      {/* submit */}
      <button type="submit" disabled={saving} style={addSubmitBtn}>
        {saving ? "…" : "Add"}
      </button>

      {/* cancel */}
      <button type="button" onClick={() => setOpen(false)} style={cancelBtn}>✕</button>
    </form>
  );
}

function SpecBadge({ label, color }: { label: string; color?: string }) {
  return (
    <span style={{
      display: "inline-flex", alignItems: "center",
      padding: "2px 8px", borderRadius: 12,
      fontSize: 11, fontWeight: 500,
      background: color ? `${color}15` : "rgba(0,0,0,0.04)",
      color: color ?? "var(--ha-secondary-text)",
      border: `1px solid ${color ? `${color}30` : "transparent"}`,
    }}>
      {label}
    </span>
  );
}

/* ─── Styles ─────────────────────────────────────────────────────────────── */
const cardWrap: React.CSSProperties = {
  display: "flex", flexDirection: "column", background: "var(--ha-card-bg)",
};
const headerRow: React.CSSProperties = {
  display: "flex", justifyContent: "space-between", alignItems: "flex-start",
  padding: "14px 16px 8px",
};
const cardTitle: React.CSSProperties = {
  fontSize: 14, fontWeight: 500, lineHeight: 1.3, color: "var(--ha-primary-text)",
};
const cardSubtitle: React.CSSProperties = {
  fontSize: 12, color: "var(--ha-secondary-text)", marginTop: 1,
};
const stockChip = (low: boolean): React.CSSProperties => ({
  display: "flex", flexDirection: "column", alignItems: "center",
  padding: "5px 10px", borderRadius: 8,
  background: low ? "var(--ha-error-bg)" : "rgba(0,0,0,0.04)",
  color: low ? "var(--ha-error)" : "var(--ha-primary-text)",
  minWidth: 48, flexShrink: 0,
});
const orderedChip: React.CSSProperties = {
  display: "flex", flexDirection: "column", alignItems: "center",
  padding: "3px 8px", borderRadius: 8, gap: 1,
  background: "rgba(3,169,244,0.12)",
  color: "var(--ha-primary-color)",
  minWidth: 48, flexShrink: 0,
};

const specsRow: React.CSSProperties = {
  display: "flex", flexWrap: "wrap", gap: 4, padding: "0 16px 10px",
};
const colorsSection: React.CSSProperties = {
  borderTop: "1px solid var(--ha-divider)",
};
const colorsSectionHeader: React.CSSProperties = {
  padding: "8px 16px 4px",
};
const sectionLabel: React.CSSProperties = {
  fontSize: 11, fontWeight: 500, color: "var(--ha-secondary-text)",
  textTransform: "uppercase", letterSpacing: "0.06em",
};
const noColorsText: React.CSSProperties = {
  fontSize: 12, color: "var(--ha-disabled-text)",
  padding: "6px 16px 4px",
};
const colorEntityRow: React.CSSProperties = {
  padding: "7px 16px", minHeight: 40,
};
const dot: React.CSSProperties = {
  width: 12, height: 12, borderRadius: "50%",
  border: "1px solid rgba(0,0,0,0.15)",
  flexShrink: 0, marginRight: 10,
};
const stepBtn: React.CSSProperties = {
  width: 20, height: 20,
  display: "flex", alignItems: "center", justifyContent: "center",
  background: "rgba(0,0,0,0.06)", border: "none",
  borderRadius: 4, color: "var(--ha-primary-text)",
  fontSize: 14, cursor: "pointer", lineHeight: 1,
};
const deleteBtn: React.CSSProperties = {
  background: "none", border: "none",
  color: "var(--ha-disabled-text)", cursor: "pointer",
  padding: "2px 4px", borderRadius: 4, marginLeft: 4,
  display: "flex", alignItems: "center",
};
const addRowBtn: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 5,
  width: "100%", padding: "8px 16px",
  background: "none", border: "none",
  color: "var(--ha-primary-color)", fontSize: 12,
  cursor: "pointer", textAlign: "left",
  borderTop: "1px solid var(--ha-divider)",
};
const addForm: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 6,
  padding: "6px 16px 8px",
  borderTop: "1px solid var(--ha-divider)",
  background: "rgba(0,0,0,0.01)",
};
const addInput: React.CSSProperties = {
  padding: "5px 8px", fontSize: 12,
  background: "#fff",
  border: "1px solid var(--ha-divider)",
  borderRadius: 4, color: "var(--ha-primary-text)", outline: "none",
};
const addSubmitBtn: React.CSSProperties = {
  padding: "5px 10px", background: "var(--ha-primary-color)",
  color: "#fff", border: "none", borderRadius: 4,
  fontSize: 12, fontWeight: 500, cursor: "pointer",
};
const cancelBtn: React.CSSProperties = {
  background: "none", border: "none",
  color: "var(--ha-disabled-text)", cursor: "pointer",
  fontSize: 13, padding: "2px 4px",
};
const actionRow: React.CSSProperties = {
  display: "flex", gap: 8, padding: "10px 16px 14px",
  borderTop: "1px solid var(--ha-divider)", marginTop: "auto",
};
const manageBtn: React.CSSProperties = {
  flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 5,
  padding: "7px 12px",
  background: "var(--ha-primary-color-light)", color: "var(--ha-primary-color)",
  border: "none", borderRadius: 4, fontSize: 13, fontWeight: 500, cursor: "pointer",
};
const buyBtn: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 5, padding: "7px 12px",
  background: "rgba(255,152,0,0.12)", color: "var(--ha-warning)",
  border: "none", borderRadius: 4, fontSize: 13, fontWeight: 500,
  textDecoration: "none", cursor: "pointer",
};
const receiveBtn: React.CSSProperties = {
  display: "inline-flex", alignItems: "center", gap: 4,
  padding: "5px 10px", borderRadius: 6,
  fontSize: 11, fontWeight: 600,
  background: "#c2f2c1", color: "#036730",
  border: "1px solid #93da98",
  cursor: "pointer", whiteSpace: "nowrap",
};
const useBtn: React.CSSProperties = {
  display: "inline-flex", alignItems: "center", gap: 3,
  padding: "5px 10px", borderRadius: 6,
  fontSize: 11, fontWeight: 600,
  background: "#ffe0c8", color: "#7e2900",
  border: "1px solid #ffbb89",
  whiteSpace: "nowrap",
};
const undoBtn: React.CSSProperties = {
  display: "inline-flex", alignItems: "center",
  padding: "5px 7px", borderRadius: 6,
  fontSize: 12,
  background: "#e6e6e6", color: "var(--ha-secondary-text)",
  border: "1px solid #cccccc",
  cursor: "pointer",
};
const reorderBtn: React.CSSProperties = {
  display: "inline-flex", alignItems: "center", gap: 4,
  padding: "5px 10px", borderRadius: 6,
  fontSize: 11, fontWeight: 600,
  background: "#dff3fc", color: "#006787",
  border: "1px solid #7bd4fb",
  cursor: "pointer", whiteSpace: "nowrap",
};
const sugBox: React.CSSProperties = {
  position: "absolute", top: "100%", left: 0, right: 0,
  background: "#fff", border: "1px solid var(--ha-divider)",
  borderRadius: 4, marginTop: 2, zIndex: 10,
  maxHeight: 150, overflowY: "auto", boxShadow: "0 8px 24px rgba(0,0,0,0.15)",
};
const sugItem: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 7,
  padding: "5px 10px", cursor: "pointer", fontSize: 12,
};
