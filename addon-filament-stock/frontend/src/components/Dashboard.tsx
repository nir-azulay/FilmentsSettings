import { useEffect, useMemo, useState, type Dispatch, type SetStateAction } from "react";
import { Filament, StapleAlertIgnore, deleteFilament } from "../api";
import { ColorFamilyId, familyFor } from "../colorFamilies";
import { MOBILE_QUERY, useMediaQuery } from "../useMediaQuery";
import { buildIgnoredStapleKeys, buildStaplePools } from "../stockUtils";
import BrandLogo from "./BrandLogo";
import ColorFilter from "./ColorFilter";
import DeleteFilamentModal from "./DeleteFilamentModal";
import FilamentCard from "./FilamentCard";
import MobileFilamentPager from "./MobileFilamentPager";
import StockManager from "./StockManager";

interface Props {
  filaments: Filament[];
  alertIgnores: StapleAlertIgnore[];
  onUpdate: () => Promise<void>;
}

export default function Dashboard({ filaments, alertIgnores, onUpdate }: Props) {
  const [selectedFilament, setSelectedFilament] = useState<Filament | null>(null);
  const [selectedTypes, setSelectedTypes] = useState<Set<string>>(() => new Set());
  const [selectedBrands, setSelectedBrands] = useState<Set<string>>(() => new Set());
  const [selectedColorFamilies, setSelectedColorFamilies] = useState<Set<ColorFamilyId>>(() => new Set());
  const [filamentToDelete, setFilamentToDelete] = useState<Filament | null>(null);
  const [deletingFilament, setDeletingFilament] = useState(false);
  const isMobile = useMediaQuery(MOBILE_QUERY);

  function toggleInSet<T>(setter: Dispatch<SetStateAction<Set<T>>>, value: T) {
    setter((prev) => {
      const next = new Set(prev);
      if (next.has(value)) next.delete(value);
      else next.add(value);
      return next;
    });
  }

  const types = useMemo(
    () => Array.from(new Set(filaments.map((f) => f.filament_type))).sort(),
    [filaments],
  );
  const brands = useMemo(() => {
    const map = new Map<string, string>();
    for (const f of filaments) {
      if (!map.has(f.brand)) map.set(f.brand, f.brand_logo_url || "");
    }
    return Array.from(map.entries())
      .map(([brand, logoUrl]) => ({ brand, logoUrl }))
      .sort((a, b) => a.brand.localeCompare(b.brand));
  }, [filaments]);

  const staplePools = useMemo(() => buildStaplePools(filaments), [filaments]);
  const ignoredStaples = useMemo(() => buildIgnoredStapleKeys(alertIgnores), [alertIgnores]);

  // Bucket every colour swatch in stock into its family so the
  // ColorFilter can hide empty buckets and the row filter can do its
  // ANY-match check cheaply. Built once per filament-list change rather
  // than per render.
  const colorFamiliesInStock = useMemo(() => {
    const set = new Set<ColorFamilyId>();
    for (const f of filaments) {
      for (const c of f.colors ?? []) {
        set.add(familyFor(c.color_hex));
      }
    }
    return set;
  }, [filaments]);

  const filtered = useMemo(() => {
    return filaments.filter((f) => {
      if (selectedTypes.size > 0 && !selectedTypes.has(f.filament_type)) return false;
      if (selectedBrands.size > 0 && !selectedBrands.has(f.brand)) return false;
      // Colour filter: a filament passes if ANY of its colour swatches
      // bucket into one of the selected families. This matches the
      // user mental model of "show me all PETG that comes in blue" --
      // we don't want to hide a multi-color spool just because one of
      // its swatches happens not to be blue.
      if (selectedColorFamilies.size > 0) {
        const colors = f.colors ?? [];
        if (colors.length === 0) return false;
        const anyMatch = colors.some((c) =>
          selectedColorFamilies.has(familyFor(c.color_hex)),
        );
        if (!anyMatch) return false;
      }
      return true;
    });
  }, [filaments, selectedTypes, selectedBrands, selectedColorFamilies]);

  const filterKey =
    `${[...selectedTypes].sort().join(",")}` +
    `|${[...selectedBrands].sort().join(",")}` +
    `|${[...selectedColorFamilies].sort().join(",")}`;

  useEffect(() => {
    if (!isMobile) return;
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [filterKey, isMobile]);

  const refreshedSelected = selectedFilament
    ? filaments.find((f) => f.id === selectedFilament.id) ?? null
    : null;

  const requestDeleteFilament = (f: Filament) => setFilamentToDelete(f);

  const executeDeleteFilament = async () => {
    if (!filamentToDelete || deletingFilament) return;
    setDeletingFilament(true);
    try {
      await deleteFilament(filamentToDelete.id);
      if (selectedFilament?.id === filamentToDelete.id) setSelectedFilament(null);
      setFilamentToDelete(null);
      await onUpdate();
    } finally {
      setDeletingFilament(false);
    }
  };

  const showTypeFilters = types.length > 0;
  const showBrandFilters = brands.length > 1;
  // Only show the colour row if there's at least 2 distinct families in
  // stock. With only one family every chip would either be empty or
  // match everything, so the filter would be pure visual noise.
  const showColorFilters = colorFamiliesInStock.size > 1;

  return (
    <>
      {(showTypeFilters || showBrandFilters || showColorFilters) && (
        <div style={filtersWrap}>
          {showTypeFilters && (
            <div style={filterGroup}>
              <span style={filterGroupLabel}>Material · multi-select</span>
              <div style={chipRow}>
                <FilterChip
                  label="All"
                  active={selectedTypes.size === 0}
                  onClick={() => setSelectedTypes(new Set())}
                />
                {types.map((t) => (
                  <FilterChip
                    key={t}
                    label={t}
                    active={selectedTypes.has(t)}
                    onClick={() => toggleInSet(setSelectedTypes, t)}
                  />
                ))}
              </div>
            </div>
          )}
          {showBrandFilters && (
            <div style={filterGroup}>
              <span style={filterGroupLabel}>Brand · multi-select</span>
              <div style={chipRow}>
                <FilterChip
                  label="All brands"
                  active={selectedBrands.size === 0}
                  onClick={() => setSelectedBrands(new Set())}
                />
                {brands.map((b) => (
                  <BrandFilterChip
                    key={b.brand}
                    brand={b.brand}
                    logoUrl={b.logoUrl}
                    active={selectedBrands.has(b.brand)}
                    onClick={() => toggleInSet(setSelectedBrands, b.brand)}
                  />
                ))}
              </div>
            </div>
          )}
          {showColorFilters && (
            <ColorFilter
              available={colorFamiliesInStock}
              selected={selectedColorFamilies}
              onToggle={(id) => toggleInSet(setSelectedColorFamilies, id)}
              onClear={() => setSelectedColorFamilies(new Set())}
            />
          )}
        </div>
      )}

      {isMobile ? (
        <MobileFilamentPager
          filaments={filtered}
          staplePools={staplePools}
          ignoredStaples={ignoredStaples}
          onManageStock={setSelectedFilament}
          onUpdate={onUpdate}
          onRequestDeleteFilament={requestDeleteFilament}
        />
      ) : (
        <div className="filament-desktop-grid">
          {filtered.map((f) => (
            <FilamentCard
              key={f.id}
              filament={f}
              staplePools={staplePools}
              ignoredStaples={ignoredStaples}
              onManageStock={() => setSelectedFilament(f)}
              onUpdate={onUpdate}
              onRequestDeleteFilament={() => requestDeleteFilament(f)}
            />
          ))}
          {filtered.length === 0 && (
            <div style={emptyState}>
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--ha-disabled-text)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="12 2 2 7 12 12 22 7 12 2" />
                <polyline points="2 17 12 22 22 17" />
                <polyline points="2 12 12 17 22 12" />
              </svg>
              <p style={{ marginTop: 12, color: "var(--ha-secondary-text)", fontSize: 14 }}>No filaments match these filters</p>
              <p style={{ color: "var(--ha-disabled-text)", fontSize: 12, marginTop: 4 }}>
                Tap &quot;All&quot; or pick more materials/brands, or use Sync Profiles to import
              </p>
            </div>
          )}
        </div>
      )}

      {refreshedSelected && (
        <StockManager
          filament={refreshedSelected}
          onClose={() => setSelectedFilament(null)}
          onUpdate={onUpdate}
          onRequestDeleteFilament={() => requestDeleteFilament(refreshedSelected)}
        />
      )}

      {filamentToDelete && (
        <DeleteFilamentModal
          filament={filamentToDelete}
          confirming={deletingFilament}
          onCancel={() => !deletingFilament && setFilamentToDelete(null)}
          onConfirm={executeDeleteFilament}
        />
      )}
    </>
  );
}

function FilterChip({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button type="button" onClick={onClick} style={chipStyle(active)}>
      {label}
    </button>
  );
}

function BrandFilterChip({
  brand,
  logoUrl,
  active,
  onClick,
}: {
  brand: string;
  logoUrl: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button type="button" onClick={onClick} style={{ ...chipStyle(active), display: "inline-flex", alignItems: "center", gap: 6 }}>
      <BrandLogo brand={brand} url={logoUrl} size={18} />
      {brand}
    </button>
  );
}

function chipStyle(active: boolean): React.CSSProperties {
  return {
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
  };
}

const filtersWrap: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 10,
  marginBottom: 12,
};
const filterGroup: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 6,
};
const filterGroupLabel: React.CSSProperties = {
  fontSize: 10,
  fontWeight: 600,
  color: "var(--ha-disabled-text)",
  textTransform: "uppercase",
  letterSpacing: "0.08em",
};
const chipRow: React.CSSProperties = {
  display: "flex",
  gap: 6,
  flexWrap: "wrap",
};
const emptyState: React.CSSProperties = {
  gridColumn: "1/-1",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  padding: "64px 24px",
  textAlign: "center",
};
