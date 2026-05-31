import type { CSSProperties } from "react";
import { COLOR_FAMILIES, ColorFamilyId, familyMeta } from "../colorFamilies";

/** Multi-select chip row for filtering by colour family. Used by both
 *  the main stock dashboard and the Assign-from-stock dialog so the
 *  bucket definitions, swatch styling, and "available" filtering all
 *  stay in one place.
 *
 *  The component is purely presentational: it doesn't know what's being
 *  filtered, only which families are *present* in the current data
 *  (so empty buckets get hidden -- nobody wants a "Purple" chip with
 *  zero matches) and which are currently selected. Selection state
 *  lives in the parent so a clear-all button or external "show
 *  everything" toggle works naturally.
 */
interface Props {
  /** Set of family ids that exist in the currently-displayed data.
   *  Pass the output of `availableFamiliesFromColors(...)`. Families not
   *  in this set are omitted from the chip row entirely. */
  available: ReadonlySet<ColorFamilyId>;
  /** Currently selected family ids. Pass an empty Set to mean "no
   *  filter applied" (the "All colours" chip becomes the active one). */
  selected: ReadonlySet<ColorFamilyId>;
  /** Toggle handler. The parent owns the selection state; this hands
   *  back which id was clicked so the parent can do the Set mutation. */
  onToggle: (familyId: ColorFamilyId) => void;
  /** Clears the entire selection. Wired to the "All colours" chip. */
  onClear: () => void;
  /** Optional label override (e.g. "Colour · multi-select" on the
   *  dashboard vs "Colour" inside the assign dialog). */
  label?: string;
}

export default function ColorFilter({
  available,
  selected,
  onToggle,
  onClear,
  label = "Colour · multi-select",
}: Props) {
  // Render in the canonical family order from COLOR_FAMILIES, NOT the
  // arbitrary iteration order of `available`. Keeps the row stable
  // when data changes -- otherwise an added purple spool would
  // rearrange every chip and the user would have to re-orient.
  const visibleFamilies = COLOR_FAMILIES.filter((f) => available.has(f.id));
  if (visibleFamilies.length === 0) return null;

  return (
    <div style={wrap}>
      <span style={groupLabel}>{label}</span>
      <div style={chipRow}>
        <button
          type="button"
          onClick={onClear}
          style={chipStyle(selected.size === 0)}
        >
          All colours
        </button>
        {visibleFamilies.map((f) => {
          const active = selected.has(f.id);
          return (
            <button
              key={f.id}
              type="button"
              onClick={() => onToggle(f.id)}
              style={{ ...chipStyle(active), display: "inline-flex", alignItems: "center", gap: 6 }}
              title={`Filter by ${f.label}`}
            >
              <Swatch family={familyMeta(f.id)} />
              {f.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function Swatch({ family }: { family: ReturnType<typeof familyMeta> }) {
  // "Multi" uses a CSS gradient string instead of a flat colour, so
  // we apply it via `background` rather than `backgroundColor`.
  const isGradient = family.swatch.includes("gradient");
  return (
    <span
      aria-hidden="true"
      style={{
        width: 14,
        height: 14,
        borderRadius: "50%",
        background: isGradient ? family.swatch : undefined,
        backgroundColor: isGradient ? undefined : family.swatch,
        // Subtle ring so white-on-white still has an edge against the
        // chip background.
        boxShadow: "inset 0 0 0 1px rgba(0,0,0,0.18)",
        flexShrink: 0,
      }}
    />
  );
}

// ── styles ────────────────────────────────────────────────────────────────
// Match the existing FilterChip / chip styling used in Dashboard.tsx so
// the colour row visually slots in next to the Material and Brand rows.

function chipStyle(active: boolean): CSSProperties {
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

const wrap: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 6,
};
const groupLabel: CSSProperties = {
  fontSize: 10,
  fontWeight: 600,
  color: "var(--ha-disabled-text)",
  textTransform: "uppercase",
  letterSpacing: "0.08em",
};
const chipRow: CSSProperties = {
  display: "flex",
  gap: 6,
  flexWrap: "wrap",
};
