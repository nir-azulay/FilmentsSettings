import { Filament, FilamentPackaging, updateFilament } from "../api";

const LABELS: Record<FilamentPackaging, string> = {
  spool: "Spool",
  refill: "Refill",
};

interface Props {
  filament: Filament;
  onUpdate: () => Promise<void>;
  compact?: boolean;
}

export default function PackagingTypeControl({ filament, onUpdate, compact }: Props) {
  const current: FilamentPackaging = filament.packaging_type ?? "spool";

  const setPackaging = async (packaging_type: FilamentPackaging) => {
    if (packaging_type === current) return;
    await updateFilament(filament.id, { packaging_type });
    await onUpdate();
  };

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: compact ? 4 : 8,
        flexWrap: "wrap",
      }}
      title="Full spool vs refill (no spool)"
    >
      {!compact && (
        <span style={{ fontSize: 11, color: "var(--ha-secondary-text)", fontWeight: 500 }}>Packaging</span>
      )}
      {(["spool", "refill"] as const).map((value) => (
        <button
          key={value}
          type="button"
          onClick={() => setPackaging(value)}
          style={chip(current === value, value === "refill")}
        >
          {LABELS[value]}
        </button>
      ))}
    </div>
  );
}

function chip(active: boolean, refill: boolean): React.CSSProperties {
  return {
    padding: "4px 10px",
    borderRadius: 6,
    fontSize: 11,
    fontWeight: 600,
    border: active
      ? `1px solid ${refill ? "#ff9800" : "var(--ha-primary-color)"}`
      : "1px solid var(--ha-divider)",
    background: active
      ? refill
        ? "rgba(255,152,0,0.15)"
        : "var(--ha-primary-color-light)"
      : "var(--ha-surface-lower)",
    color: active
      ? refill
        ? "#e65100"
        : "var(--ha-primary-color)"
      : "var(--ha-secondary-text)",
    cursor: "pointer",
  };
}

export function packagingBadgeLabel(filament: Filament): string {
  return LABELS[filament.packaging_type ?? "spool"];
}
