import { useEffect, useRef, useState } from "react";
import { ColorStock, Filament, StockEntry, addColor, addStockEvent, deleteColor, fetchHistory, updateColor } from "../api";
import { getColorSuggestions, lookupColorHex } from "../colorMap";

interface Props {
  filament: Filament;
  onClose: () => void;
  onUpdate: () => Promise<void>;
}

export default function StockManager({ filament, onClose, onUpdate }: Props) {
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
  const [suggestions, setSuggestions] = useState<Array<{ name: string; hex: string }>>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchHistory(filament.id).then(setHistory);
  }, [filament.id]);

  const handleColorNameChange = (value: string) => {
    setNewColorName(value);
    const hex = lookupColorHex(value);
    if (hex) {
      setNewColorHex(hex);
    }
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
    await addStockEvent(filament.id, {
      quantity: qty,
      event_type: eventType,
      color_stock_id: selectedColorId,
      notes,
    });
    setNotes("");
    setQuantity(1);
    const h = await fetchHistory(filament.id);
    setHistory(h);
    await onUpdate();
  };

  const handleAddColor = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newColorName.trim()) return;
    await addColor(filament.id, { color_name: newColorName, color_hex: newColorHex, quantity: newColorQty });
    setNewColorName("");
    setNewColorHex("#808080");
    setNewColorQty(0);
    setShowAddColor(false);
    await onUpdate();
  };

  const handleDeleteColor = async (colorId: number) => {
    if (!confirm("Delete this color?")) return;
    await deleteColor(colorId);
    await onUpdate();
  };

  const handleEditColorQty = async (color: ColorStock, newQty: number) => {
    await updateColor(color.id, { quantity: newQty });
    await onUpdate();
  };

  return (
    <div style={overlayStyle} onClick={onClose}>
      <div style={modalStyle} onClick={(e) => e.stopPropagation()}>
        {/* Modal header */}
        <div style={modalHeader}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
            {filament.brand_logo_url && (
              <img src={filament.brand_logo_url} alt="" style={{ width: "24px", height: "24px", borderRadius: "4px", objectFit: "contain" }} />
            )}
            <div>
              <h2 style={modalTitle}>{filament.brand} {filament.material}</h2>
              <p style={modalSubtitle}>{filament.filament_type} &middot; {filament.current_stock} spools total</p>
            </div>
          </div>
          <button onClick={onClose} style={closeBtn}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* Colors section */}
        <section style={sectionStyle}>
          <div style={sectionHeader}>
            <h3 style={sectionTitle}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="13.5" cy="6.5" r="0.5" fill="var(--accent)" />
                <circle cx="17.5" cy="10.5" r="0.5" fill="var(--accent)" />
                <circle cx="8.5" cy="7.5" r="0.5" fill="var(--accent)" />
                <circle cx="6.5" cy="12.5" r="0.5" fill="var(--accent)" />
                <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z" />
              </svg>
              Colors in Stock
            </h3>
            <button onClick={() => setShowAddColor(!showAddColor)} style={addColorBtn}>
              {showAddColor ? "Cancel" : "+ Add Color"}
            </button>
          </div>

          {showAddColor && (
            <form onSubmit={handleAddColor} style={addColorForm}>
              <input
                type="color"
                value={newColorHex}
                onChange={(e) => setNewColorHex(e.target.value)}
                style={colorPickerInput}
              />
              <div style={{ position: "relative", flex: 1 }}>
                <input
                  type="text"
                  value={newColorName}
                  onChange={(e) => handleColorNameChange(e.target.value)}
                  onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                  onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
                  placeholder="Type color name..."
                  style={{ ...inputStyle, width: "100%" }}
                  required
                />
                {showSuggestions && (
                  <div ref={suggestionsRef} style={suggestionsDropdown}>
                    {suggestions.map((s) => (
                      <div
                        key={s.name}
                        style={suggestionItem}
                        onMouseDown={() => handleSuggestionClick(s.name, s.hex)}
                      >
                        <div style={{ width: "12px", height: "12px", borderRadius: "3px", background: s.hex, border: "1px solid rgba(255,255,255,0.15)", flexShrink: 0 }} />
                        <span style={{ flex: 1 }}>{s.name}</span>
                        <span style={{ opacity: 0.4, fontSize: "0.72rem", fontFamily: "monospace" }}>{s.hex}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <input
                type="number"
                min={0}
                value={newColorQty}
                onChange={(e) => setNewColorQty(Number(e.target.value))}
                style={{ ...inputStyle, width: "55px", textAlign: "center" }}
                placeholder="Qty"
              />
              <button type="submit" style={submitColorBtn}>Add</button>
            </form>
          )}

          {filament.colors.length === 0 ? (
            <div style={emptyState}>
              <p>No colors yet. Add your first color above.</p>
            </div>
          ) : (
            <div style={colorList}>
              {filament.colors.map((c) => (
                <div key={c.id} style={colorRow}>
                  <div style={{ ...colorDot, background: c.color_hex }} />
                  <span style={{ flex: 1, fontSize: "0.85rem", fontWeight: 500 }}>{c.color_name}</span>
                  <input
                    type="number"
                    min={0}
                    value={c.quantity}
                    onChange={(e) => handleEditColorQty(c, Number(e.target.value))}
                    style={qtyInput}
                  />
                  <button onClick={() => handleDeleteColor(c.id)} style={deleteColorBtn} title="Remove color">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="3 6 5 6 21 6" />
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Log stock section */}
        <section style={sectionStyle}>
          <h3 style={sectionTitle}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--success)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 20V10M6 20V14M18 20V4" />
            </svg>
            Log Stock Change
          </h3>
          <form onSubmit={handleStockSubmit} style={stockForm}>
            <div style={formRow}>
              <select
                value={eventType}
                onChange={(e) => setEventType(e.target.value as "purchase" | "used" | "adjustment")}
                style={selectStyle}
              >
                <option value="purchase">+ Purchase</option>
                <option value="used">- Used</option>
                <option value="adjustment">~ Adjustment</option>
              </select>
              {filament.colors.length > 0 && (
                <select
                  value={selectedColorId ?? ""}
                  onChange={(e) => setSelectedColorId(e.target.value ? Number(e.target.value) : null)}
                  style={selectStyle}
                >
                  <option value="">All colors</option>
                  {filament.colors.map((c) => (
                    <option key={c.id} value={c.id}>{c.color_name}</option>
                  ))}
                </select>
              )}
              <input
                type="number"
                min={1}
                value={quantity}
                onChange={(e) => setQuantity(Number(e.target.value))}
                style={{ ...inputStyle, width: "60px", textAlign: "center" }}
              />
            </div>
            <div style={formRow}>
              <input
                type="text"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Notes (optional)"
                style={{ ...inputStyle, flex: 1 }}
              />
              <button type="submit" style={logBtn}>Log</button>
            </div>
          </form>
        </section>

        {/* History */}
        <section style={sectionStyle}>
          <h3 style={sectionTitle}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
            History
          </h3>
          <div style={historyList}>
            {history.length === 0 && <p style={emptyState}>No history yet.</p>}
            {history.map((entry) => {
              const color = filament.colors.find((c) => c.id === entry.color_stock_id);
              return (
                <div key={entry.id} style={historyRow}>
                  <span style={eventBadge(entry.event_type)}>
                    {entry.event_type === "purchase" ? "+" : entry.event_type === "used" ? "" : "~"}
                    {entry.quantity}
                  </span>
                  {color && <div style={{ width: "10px", height: "10px", borderRadius: "50%", background: color.color_hex, border: "1px solid rgba(255,255,255,0.15)" }} />}
                  <span style={{ flex: 1, fontSize: "0.82rem", color: "var(--text-secondary)" }}>
                    {entry.notes || entry.event_type}
                  </span>
                  <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
                    {new Date(entry.created_at).toLocaleDateString()}
                  </span>
                </div>
              );
            })}
          </div>
        </section>
      </div>
    </div>
  );
}

const overlayStyle: React.CSSProperties = {
  position: "fixed",
  inset: 0,
  background: "rgba(0, 0, 0, 0.75)",
  backdropFilter: "blur(4px)",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  zIndex: 1000,
  animation: "fadeIn 0.15s ease-out",
};

const modalStyle: React.CSSProperties = {
  background: "var(--bg-secondary)",
  borderRadius: "var(--radius-xl)",
  width: "90%",
  maxWidth: "580px",
  maxHeight: "88vh",
  overflow: "auto",
  border: "1px solid var(--border)",
  boxShadow: "var(--shadow-lg)",
  animation: "slideUp 0.2s ease-out",
};

const modalHeader: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  padding: "1.2rem 1.5rem",
  borderBottom: "1px solid var(--border-subtle)",
  position: "sticky",
  top: 0,
  background: "var(--bg-secondary)",
  zIndex: 1,
};

const modalTitle: React.CSSProperties = {
  fontSize: "1.1rem",
  fontWeight: 600,
};

const modalSubtitle: React.CSSProperties = {
  fontSize: "0.78rem",
  color: "var(--text-muted)",
  marginTop: "1px",
};

const closeBtn: React.CSSProperties = {
  background: "var(--bg-tertiary)",
  border: "1px solid var(--border-subtle)",
  color: "var(--text-secondary)",
  width: "32px",
  height: "32px",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  borderRadius: "var(--radius-sm)",
  cursor: "pointer",
  transition: "var(--transition)",
};

const sectionStyle: React.CSSProperties = {
  padding: "1rem 1.5rem",
  borderBottom: "1px solid var(--border-subtle)",
};

const sectionHeader: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: "0.7rem",
};

const sectionTitle: React.CSSProperties = {
  fontSize: "0.85rem",
  fontWeight: 600,
  display: "flex",
  alignItems: "center",
  gap: "0.4rem",
};

const addColorBtn: React.CSSProperties = {
  padding: "0.3rem 0.7rem",
  background: "var(--accent-subtle)",
  color: "var(--accent-hover)",
  border: "1px solid rgba(99, 102, 241, 0.2)",
  borderRadius: "var(--radius-sm)",
  fontSize: "0.75rem",
  fontWeight: 500,
  cursor: "pointer",
};

const addColorForm: React.CSSProperties = {
  display: "flex",
  gap: "0.4rem",
  alignItems: "center",
  marginBottom: "0.7rem",
  padding: "0.6rem",
  background: "var(--bg-tertiary)",
  borderRadius: "var(--radius-md)",
  border: "1px solid var(--border-subtle)",
};

const colorPickerInput: React.CSSProperties = {
  width: "34px",
  height: "30px",
  border: "none",
  cursor: "pointer",
  borderRadius: "var(--radius-sm)",
  padding: 0,
  background: "none",
};

const inputStyle: React.CSSProperties = {
  padding: "0.45rem 0.65rem",
  background: "var(--bg-elevated)",
  border: "1px solid var(--border)",
  borderRadius: "var(--radius-sm)",
  color: "var(--text-primary)",
  fontSize: "0.82rem",
  outline: "none",
  transition: "var(--transition)",
};

const submitColorBtn: React.CSSProperties = {
  padding: "0.45rem 0.8rem",
  background: "var(--accent)",
  color: "#fff",
  border: "none",
  borderRadius: "var(--radius-sm)",
  fontSize: "0.8rem",
  fontWeight: 500,
  cursor: "pointer",
};

const colorList: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "0.25rem",
};

const colorRow: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: "0.6rem",
  padding: "0.4rem 0.6rem",
  borderRadius: "var(--radius-sm)",
  background: "var(--bg-tertiary)",
};

const colorDot: React.CSSProperties = {
  width: "14px",
  height: "14px",
  borderRadius: "50%",
  border: "2px solid rgba(255,255,255,0.15)",
  flexShrink: 0,
};

const qtyInput: React.CSSProperties = {
  ...inputStyle,
  width: "50px",
  textAlign: "center",
  fontWeight: 600,
};

const deleteColorBtn: React.CSSProperties = {
  background: "none",
  border: "none",
  color: "var(--text-muted)",
  cursor: "pointer",
  padding: "0.3rem",
  borderRadius: "var(--radius-sm)",
  display: "flex",
  alignItems: "center",
  transition: "var(--transition)",
};

const selectStyle: React.CSSProperties = {
  padding: "0.45rem 0.65rem",
  background: "var(--bg-elevated)",
  border: "1px solid var(--border)",
  borderRadius: "var(--radius-sm)",
  color: "var(--text-primary)",
  fontSize: "0.82rem",
  outline: "none",
};

const stockForm: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "0.5rem",
};

const formRow: React.CSSProperties = {
  display: "flex",
  gap: "0.4rem",
  flexWrap: "wrap",
};

const logBtn: React.CSSProperties = {
  padding: "0.45rem 1.2rem",
  background: "var(--accent)",
  color: "#fff",
  border: "none",
  borderRadius: "var(--radius-sm)",
  fontSize: "0.82rem",
  fontWeight: 500,
  cursor: "pointer",
  transition: "var(--transition)",
};

const historyList: React.CSSProperties = {
  maxHeight: "180px",
  overflow: "auto",
  display: "flex",
  flexDirection: "column",
  gap: "2px",
};

const historyRow: React.CSSProperties = {
  display: "flex",
  gap: "0.5rem",
  alignItems: "center",
  padding: "0.4rem 0.5rem",
  borderRadius: "var(--radius-sm)",
};

const eventBadge = (type: string): React.CSSProperties => ({
  fontSize: "0.78rem",
  fontWeight: 600,
  minWidth: "38px",
  textAlign: "center",
  padding: "0.15rem 0.3rem",
  borderRadius: "4px",
  background: type === "purchase" ? "var(--success-subtle)" : type === "used" ? "var(--danger-subtle)" : "var(--warning-subtle)",
  color: type === "purchase" ? "var(--success)" : type === "used" ? "var(--danger)" : "var(--warning)",
});

const emptyState: React.CSSProperties = {
  padding: "0.8rem",
  textAlign: "center",
  fontSize: "0.82rem",
  color: "var(--text-muted)",
  background: "var(--bg-tertiary)",
  borderRadius: "var(--radius-sm)",
};

const suggestionsDropdown: React.CSSProperties = {
  position: "absolute",
  top: "100%",
  left: 0,
  right: 0,
  background: "var(--bg-elevated)",
  border: "1px solid var(--border)",
  borderRadius: "var(--radius-sm)",
  marginTop: "4px",
  zIndex: 10,
  maxHeight: "160px",
  overflow: "auto",
  boxShadow: "var(--shadow-md)",
};

const suggestionItem: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: "0.5rem",
  padding: "0.4rem 0.6rem",
  cursor: "pointer",
  fontSize: "0.8rem",
  transition: "background 0.1s",
};
