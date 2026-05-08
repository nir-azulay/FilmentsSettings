import { useState } from "react";
import { Filament } from "../api";

interface Props {
  filament: Filament;
  onManageStock: () => void;
}

export default function FilamentCard({ filament, onManageStock }: Props) {
  const [hovered, setHovered] = useState(false);
  const isLowStock = filament.current_stock <= filament.low_stock_threshold;

  const materialColor = getMaterialAccent(filament.filament_type);

  return (
    <div
      style={{
        ...cardStyle,
        borderColor: hovered ? "var(--border)" : "var(--border-subtle)",
        transform: hovered ? "translateY(-2px)" : "none",
        boxShadow: hovered ? "var(--shadow-md)" : "var(--shadow-sm)",
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Top accent strip */}
      <div style={{ ...accentStrip, background: materialColor }} />

      {/* Header row */}
      <div style={headerRow}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", flex: 1 }}>
          {filament.brand_logo_url && (
            <img
              src={filament.brand_logo_url}
              alt={filament.brand}
              style={logoStyle}
              onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
            />
          )}
          <div>
            <h3 style={brandName}>{filament.brand}</h3>
            <p style={materialName}>{filament.material}</p>
          </div>
        </div>
        <div style={stockBadge(isLowStock)}>
          <span style={{ fontSize: "0.65rem", textTransform: "uppercase", opacity: 0.8 }}>
            {isLowStock ? "Low" : "Stock"}
          </span>
          <span style={{ fontSize: "1.3rem", fontWeight: 700, lineHeight: 1 }}>
            {filament.current_stock}
          </span>
        </div>
      </div>

      {/* Color chips */}
      {filament.colors.length > 0 && (
        <div style={colorChipsWrap}>
          {filament.colors.map((c) => (
            <div key={c.id} style={colorChip}>
              <div style={{ ...colorChipDot, background: c.color_hex }} />
              <span style={{ fontSize: "0.78rem" }}>{c.color_name}</span>
              <span style={colorChipQty(c.quantity)}>{c.quantity}</span>
            </div>
          ))}
        </div>
      )}

      {filament.colors.length === 0 && (
        <div style={noColorsHint}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          No colors added
        </div>
      )}

      {/* Specs row */}
      <div style={specsRow}>
        <SpecPill label="Type" value={filament.filament_type} />
        {filament.density && <SpecPill label="Density" value={`${filament.density}`} />}
        {filament.nozzle_temp_min && filament.nozzle_temp_max && (
          <SpecPill label="Nozzle" value={`${filament.nozzle_temp_min}-${filament.nozzle_temp_max}°`} />
        )}
        {filament.bed_temp && <SpecPill label="Bed" value={`${filament.bed_temp}°`} />}
      </div>

      {/* Actions */}
      <div style={actionsRow}>
        <button onClick={onManageStock} style={primaryBtn}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 20V10M6 20V14M18 20V4" />
          </svg>
          Manage Stock
        </button>
        {filament.amazon_url && (
          <a href={filament.amazon_url} target="_blank" rel="noopener" style={amazonBtn}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
              <polyline points="15 3 21 3 21 9" />
              <line x1="10" y1="14" x2="21" y2="3" />
            </svg>
            Amazon
          </a>
        )}
      </div>
    </div>
  );
}

function SpecPill({ label, value }: { label: string; value: string }) {
  return (
    <div style={specPillStyle}>
      <span style={{ fontSize: "0.65rem", color: "var(--text-muted)", textTransform: "uppercase" }}>{label}</span>
      <span style={{ fontSize: "0.78rem", fontWeight: 500 }}>{value}</span>
    </div>
  );
}

function getMaterialAccent(type: string): string {
  const map: Record<string, string> = {
    PLA: "#22c55e",
    PETG: "#3b82f6",
    ASA: "#f59e0b",
    ABS: "#ef4444",
    PA: "#8b5cf6",
    TPU: "#ec4899",
  };
  return map[type] || "var(--accent)";
}

const cardStyle: React.CSSProperties = {
  position: "relative",
  background: "var(--bg-secondary)",
  borderRadius: "var(--radius-lg)",
  padding: "1.2rem",
  paddingTop: "1.4rem",
  border: "1px solid var(--border-subtle)",
  transition: "var(--transition)",
  overflow: "hidden",
  display: "flex",
  flexDirection: "column",
  gap: "0.8rem",
};

const accentStrip: React.CSSProperties = {
  position: "absolute",
  top: 0,
  left: 0,
  right: 0,
  height: "3px",
  borderRadius: "var(--radius-lg) var(--radius-lg) 0 0",
};

const headerRow: React.CSSProperties = {
  display: "flex",
  alignItems: "flex-start",
  gap: "0.6rem",
};

const logoStyle: React.CSSProperties = {
  width: "28px",
  height: "28px",
  objectFit: "contain",
  borderRadius: "var(--radius-sm)",
  background: "var(--bg-tertiary)",
  padding: "3px",
};

const brandName: React.CSSProperties = {
  fontSize: "0.95rem",
  fontWeight: 600,
  lineHeight: 1.2,
};

const materialName: React.CSSProperties = {
  fontSize: "0.8rem",
  color: "var(--text-secondary)",
  marginTop: "1px",
};

const stockBadge = (low: boolean): React.CSSProperties => ({
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  padding: "0.4rem 0.6rem",
  borderRadius: "var(--radius-md)",
  background: low ? "var(--danger-subtle)" : "var(--success-subtle)",
  color: low ? "var(--danger)" : "var(--success)",
  minWidth: "48px",
});

const colorChipsWrap: React.CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: "0.35rem",
};

