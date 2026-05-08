import { useState } from "react";
import { Filament } from "../api";
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

  const filtered = filter === "all"
    ? filaments
    : filaments.filter((f) => f.filament_type === filter);

  const refreshedSelected = selectedFilament
    ? filaments.find((f) => f.id === selectedFilament.id) ?? null
    : null;

  return (
    <>
      {/* Filter pills */}
      {types.length > 1 && (
        <div style={filterRow}>
          <FilterPill label="All" value="all" active={filter === "all"} onClick={() => setFilter("all")} />
          {types.map((t) => (
            <FilterPill key={t} label={t} value={t} active={filter === t} onClick={() => setFilter(t)} />
          ))}
        </div>
      )}

      <div style={gridStyle}>
        {filtered.map((f) => (
          <FilamentCard key={f.id} filament={f} onManageStock={() => setSelectedFilament(f)} />
        ))}
        {filtered.length === 0 && (
          <div style={emptyStyle}>
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <p>No filaments found. Click "Import Profiles" to get started.</p>
          </div>
        )}
      </div>

      {refreshedSelected && (
        <StockManager
          filament={refreshedSelected}
          onClose={() => setSelectedFilament(null)}
          onUpdate={onUpdate}
        />
      )}
    </>
  );
}

function FilterPill({ label, active, onClick }: { label: string; value: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: "0.35rem 0.8rem",
        background: active ? "var(--accent-subtle)" : "var(--bg-tertiary)",
        color: active ? "var(--accent-hover)" : "var(--text-secondary)",
        border: active ? "1px solid rgba(99, 102, 241, 0.3)" : "1px solid var(--border-subtle)",
        borderRadius: "20px",
        fontSize: "0.78rem",
        fontWeight: 500,
        cursor: "pointer",
        transition: "var(--transition)",
      }}
    >
      {label}
    </button>
  );
}

const filterRow: React.CSSProperties = {
  display: "flex",
  gap: "0.4rem",
  marginBottom: "1.2rem",
  flexWrap: "wrap",
};

const gridStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
  gap: "1rem",
};

const emptyStyle: React.CSSProperties = {
  gridColumn: "1 / -1",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  gap: "0.8rem",
  padding: "4rem 2rem",
  color: "var(--text-muted)",
  fontSize: "0.9rem",
};
