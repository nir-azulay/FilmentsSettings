import { useState } from "react";
import { Filament, updateFilament } from "../api";

interface Props {
  filament: Filament;
  onManageStock: () => void;
  onUpdate: () => Promise<void>;
}

export default function FilamentCard({ filament, onManageStock, onUpdate }: Props) {
  const [editingColor, setEditingColor] = useState(false);
  const [colorHex, setColorHex] = useState(filament.color_hex);
  const [colorName, setColorName] = useState(filament.color_name);

  const isLowStock = filament.current_stock <= filament.low_stock_threshold;

  const handleColorSave = async () => {
    await updateFilament(filament.id, { color_hex: colorHex, color_name: colorName });
    setEditingColor(false);
    await onUpdate();
  };

  return (
    <div style={{ ...cardStyle, borderColor: isLowStock ? "#dc2626" : "#27272a" }}>
      <div style={{ display: "flex", gap: "0.8rem", alignItems: "flex-start" }}>
        <div
          style={{ ...swatchStyle, background: filament.color_hex }}
          onClick={() => setEditingColor(true)}
          title="Click to change color"
        />
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            {filament.brand_logo_url && (
              <img
                src={filament.brand_logo_url}
                alt={filament.brand}
                style={logoStyle}
                onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
              />
            )}
            <h3 style={{ fontSize: "1rem", fontWeight: 600 }}>{filament.brand}</h3>
          </div>
          <p style={{ fontSize: "0.85rem", opacity: 0.7 }}>{filament.material}</p>
          {filament.color_name && (
            <p style={{ fontSize: "0.75rem", opacity: 0.5 }}>{filament.color_name}</p>
          )}
        </div>
        <div style={stockBadgeStyle(isLowStock)}>
          {filament.current_stock}
        </div>
      </div>

      <div style={detailsStyle}>
        <Detail label="Type" value={filament.filament_type} />
        <Detail label="Density" value={filament.density ? `${filament.density} g/cm³` : "—"} />
        <Detail
          label="Nozzle"
          value={
            filament.nozzle_temp_min && filament.nozzle_temp_max
              ? `${filament.nozzle_temp_min}–${filament.nozzle_temp_max}°C`
              : "—"
          }
        />
        <Detail label="Bed" value={filament.bed_temp ? `${filament.bed_temp}°C` : "—"} />
      </div>

      <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.8rem" }}>
        <button onClick={onManageStock} style={btnStyle}>
          Manage Stock
        </button>
        {filament.amazon_url && (
          <a href={filament.amazon_url} target="_blank" rel="noopener" style={linkBtnStyle}>
            Amazon
          </a>
        )}
      </div>

      {editingColor && (
        <div style={colorEditStyle}>
          <input
            type="color"
            value={colorHex}
            onChange={(e) => setColorHex(e.target.value)}
            style={{ width: "40px", height: "32px", border: "none", cursor: "pointer" }}
          />
          <input
            type="text"
            value={colorName}
            onChange={(e) => setColorName(e.target.value)}
            placeholder="Color name"
            style={inputStyle}
          />
          <button onClick={handleColorSave} style={{ ...btnStyle, background: "#22c55e" }}>
            Save
          </button>
          <button onClick={() => setEditingColor(false)} style={btnStyle}>
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span style={{ fontSize: "0.7rem", opacity: 0.5, textTransform: "uppercase" }}>{label}</span>
      <p style={{ fontSize: "0.82rem" }}>{value}</p>
    </div>
  );
}

const cardStyle: React.CSSProperties = {
  background: "#18181b",
  borderRadius: "12px",
  padding: "1.2rem",
  border: "1px solid #27272a",
  transition: "border-color 0.2s",
};

const logoStyle: React.CSSProperties = {
  width: "22px",
  height: "22px",
  objectFit: "contain",
  borderRadius: "4px",
};

const swatchStyle: React.CSSProperties = {
  width: "42px",
  height: "42px",
  borderRadius: "8px",
  flexShrink: 0,
  cursor: "pointer",
  border: "2px solid rgba(255,255,255,0.1)",
};

const stockBadgeStyle = (low: boolean): React.CSSProperties => ({
  background: low ? "#dc262620" : "#22c55e20",
  color: low ? "#f87171" : "#4ade80",
  padding: "0.2rem 0.6rem",
  borderRadius: "6px",
  fontWeight: 700,
  fontSize: "1.1rem",
});

const detailsStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "1fr 1fr",
  gap: "0.5rem",
  marginTop: "0.8rem",
  padding: "0.6rem 0",
  borderTop: "1px solid #27272a",
};

const btnStyle: React.CSSProperties = {
  padding: "0.4rem 0.8rem",
  background: "#3f3f46",
  color: "#e4e4e7",
  border: "none",
  borderRadius: "6px",
  fontSize: "0.8rem",
  cursor: "pointer",
};

const linkBtnStyle: React.CSSProperties = {
  ...btnStyle,
  textDecoration: "none",
  background: "#f59e0b20",
  color: "#fbbf24",
};

const inputStyle: React.CSSProperties = {
  padding: "0.3rem 0.5rem",
  background: "#27272a",
  border: "1px solid #3f3f46",
  borderRadius: "4px",
  color: "#e4e4e7",
  fontSize: "0.8rem",
  flex: 1,
};

const colorEditStyle: React.CSSProperties = {
  display: "flex",
  gap: "0.5rem",
  alignItems: "center",
  marginTop: "0.8rem",
  padding: "0.6rem",
  background: "#27272a",
  borderRadius: "8px",
};