const colorChip: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: "0.35rem",
  padding: "0.25rem 0.5rem",
  background: "var(--bg-tertiary)",
  borderRadius: "var(--radius-sm)",
  border: "1px solid var(--border-subtle)",
};

const colorChipDot: React.CSSProperties = {
  width: "10px",
  height: "10px",
  borderRadius: "50%",
  border: "1px solid rgba(255,255,255,0.15)",
  flexShrink: 0,
};

const colorChipQty = (qty: number): React.CSSProperties => ({
  fontSize: "0.72rem",
  fontWeight: 600,
  color: qty <= 0 ? "var(--danger)" : "var(--success)",
  marginLeft: "0.15rem",
});

const noColorsHint: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: "0.4rem",
  padding: "0.5rem 0.7rem",
  background: "var(--bg-tertiary)",
  borderRadius: "var(--radius-sm)",
  fontSize: "0.78rem",
  color: "var(--text-muted)",
};

const specsRow: React.CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: "0.35rem",
};

const specPillStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  padding: "0.3rem 0.5rem",
  background: "var(--bg-primary)",
  borderRadius: "var(--radius-sm)",
  border: "1px solid var(--border-subtle)",
};

const actionsRow: React.CSSProperties = {
  display: "flex",
  gap: "0.5rem",
  marginTop: "auto",
  paddingTop: "0.4rem",
};

const primaryBtn: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: "0.4rem",
  padding: "0.45rem 0.8rem",
  background: "var(--accent-subtle)",
  color: "var(--accent-hover)",
  border: "1px solid rgba(99, 102, 241, 0.2)",
  borderRadius: "var(--radius-sm)",
  fontSize: "0.8rem",
  fontWeight: 500,
  cursor: "pointer",
  transition: "var(--transition)",
};

const amazonBtn: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: "0.35rem",
  padding: "0.45rem 0.8rem",
  background: "var(--warning-subtle)",
  color: "var(--warning)",
  border: "1px solid rgba(245, 158, 11, 0.2)",
  borderRadius: "var(--radius-sm)",
  fontSize: "0.8rem",
  fontWeight: 500,
  textDecoration: "none",
  cursor: "pointer",
  transition: "var(--transition)",
};
