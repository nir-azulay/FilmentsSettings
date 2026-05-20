import { useState } from "react";
import { useMemo } from "react";
import { Filament } from "../api";
import { buildStaplePools } from "../stockUtils";
import FilamentCard from "./FilamentCard";
import StockManager from "./StockManager";

interface Props {
  filaments: Filament[];
  onUpdate: () => Promise<void>;
}

export default function Dashboard({ filaments, onUpdate }: Props) {
  const [selectedFilament, setSelectedFilament] = useState<Filament | null>(null);
  const [filter, setFilter] = useState<string>("all");

  const types = Array.from(new Set(filaments.map((f) => f.filament_type)));
  const staplePools = useMemo(() => buildStaplePools(filaments), [filaments]);
  const filtered = filter === "all" ? filaments : filaments.filter((f) => f.filament_type === filter);
  const refreshedSelected = selectedFilament
    ? filaments.find((f) => f.id === selectedFilament.id) ?? null
    : null;

  return (
    <>
      {/* ── HA-style filter chips ── */}
      {types.length > 1 && (
        <div style={chipRow}>
          <FilterChip label="All" active={filter === "all"} onClick={() => setFilter("all")} />
          {types.map((t) => (
            <FilterChip key={t} label={t} active={filter === t} onClick={() => setFilter(t)} />
          ))}
        </div>
      )}

      {/* ── Card grid ── */}
      <div style={grid}>
        {filtered.map((f) => (
          <FilamentCard key={f.id} filament={f} staplePools={staplePools} onManageStock={() => setSelectedFilament(f)} onUpdate={onUpdate} />
        ))}
        {filtered.length === 0 && (
          <div style={emptyState}>
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--ha-disabled-text)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="12 2 2 7 12 12 22 7 12 2" />
              <polyline points="2 17 12 22 22 17" />
              <polyline points="2 12 12 17 22 12" />
            </svg>
            <p style={{ marginTop: 12, color: "var(--ha-secondary-text)", fontSize: 14 }}>No filaments found</p>
            <p style={{ color: "var(--ha-disabled-text)", fontSize: 12, marginTop: 4 }}>
              Click "Sync Profiles" to import your Bambu Studio profiles
            </p>
          </div>
        )}
      </div>

      {refreshedSelected && (
        <StockManager filament={refreshedSelected} onClose={() => setSelectedFilament(null)} onUpdate={onUpdate} />
      )}
    </>
  );
}

function FilterChip({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: "5px 14px",
        borderRadius: "var(--ha-chip-radius)",
        fontSize: 12,
        fontWeight: active ? 500 : 400,
        background: active ? "var(--ha-primary-color)" : "var(--ha-surface-lower)",
        color: active ? "#fff" : "var(--ha-secondary-text)",
        border: "none",
        cursor: "pointer",
        transition: "var(--ha-transition)",
        letterSpacing: "0.01em",
      }}
    >
      {label}
    </button>
  );
}

const chipRow: React.CSSProperties = {
  display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 12,
};
const grid: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
  gap: 12,
};
const emptyState: React.CSSProperties = {
  gridColumn: "1/-1",
  display: "flex", flexDirection: "column", alignItems: "center",
  padding: "64px 24px", textAlign: "center",
};
