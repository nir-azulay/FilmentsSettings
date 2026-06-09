import { useEffect, useRef, useState } from "react";
import { ColorStatus, ColorStock, Filament, StockEntry, addColor, addStockEvent, deleteColor, fetchHistory, updateColor } from "../api";
import { getColorSuggestions, lookupColorHex } from "../colorMap";
import BrandLogo from "./BrandLogo";
import { filamentAvailableSpools } from "../stockUtils";
import DeleteColorModal from "./DeleteColorModal";
import TrashIconButton from "./TrashIconButton";

interface Props {
  filament: Filament;
  onClose: () => void;
  onUpdate: () => Promise<void>;
  onRequestDeleteFilament: () => void;
}

export default function StockManager({ filament, onClose, onUpdate, onRequestDeleteFilament }: Props) {
  const [history, setHistory] = useState<StockEntry[]>([]);
  const [quantity, setQuantity] = useState(1);
  const [eventType, setEventType] = useState<"purchase" | "used" | "adjustment">("purchase");
  const [selectedColorId, setSelectedColorId] = useState<number | null>(
    filament.colors.length > 0 ? filament.colors[0].id : null
  );
  const [notes, setNotes] = useState("");
  const [newColorName, setNewColorName] = useState("");
  const [newColorHex, setNewColorHex] = useState("#808080");
  const [newColorQty, setNewColorQty] = useState(0);
  const [showAddColor, setShowAddColor] = useState(false);
  const [colorToDelete, setColorToDelete] = useState<ColorStock | null>(null);
  const [deletingColor, setDeletingColor] = useState(false);
  const [suggestions, setSuggestions] = useState<Array<{ name: string; hex: string }>>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  useEffect(() => { fetchHistory(filament.id).then(setHistory); }, [filament.id]);

  const handleColorNameChange = (value: string) => {
    setNewColorName(value);
    const hex = lookupColorHex(value);
    if (hex) setNewColorHex(hex);
    const sugg = getColorSuggestions(value);
    setSuggestions(sugg);
    setShowSuggestions(sugg.length > 0 && value.length > 0);
  };

  const handleSuggestionClick = (name: string, hex: string) => {
    setNewColorName(name.charAt(0).toUpperCase() + name.slice(1));
    setNewColorHex(hex);
    setShowSuggestions(false);
  };

  const handleStockSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const qty = eventType === "used" ? -Math.abs(quantity) : quantity;
    await addStockEvent(filament.id, { quantity: qty, event_type: eventType, color_stock_id: selectedColorId, notes });
    setNotes(""); setQuantity(1);
    setHistory(await fetchHistory(filament.id));
    await onUpdate();
  };

  const handleAddColor = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newColorName.trim()) return;
    await addColor(filament.id, { color_name: newColorName, color_hex: newColorHex, quantity: newColorQty });
    setNewColorName(""); setNewColorHex("#808080"); setNewColorQty(0);
    setShowAddColor(false);
    await onUpdate();
  };

  const executeDeleteColor = async () => {
    if (!colorToDelete || deletingColor) return;
    setDeletingColor(true);
    try {
      await deleteColor(colorToDelete.id);
      setColorToDelete(null);
      await onUpdate();
    } finally {
      setDeletingColor(false);
    }
  };

  const handleEditColorQty = async (color: ColorStock, newQty: number) => {
    await updateColor(color.id, { quantity: newQty });
    await onUpdate();
  };

  return (
    <div style={overlay} onClick={onClose}>
      <div style={dialog} onClick={(e) => e.stopPropagation()}>

        {/* ── Dialog header — like HA dialog ── */}
        <div style={dialogHeader}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <BrandLogo brand={filament.brand} url={filament.brand_logo_url} size={28} />
            <div>
              <h2 style={dialogTitle}>{filament.brand} {filament.material}</h2>
              <p style={dialogSubtitle}>{filament.filament_type} · {filamentAvailableSpools(filament)} spools available</p>
            </div>
          </div>
          <button onClick={onClose} style={closeBtn} aria-label="Close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* ── Colors section ── */}
        <section style={section}>
          <div style={sectionHeaderRow}>
            <span style={sectionLabel}>Colors in Stock</span>
            <button onClick={() => setShowAddColor(!showAddColor)} style={chipActionBtn}>
              {showAddColor ? "Cancel" : "+ Add Color"}
            </button>
          </div>

          {showAddColor && (
            <form onSubmit={handleAddColor} style={addColorForm}>
              <input type="color" value={newColorHex} onChange={(e) => setNewColorHex(e.target.value)} style={colorPicker} />
              <div style={{ position: "relative", flex: 1 }}>
                <input
                  type="text" value={newColorName}
                  onChange={(e) => handleColorNameChange(e.target.value)}
                  onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                  onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
                  placeholder="Color name…"
                  style={{ ...inputStyle, width: "100%" }} required
                />
                {showSuggestions && (
                  <div ref={suggestionsRef} style={suggestionsList}>
                    {suggestions.map((s) => (
                      <div key={s.name} style={suggestionItem} onMouseDown={() => handleSuggestionClick(s.name, s.hex)}>
                        <div style={{ width: 11, height: 11, borderRadius: 2, background: s.hex, border: "1px solid var(--ha-divider)", flexShrink: 0 }} />
                        <span style={{ flex: 1 }}>{s.name}</span>
                        <span style={{ opacity: 0.4, fontSize: 11, fontFamily: "monospace" }}>{s.hex}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <input type="number" min={0} value={newColorQty} onChange={(e) => setNewColorQty(Number(e.target.value))}
                style={{ ...inputStyle, width: 56, textAlign: "center" }} placeholder="Qty" />
              <button type="submit" style={primaryBtn}>Add</button>
            </form>
          )}

          {filament.colors.length === 0 ? (
            <p style={emptyText}>No colors yet. Add your first one above.</p>
          ) : (
            <div style={colorList}>
              {filament.colors.map((c) => (
                <div key={c.id} className="ha-entity-row">
                  <div style={{ width: 12, height: 12, borderRadius: "50%", background: c.color_hex, border: "1px solid var(--ha-divider)", flexShrink: 0, marginRight: 10 }} />
                  <span style={{ flex: 1, fontSize: 13 }}>{c.color_name}</span>
                  <StatusSelect colorId={c.id} status={(c.status ?? "in_stock") as ColorStatus} onUpdate={onUpdate} />
                  <input type="number" min={0} value={c.quantity}
                    onChange={(e) => handleEditColorQty(c, Number(e.target.value))}
                    style={{ ...inputStyle, width: 52, textAlign: "center", fontWeight: 600, marginRight: 6 }}
                  />
                  <TrashIconButton onClick={() => setColorToDelete(c)} title="Delete color" />
                </div>
              ))}
            </div>
          )}
        </section>

        {/* ── Log stock section ── */}
        <section style={section}>
          <span style={sectionLabel}>Log Stock Change</span>
          <form onSubmit={handleStockSubmit} style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 10 }}>
            <div style={formRow}>
              <select value={eventType} onChange={(e) => setEventType(e.target.value as typeof eventType)} style={selectStyle}>
                <option value="purchase">+ Purchase</option>
                <option value="used">− Used</option>
                <option value="adjustment">~ Adjustment</option>
              </select>
              {filament.colors.length > 0 && (
                <select value={selectedColorId ?? ""} onChange={(e) => setSelectedColorId(e.target.value ? Number(e.target.value) : null)} style={selectStyle}>
                  <option value="">All colors</option>
                  {filament.colors.map((c) => <option key={c.id} value={c.id}>{c.color_name}</option>)}
                </select>
              )}
              <input type="number" min={1} value={quantity} onChange={(e) => setQuantity(Number(e.target.value))}
                style={{ ...inputStyle, width: 60, textAlign: "center" }} />
            </div>
            <div style={formRow}>
              <input type="text" value={notes} onChange={(e) => setNotes(e.target.value)}
                placeholder="Notes (optional)" style={{ ...inputStyle, flex: 1 }} />
              <button type="submit" style={primaryBtn}>Log</button>
            </div>
          </form>
        </section>

        {/* ── History section ── */}
        <section style={{ ...section, borderBottom: "none" }}>
          <span style={sectionLabel}>History</span>
          <div style={{ maxHeight: 200, overflowY: "auto", marginTop: 8 }}>
            {history.length === 0 && <p style={emptyText}>No history yet.</p>}
            {history.map((entry) => {
              const color = filament.colors.find((c) => c.id === entry.color_stock_id);
              return (
                <div key={entry.id} className="ha-entity-row">
                  <span style={eventBadge(entry.event_type)}>
                    {entry.event_type === "purchase" ? "+" : entry.event_type === "used" ? "−" : "~"}
                    {Math.abs(entry.quantity)}
                  </span>
                  {color && <div style={{ width: 8, height: 8, borderRadius: "50%", background: color.color_hex, marginLeft: 6, flexShrink: 0 }} />}
                  <span style={{ flex: 1, fontSize: 12, color: "var(--ha-secondary-text)", marginLeft: 8 }}>
                    {entry.notes || entry.event_type}
                  </span>
                  <span style={{ fontSize: 11, color: "var(--ha-disabled-text)" }}>
                    {new Date(entry.created_at).toLocaleDateString()}
                  </span>
                </div>
              );
            })}
          </div>
        </section>

        <section style={{ ...section, borderBottom: "none" }}>
          <button type="button" onClick={onRequestDeleteFilament} style={deleteFilamentBtn}>
            Delete filament
          </button>
          <p style={deleteFilamentHint}>Removes this entry, all colors, and history permanently.</p>
        </section>
      </div>

      {colorToDelete && (
        <DeleteColorModal
          colorName={colorToDelete.color_name}
          confirming={deletingColor}
          onCancel={() => !deletingColor && setColorToDelete(null)}
          onConfirm={executeDeleteColor}
        />
      )}
    </div>
  );
}

const STATUS_CFG: Record<ColorStatus, { label: string; color: string; bg: string }> = {
  in_stock:    { label: "In Stock",    color: "#4caf50", bg: "rgba(76,175,80,0.15)"  },
  ordered:     { label: "Ordered",     color: "#03a9f4", bg: "rgba(3,169,244,0.15)"  },
  out_of_stock:{ label: "Out of Stock",color: "#f44336", bg: "rgba(244,67,54,0.15)"  },
};

function StatusSelect({ colorId, status, onUpdate }: { colorId: number; status: ColorStatus; onUpdate: () => Promise<void> }) {
  const handleChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    await updateColor(colorId, { status: e.target.value as ColorStatus });
    await onUpdate();
  };
  const cfg = STATUS_CFG[status];
  return (
    <select
      value={status}
      onChange={handleChange}
      style={{
        fontSize: 11, fontWeight: 600, padding: "2px 5px",
        borderRadius: 10, border: `1px solid ${cfg.color}40`,
        background: cfg.bg, color: cfg.color,
        cursor: "pointer", marginRight: 6, outline: "none",
      }}
    >
      <option value="in_stock">In Stock</option>
      <option value="ordered">Ordered</option>
      <option value="out_of_stock">Out of Stock</option>
    </select>
  );
}

/* ─── Styles ─────────────────────────────────────────────────────────────── */
const overlay: React.CSSProperties = {
  position: "fixed", inset: 0,
  background: "var(--ha-overlay-bg)",
  backdropFilter: "blur(4px)",
  display: "flex", justifyContent: "center", alignItems: "center",
  zIndex: 1000,
  animation: "fadeIn 0.15s ease-out",
};
const dialog: React.CSSProperties = {
  background: "var(--ha-card-bg)",
  borderRadius: "var(--ha-card-radius)",
  width: "92%", maxWidth: 560, maxHeight: "90vh",
  overflowY: "auto",
  boxShadow: "var(--ha-dialog-shadow)",
  animation: "slideUp 0.22s cubic-bezier(0.34,1.2,0.64,1)",
};
const dialogHeader: React.CSSProperties = {
  display: "flex", justifyContent: "space-between", alignItems: "center",
  padding: "16px 20px",
  borderBottom: "1px solid var(--ha-divider)",
  position: "sticky", top: 0, background: "var(--ha-card-bg)", zIndex: 1,
};
const dialogTitle: React.CSSProperties = {
  fontSize: 16, fontWeight: 400, color: "var(--ha-primary-text)",
};
const dialogSubtitle: React.CSSProperties = {
  fontSize: 12, color: "var(--ha-secondary-text)", marginTop: 2,
};
const closeBtn: React.CSSProperties = {
  background: "none", border: "none",
  color: "var(--ha-secondary-text)",
  width: 32, height: 32,
  display: "flex", alignItems: "center", justifyContent: "center",
  borderRadius: "50%", cursor: "pointer",
};
const section: React.CSSProperties = {
  padding: "14px 20px",
  borderBottom: "1px solid var(--ha-divider)",
};
const sectionHeaderRow: React.CSSProperties = {
  display: "flex", justifyContent: "space-between", alignItems: "center",
};
const sectionLabel: React.CSSProperties = {
  fontSize: 12, fontWeight: 500,
  color: "var(--ha-secondary-text)",
  textTransform: "uppercase", letterSpacing: "0.06em",
};
const chipActionBtn: React.CSSProperties = {
  padding: "3px 10px",
  background: "var(--ha-primary-color-light)",
  color: "var(--ha-primary-color)",
  border: "none",
  borderRadius: "var(--ha-chip-radius)",
  fontSize: 11, fontWeight: 500, cursor: "pointer",
};
const addColorForm: React.CSSProperties = {
  display: "flex", gap: 6, alignItems: "center",
  marginTop: 8, padding: "8px 10px",
  background: "var(--ha-tray-empty-bg)",
  borderRadius: "var(--ha-btn-radius)",
  border: "1px solid var(--ha-divider)",
};
const colorPicker: React.CSSProperties = {
  width: 30, height: 26, border: "none", background: "none",
  borderRadius: 4, cursor: "pointer", padding: 0,
};
const inputStyle: React.CSSProperties = {
  padding: "6px 8px",
  background: "var(--ha-input-bg)",
  border: "1px solid var(--ha-divider)",
  borderRadius: "var(--ha-btn-radius)",
  color: "var(--ha-primary-text)",
  fontSize: 13, outline: "none",
  transition: "var(--ha-transition)",
};
const primaryBtn: React.CSSProperties = {
  padding: "6px 14px",
  background: "var(--ha-primary-color)",
  color: "#fff", border: "none",
  borderRadius: "var(--ha-btn-radius)",
  fontSize: 13, fontWeight: 500, cursor: "pointer", whiteSpace: "nowrap",
};
const colorList: React.CSSProperties = {
  marginTop: 4,
  borderTop: "1px solid var(--ha-divider)",
};
const deleteFilamentBtn: React.CSSProperties = {
  width: "100%",
  padding: "10px 14px",
  borderRadius: "var(--ha-btn-radius)",
  border: "1px solid rgba(244,67,54,0.35)",
  background: "var(--ha-error-bg)",
  color: "var(--ha-error)",
  fontSize: 13,
  fontWeight: 600,
  cursor: "pointer",
};
const deleteFilamentHint: React.CSSProperties = {
  marginTop: 8,
  fontSize: 11,
  color: "var(--ha-disabled-text)",
  textAlign: "center",
};
const deleteBtn: React.CSSProperties = {
  background: "none", border: "none",
  color: "var(--ha-disabled-text)",
  cursor: "pointer", padding: 4,
  borderRadius: "var(--ha-btn-radius)",
  display: "flex", alignItems: "center",
  transition: "color var(--ha-transition)",
};
const selectStyle: React.CSSProperties = {
  padding: "6px 8px",
  background: "var(--ha-input-bg)",
  border: "1px solid var(--ha-divider)",
  borderRadius: "var(--ha-btn-radius)",
  color: "var(--ha-primary-text)",
  fontSize: 13, outline: "none",
};
const formRow: React.CSSProperties = { display: "flex", gap: 6, flexWrap: "wrap" };
const emptyText: React.CSSProperties = {
  fontSize: 12, color: "var(--ha-disabled-text)",
  padding: "8px 0",
};
const eventBadge = (type: string): React.CSSProperties => ({
  fontSize: 12, fontWeight: 600,
  minWidth: 36, textAlign: "center",
  padding: "2px 5px", borderRadius: 4,
  background: type === "purchase" ? "var(--ha-success-bg)" : type === "used" ? "var(--ha-error-bg)" : "var(--ha-warning-bg)",
  color: type === "purchase" ? "var(--ha-success)" : type === "used" ? "var(--ha-error)" : "var(--ha-warning)",
});
const suggestionsList: React.CSSProperties = {
  position: "absolute", top: "100%", left: 0, right: 0,
  background: "var(--ha-card-bg)",
  border: "1px solid var(--ha-divider)",
  borderRadius: "var(--ha-btn-radius)",
  marginTop: 3, zIndex: 10,
  maxHeight: 160, overflowY: "auto",
  boxShadow: "0 8px 24px rgba(0,0,0,0.15)",
};
const suggestionItem: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 8,
  padding: "6px 10px", cursor: "pointer", fontSize: 12,
};
