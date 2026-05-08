import { useEffect, useState } from "react";
import { Filament, StockEntry, addStockEvent, fetchHistory } from "../api";

interface Props {
  filament: Filament;
  onClose: () => void;
  onUpdate: () => Promise<void>;
}

export default function StockManager({ filament, onClose, onUpdate }: Props) {
  const [history, setHistory] = useState<StockEntry[]>([]);
  const [quantity, setQuantity] = useState(1);
  const [eventType, setEventType] = useState<"purchase" | "used" | "adjustment">("purchase");
  const [notes, setNotes] = useState("");

  useEffect(() => {
    fetchHistory(filament.id).then(setHistory);
  }, [filament.id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const qty = eventType === "used" ? -Math.abs(quantity) : quantity;
    await addStockEvent(filament.id, { quantity: qty, event_type: eventType, notes });
    setNotes("");
    setQuantity(1);
    const h = await fetchHistory(filament.id);
    setHistory(h);
    await onUpdate();
  };

  return (
    <div style={overlayStyle} onClick={onClose}>
      <div style={modalStyle} onClick={(e) => e.stopPropagation()}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <h2 style={{ fontSize: "1.2rem", fontWeight: 600 }}>
            {filament.brand} {filament.material}
          </h2>
          <button onClick={onClose} style={closeBtnStyle}>&times;</button>
        </div>

        <p style={{ marginBottom: "1rem", opacity: 0.7 }}>
          Current stock: <strong style={{ color: "#4ade80" }}>{filament.current_stock} spools</strong>
        </p>

        <form onSubmit={handleSubmit} style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
          <select
            value={eventType}
            onChange={(e) => setEventType(e.target.value as "purchase" | "used" | "adjustment")}
            style={selectStyle}
          >
            <option value="purchase">Purchase (+)</option>
            <option value="used">Used (-)</option>
            <option value="adjustment">Adjustment</option>
          </select>
          <input
            type="number"
            min={1}
            value={quantity}
            onChange={(e) => setQuantity(Number(e.target.value))}
            style={{ ...inputStyle, width: "70px" }}
          />
          <input
            type="text"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Notes (optional)"
            style={{ ...inputStyle, flex: 1 }}
          />
          <button type="submit" style={submitBtnStyle}>
            Add
          </button>
        </form>

        <h3 style={{ fontSize: "0.9rem", fontWeight: 600, marginBottom: "0.5rem" }}>History</h3>
        <div style={{ maxHeight: "250px", overflow: "auto" }}>
          {history.length === 0 && <p style={{ opacity: 0.5, fontSize: "0.85rem" }}>No history yet.</p>}
          {history.map((entry) => (
            <div key={entry.id} style={entryStyle}>
              <span style={{ ...eventBadge(entry.event_type) }}>
                {entry.event_type === "purchase" ? "+" : entry.event_type === "used" ? "" : "~"}
                {entry.quantity}
              </span>
              <span style={{ flex: 1, fontSize: "0.82rem" }}>{entry.notes || entry.event_type}</span>
              <span style={{ fontSize: "0.75rem", opacity: 0.5 }}>
                {new Date(entry.created_at).toLocaleDateString()}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

const overlayStyle: React.CSSProperties = {
  position: "fixed",
  inset: 0,
  background: "rgba(0,0,0,0.7)",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  zIndex: 1000,
};

const modalStyle: React.CSSProperties = {
  background: "#18181b",
  borderRadius: "16px",
  padding: "1.5rem",
  width: "90%",
  maxWidth: "520px",
  border: "1px solid #27272a",
};

const closeBtnStyle: React.CSSProperties = {
  background: "none",
  border: "none",
  color: "#e4e4e7",
  fontSize: "1.5rem",
  cursor: "pointer",
};

const selectStyle: React.CSSProperties = {
  padding: "0.4rem 0.6rem",
  background: "#27272a",
  border: "1px solid #3f3f46",
  borderRadius: "6px",
  color: "#e4e4e7",
  fontSize: "0.85rem",
};

const inputStyle: React.CSSProperties = {
  padding: "0.4rem 0.6rem",
  background: "#27272a",
  border: "1px solid #3f3f46",
  borderRadius: "6px",
  color: "#e4e4e7",
  fontSize: "0.85rem",
};

const submitBtnStyle: React.CSSProperties = {
  padding: "0.4rem 1rem",
  background: "#3b82f6",
  color: "#fff",
  border: "none",
  borderRadius: "6px",
  fontSize: "0.85rem",
  fontWeight: 500,
  cursor: "pointer",
};

const entryStyle: React.CSSProperties = {
  display: "flex",
  gap: "0.6rem",
  alignItems: "center",
  padding: "0.4rem 0",
  borderBottom: "1px solid #27272a",
};

const eventBadge = (type: string): React.CSSProperties => ({
  fontSize: "0.8rem",
  fontWeight: 600,
  minWidth: "36px",
  textAlign: "center",
  color: type === "purchase" ? "#4ade80" : type === "used" ? "#f87171" : "#fbbf24",
});
