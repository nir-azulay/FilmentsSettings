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

  return (
    <>
      <div style={gridStyle}>
        {filaments.map((f) => (
          <FilamentCard key={f.id} filament={f} onManageStock={() => setSelectedFilament(f)} onUpdate={onUpdate} />
        ))}
        {filaments.length === 0 && (
          <p style={{ opacity: 0.5, gridColumn: "1 / -1", textAlign: "center", padding: "3rem" }}>
            No filaments yet. Click "Import from Profiles" to get started.
          </p>
        )}
      </div>

      {selectedFilament && (
        <StockManager
          filament={selectedFilament}
          onClose={() => setSelectedFilament(null)}
          onUpdate={onUpdate}
        />
      )}
    </>
  );
}

const gridStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
  gap: "1.2rem",
};
