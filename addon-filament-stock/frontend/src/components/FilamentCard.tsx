import { useEffect, useRef, useState } from "react";
import { ColorStatus, ColorStock, Filament, addColor, deleteColor, updateColor } from "../api";
import { getColorSuggestions, lookupColorHex } from "../colorMap";
import { colorTint, getColorVisual } from "../colorVisual";
import { deleteDangerBtn } from "../deleteDangerButton";
import {
  availableRefill,
  availableSpool,
  filamentHasLowStock,
  filamentInStockQty,
  filamentOrderedQty,
} from "../stockUtils";
import BrandLogo from "./BrandLogo";
import DeleteColorModal from "./DeleteColorModal";
import FilamentProfilePanel from "./FilamentProfilePanel";
import SpoolListPanel from "./SpoolListPanel";
import { SpoolIcon, SpoolStack } from "./SpoolIcon";
import TrashIconButton from "./TrashIconButton";

interface Props {
  filament: Filament;
  staplePools: Map<string, number>;
  ignoredStaples: Set<string>;
  onManageStock: () => void;
  onUpdate: () => Promise<void>;
  onRequestDeleteFilament: () => void;
}

function getMaterialColor(type: string): string {
  const map: Record<string, string> = {
    PLA: "#4caf50", PETG: "#03a9f4", ASA: "#ff9800",
    ABS: "#f44336", PA: "#9c27b0", TPU: "#e91e63", PLA_CF: "#00bcd4",
  };
  return map[type] ?? "#607d8b";
}

export default function FilamentCard({ filament, staplePools, ignoredStaples, onManageStock, onUpdate, onRequestDeleteFilament }: Props) {
  const inStockQty  = filamentInStockQty(filament.colors);
  const orderedQty  = filamentOrderedQty(filament.colors);
  const isLow       = filamentHasLowStock(filament, staplePools, ignoredStaples);
  const matColor    = getMaterialColor(filament.filament_type);
  const [showProfile, setShowProfile] = useState(false);

  return (
    <div id={`filament-${filament.id}`} className="ha-card" style={cardWrap}>
      {/* colored top strip */}
      <div style={{ height: 3, background: matColor }} />

      {/* header */}
      <div style={headerRow}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <BrandLogo url={filament.brand_logo_url} brand={filament.brand} size={36} />
          <div>
            <p style={cardTitle}>
              {filament.brand} <span style={{ color: matColor }}>{filament.material}</span>
            </p>
            <p style={cardSubtitle}>{filament.filament_type}</p>
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 4, alignItems: "flex-end" }}>
          {/* In Stock */}
          <div style={stockChip(isLow)}>
            {isLow && inStockQty === 0 ? null : isLow && <span style={{ fontSize: 9 }}>⚠ </span>}
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <SpoolIcon colorHex={isLow ? "#db4437" : "#43a047"} size={28} count={inStockQty > 1 ? inStockQty : undefined} />
              <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-start" }}>
                <span style={{ fontSize: 18, fontWeight: 600, lineHeight: 1 }}>{inStockQty}</span>
                <span style={{ fontSize: 9, opacity: 0.7 }}>in stock</span>
              </div>
            </div>
          </div>
          {/* Ordered */}
          {orderedQty > 0 && (
            <div style={orderedChip}>
              <span style={{ fontSize: 9 }}>⏳</span>
              <span style={{ fontSize: 13, fontWeight: 400, lineHeight: 1 }}>{orderedQty}</span>
              <span style={{ fontSize: 9, opacity: 0.7 }}>ordered</span>
            </div>
          )}
        </div>
      </div>

      {/* specs */}
      <div style={specsRow}>
        <SpecBadge label={filament.filament_type} color={matColor} />
        {filament.nozzle_temp_min && filament.nozzle_temp_max &&
          <SpecBadge label={`${filament.nozzle_temp_min}–${filament.nozzle_temp_max}°C`} />}
        {filament.bed_temp && <SpecBadge label={`Bed ${filament.bed_temp}°C`} />}
        {filament.density && <SpecBadge label={`${filament.density} g/cm³`} />}
      </div>

      {/* ── Inline color rows ── */}
      <div style={colorsSection}>
        <div style={colorsSectionHeader}>
          <span style={{ ...sectionLabel, display: "flex", alignItems: "center", gap: 6 }}>
            <SpoolIcon colorHex="#607d8b" size={18} />
            Colors in stock
          </span>
        </div>

        {filament.colors.length === 0 && (
          <p style={noColorsText}>No colors added</p>
        )}

        {filament.colors.map((c) => (
          <ColorRow key={c.id} color={c} onUpdate={onUpdate} />
        ))}

        <AddColorInline filamentId={filament.id} onUpdate={onUpdate} />
      </div>

      {/* actions */}
      <div style={actionRow}>
        <button onClick={onManageStock} style={manageBtn}>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 20V10M6 20V14M18 20V4" />
          </svg>
          History & Log
        </button>
        <button
          onClick={() => setShowProfile((s) => !s)}
          style={profileBtn}
          title="View filament configuration and download BambuStudio profile"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
          </svg>
          {showProfile ? "Hide profile" : "Profile"}
        </button>
        {filament.amazon_url && (
          <a href={filament.amazon_url} target="_blank" rel="noopener" style={buyBtn}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
              <polyline points="15 3 21 3 21 9" /><line x1="10" y1="14" x2="21" y2="3" />
            </svg>
            Buy
          </a>
        )}
        <button
          type="button"
          onClick={onRequestDeleteFilament}
          style={deleteDangerBtn}
          title="Delete this filament"
        >
          Delete
        </button>
      </div>

      {showProfile && <FilamentProfilePanel filament={filament} />}
    </div>
  );
}

const STATUS_CFG: Record<ColorStatus, { label: string; color: string; bg: string }> = {
  in_stock:    { label: "In Stock",    color: "#4caf50", bg: "rgba(76,175,80,0.15)"  },
  ordered:     { label: "Ordered",     color: "#03a9f4", bg: "rgba(3,169,244,0.15)"  },
  out_of_stock:{ label: "Out of Stock",color: "#f44336", bg: "rgba(244,67,54,0.15)"  },
};

/* ── Editable color entity row ────────────────────────────────────────────── */
function ColorRow({ color, onUpdate }: { color: ColorStock; onUpdate: () => Promise<void> }) {
  const [hovered, setHovered] = useState(false);
  const [qty, setQty] = useState(color.quantity);
  const [qtyUsed, setQtyUsed] = useState(color.quantity_used ?? 0);
  const [qtyRefill, setQtyRefill] = useState(color.quantity_refill ?? 0);
  const [usedRefill, setUsedRefill] = useState(color.used_refill ?? 0);
  const [status, setStatus] = useState<ColorStatus>(color.status ?? "in_stock");
  const [saving, setSaving] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletingColor, setDeletingColor] = useState(false);
  const [showSpools, setShowSpools] = useState(false);

  useEffect(() => {
    setQty(color.quantity);
    setQtyUsed(color.quantity_used ?? 0);
    setQtyRefill(color.quantity_refill ?? 0);
    setUsedRefill(color.used_refill ?? 0);
    setStatus(color.status ?? "in_stock");
  }, [color.id, color.quantity, color.quantity_used, color.quantity_refill, color.used_refill, color.status]);

  const remainingSpool = availableSpool({ ...color, quantity: qty, quantity_used: qtyUsed });
  const remainingRefill = availableRefill({ ...color, quantity_refill: qtyRefill, used_refill: usedRefill });
  const remainingTotal = remainingSpool + remainingRefill;

  const handleQtyChange = async (newQty: number) => {
    setQty(newQty);
    setSaving(true);
    await updateColor(color.id, { quantity: newQty });
    await onUpdate();
    setSaving(false);
  };

  const handleAddSpool = async () => {
    const newQty = qty + 1;
    setQty(newQty);
    setSaving(true);
    const updates: Parameters<typeof updateColor>[1] = { quantity: newQty };
    if (status === "out_of_stock") {
      setStatus("in_stock");
      updates.status = "in_stock";
    }
    await updateColor(color.id, updates);
    await onUpdate();
    setSaving(false);
  };

  const handleUseSpool = async () => {
    const newUsed = Math.min(qtyUsed + 1, qty);
    setQtyUsed(newUsed);
    setSaving(true);
    const updates: Parameters<typeof updateColor>[1] = { quantity_used: newUsed };
    // Only auto-flip to out_of_stock when both counters are exhausted.
    if (newUsed >= qty && remainingRefill <= 0) {
      setStatus("out_of_stock");
      updates.status = "out_of_stock";
    }
    await updateColor(color.id, updates);
    await onUpdate();
    setSaving(false);
  };

  const handleAddRefill = async () => {
    const newQty = qtyRefill + 1;
    setQtyRefill(newQty);
    setSaving(true);
    const updates: Parameters<typeof updateColor>[1] = { quantity_refill: newQty };
    if (status === "out_of_stock") {
      setStatus("in_stock");
      updates.status = "in_stock";
    }
    await updateColor(color.id, updates);
    await onUpdate();
    setSaving(false);
  };

  const handleUseRefill = async () => {
    const newUsed = Math.min(usedRefill + 1, qtyRefill);
    setUsedRefill(newUsed);
    setSaving(true);
    const updates: Parameters<typeof updateColor>[1] = { used_refill: newUsed };
    if (newUsed >= qtyRefill && remainingSpool <= 0) {
      setStatus("out_of_stock");
      updates.status = "out_of_stock";
    }
    await updateColor(color.id, updates);
    await onUpdate();
    setSaving(false);
  };

  const handleReceive = async () => {
    setStatus("in_stock");
    await updateColor(color.id, { status: "in_stock" });
    await onUpdate();
  };

  const handleMarkOrdered = async () => {
    setStatus("ordered");
    await updateColor(color.id, { status: "ordered" });
    await onUpdate();
  };

  const executeDeleteColor = async () => {
    if (deletingColor) return;
    setDeletingColor(true);
    try {
      await deleteColor(color.id);
      setShowDeleteModal(false);
      await onUpdate();
    } finally {
      setDeletingColor(false);
    }
  };

  const cfg = STATUS_CFG[status];
  const vis = getColorVisual(color.color_hex, status !== "in_stock");

  return (
    <div
      className="ha-entity-row color-stock-row"
      style={{
        ...colorEntityRow,
        background: hovered ? vis.bgHover : vis.bg,
        borderLeft: `4px solid ${vis.accent}`,
        boxShadow: hovered ? `inset 0 0 0 1px ${vis.border}` : undefined,
        transition: "background 0.15s, box-shadow 0.15s",
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <div className="color-stock-row__line">
        {status === "in_stock" && remainingTotal > 0 ? (
          <SpoolStack colorHex={color.color_hex} count={remainingTotal} size={28} />
        ) : (
          <SpoolIcon colorHex={color.color_hex} size={32} muted={status !== "in_stock"} />
        )}

        <span
          className="color-stock-row__name"
          style={{
            fontSize: 15,
            fontWeight: 700,
            color: "var(--ha-primary-text)",
            textShadow: "0 1px 2px rgba(255,255,255,0.55)",
            minWidth: 40,
            flex: "1 1 40px",
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}
          title={`${color.color_name} • ${color.color_hex}`}
        >
          {color.color_name}
        </span>

        {/* ══ IN STOCK ══ Two pills (spool / refill), each with Add + Use */}
        {status === "in_stock" && (
          <div style={pillRow}>
            <div style={pillStack}>
              <PackagingPill
                kind="spool"
                remaining={remainingSpool}
                used={qtyUsed}
                total={qty}
                accent={vis.accent}
                tint={colorTint(color.color_hex, 0.22)}
                onAdd={handleAddSpool}
                onUse={handleUseSpool}
                disabled={saving}
              />
              <PackagingPill
                kind="refill"
                remaining={remainingRefill}
                used={usedRefill}
                total={qtyRefill}
                accent={vis.accent}
                tint="rgba(255,152,0,0.18)"
                onAdd={handleAddRefill}
                onUse={handleUseRefill}
                disabled={saving}
              />
            </div>
            <div style={iconColumn}>
              <TrashIconButton onClick={() => setShowDeleteModal(true)} title="Delete color" />
              <button onClick={() => setShowSpools(!showSpools)} style={printIconBtn} title="Spools & Labels">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="6 9 6 2 18 2 18 9" />
                  <path d="M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2" />
                  <rect x="6" y="14" width="12" height="8" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* ══ ORDERED layout ══ */}
        {status === "ordered" && (
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 4, opacity: hovered ? 1 : 0.75, transition: "opacity 0.15s" }}>
              <button onClick={() => handleQtyChange(Math.max(0, qty - 1))} style={stepBtn}>−</button>
              <SpoolIcon colorHex={color.color_hex} size={28} count={qty > 1 ? qty : undefined} muted />
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", minWidth: 32 }}>
                <span style={{ fontSize: 18, fontWeight: 700, lineHeight: 1, color: cfg.color }}>{qty}</span>
                <span style={{ fontSize: 9, color: "var(--ha-secondary-text)" }}>ordered</span>
              </div>
              <button onClick={() => handleQtyChange(qty + 1)} style={stepBtn}>+</button>
            </div>
            <button onClick={handleReceive} style={receiveBtn}>
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              Arrived
            </button>
            <div style={iconColumn}>
              <TrashIconButton onClick={() => setShowDeleteModal(true)} title="Delete color" />
              <button onClick={() => setShowSpools(!showSpools)} style={printIconBtn} title="Spools & Labels">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="6 9 6 2 18 2 18 9" />
                  <path d="M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2" />
                  <rect x="6" y="14" width="12" height="8" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* ══ OUT OF STOCK layout ══ */}
        {status === "out_of_stock" && (
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "nowrap" }}>
            <span style={{ fontSize: 11, color: "var(--ha-error)", fontWeight: 600 }}>Out of stock</span>
            <button type="button" onClick={handleAddSpool} disabled={saving} style={addSpoolBtnCompact} title="Add 1 spool to stock">
              + Spool
            </button>
            <button type="button" onClick={handleAddRefill} disabled={saving} style={addRefillBtnCompact} title="Add 1 refill to stock">
              + Refill
            </button>
            <button onClick={handleMarkOrdered} style={reorderBtn}>↺ Reorder</button>
            <div style={iconColumn}>
              <TrashIconButton onClick={() => setShowDeleteModal(true)} title="Delete color" />
              <button onClick={() => setShowSpools(!showSpools)} style={printIconBtn} title="Spools & Labels">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="6 9 6 2 18 2 18 9" />
                  <path d="M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2" />
                  <rect x="6" y="14" width="12" height="8" />
                </svg>
              </button>
            </div>
          </div>
        )}
      </div>

      {showSpools && (
        <SpoolListPanel
          colorStockId={color.id}
          colorHex={color.color_hex}
          onStockChanged={onUpdate}
        />
      )}

      {showDeleteModal && (
        <DeleteColorModal
          colorName={color.color_name}
          confirming={deletingColor}
          onCancel={() => !deletingColor && setShowDeleteModal(false)}
          onConfirm={executeDeleteColor}
        />
      )}
    </div>
  );
}

/* ── Per-packaging-type pill (Spool or Refill) ───────────────────────────── */
interface PackagingPillProps {
  kind: "spool" | "refill";
  remaining: number;
  used: number;
  total: number;
  accent: string;
  tint: string;
  onAdd: () => Promise<void>;
  onUse: () => Promise<void>;
  disabled?: boolean;
}

function PackagingPill({ kind, remaining, used, total, accent, tint, onAdd, onUse, disabled }: PackagingPillProps) {
  const isRefill = kind === "refill";
  const label = isRefill ? "Refill" : "Spool";
  const labelColor = isRefill ? "#e65100" : accent;
  const useBtnStyle = isRefill ? useRefillBtnCompact : useBtnCompact;
  const addBtnStyle = isRefill ? addRefillBtnCompact : addSpoolBtnCompact;
  const empty = total === 0;
  const exhausted = remaining <= 0 && total > 0;

  return (
    <div style={{
      ...packagingPillWrap,
      opacity: empty ? 0.45 : 1,
      borderColor: empty ? "var(--ha-divider)" : isRefill ? "#ffb74d" : "var(--ha-divider)",
    }}>
      <span style={{ fontSize: 9, fontWeight: 700, color: labelColor, letterSpacing: "0.04em", textTransform: "uppercase" }}>
        {label}
      </span>
      <span
        style={{
          ...packagingPillCount,
          color: exhausted ? "var(--ha-error)" : labelColor,
          background: empty ? "rgba(0,0,0,0.04)" : tint,
        }}
        title={total === 0 ? `No ${label.toLowerCase()}s tracked` : `${remaining} ${label.toLowerCase()}(s) left`}
      >
        {remaining}
      </span>
      <span style={{ fontSize: 10, color: "var(--ha-secondary-text)", minWidth: 24, textAlign: "right" }}>
        {used}/{total}
      </span>
      <button type="button" onClick={onAdd} disabled={disabled} style={addBtnStyle} title={`Add 1 ${label.toLowerCase()}`}>
        +
      </button>
      <button
        type="button"
        onClick={onUse}
        disabled={disabled || exhausted || empty}
        style={{ ...useBtnStyle, opacity: exhausted || empty ? 0.35 : 1, cursor: exhausted || empty ? "not-allowed" : "pointer" }}
        title={`Mark 1 ${label.toLowerCase()} as used`}
      >
        Use
      </button>
    </div>
  );
}

/* ── Add color inline row ─────────────────────────────────────────────────── */
function AddColorInline({ filamentId, onUpdate }: { filamentId: number; onUpdate: () => Promise<void> }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [hex, setHex] = useState("#808080");
  const [qty, setQty] = useState(1);
  const [suggestions, setSuggestions] = useState<Array<{ name: string; hex: string }>>([]);
  const [showSug, setShowSug] = useState(false);
  const [saving, setSaving] = useState(false);
  const sugRef = useRef<HTMLDivElement>(null);

  const handleNameChange = (v: string) => {
    setName(v);
    const found = lookupColorHex(v);
    if (found) setHex(found);
    const sugg = getColorSuggestions(v);
    setSuggestions(sugg);
    setShowSug(sugg.length > 0 && v.length > 0);
  };

  const pickSuggestion = (n: string, h: string) => {
    setName(n.charAt(0).toUpperCase() + n.slice(1));
    setHex(h);
    setShowSug(false);
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    await addColor(filamentId, { color_name: name, color_hex: hex, quantity: qty, status: "in_stock" });
    setName(""); setHex("#808080"); setQty(1); setOpen(false);
    await onUpdate();
    setSaving(false);
  };

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} style={addRowBtn}>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        Add color
      </button>
    );
  }

  return (
    <form onSubmit={handleAdd} style={addForm}>
      <label style={{ cursor: "pointer", flexShrink: 0, display: "flex" }} title="Pick color">
        <SpoolIcon colorHex={hex} size={32} />
        <input type="color" value={hex} onChange={(e) => setHex(e.target.value)} style={{ display: "none" }} />
      </label>

      {/* name input with suggestions */}
      <div style={{ position: "relative", flex: 1 }}>
        <input
          type="text" value={name} onChange={(e) => handleNameChange(e.target.value)}
          onFocus={() => suggestions.length > 0 && setShowSug(true)}
          onBlur={() => setTimeout(() => setShowSug(false), 150)}
          placeholder="Color name…"
          style={addInput} autoFocus required
        />
        {showSug && (
          <div ref={sugRef} style={sugBox}>
            {suggestions.map((s) => (
              <div key={s.name} style={sugItem} onMouseDown={() => pickSuggestion(s.name, s.hex)}>
                <div style={{ width: 10, height: 10, borderRadius: 2, background: s.hex, border: "1px solid rgba(255,255,255,0.15)", flexShrink: 0 }} />
                <span style={{ flex: 1 }}>{s.name}</span>
                <span style={{ opacity: 0.4, fontSize: 10, fontFamily: "monospace" }}>{s.hex}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* qty */}
      <input type="number" min={0} value={qty} onChange={(e) => setQty(Number(e.target.value))}
        style={{ ...addInput, width: 44, textAlign: "center" }} />

      {/* submit */}
      <button type="submit" disabled={saving} style={addSubmitBtn}>
        {saving ? "…" : "Add"}
      </button>

      {/* cancel */}
      <button type="button" onClick={() => setOpen(false)} style={cancelBtn}>✕</button>
    </form>
  );
}

function SpecBadge({ label, color }: { label: string; color?: string }) {
  return (
    <span style={{
      display: "inline-flex", alignItems: "center",
      padding: "2px 8px", borderRadius: 12,
      fontSize: 11, fontWeight: 500,
      background: color ? `${color}15` : "rgba(0,0,0,0.04)",
      color: color ?? "var(--ha-secondary-text)",
      border: `1px solid ${color ? `${color}30` : "transparent"}`,
    }}>
      {label}
    </span>
  );
}

/* ─── Styles ─────────────────────────────────────────────────────────────── */
const cardWrap: React.CSSProperties = {
  display: "flex", flexDirection: "column", background: "var(--ha-card-bg)",
};
const headerRow: React.CSSProperties = {
  display: "flex", justifyContent: "space-between", alignItems: "flex-start",
  padding: "14px 16px 8px",
};
const cardTitle: React.CSSProperties = {
  fontSize: 14, fontWeight: 500, lineHeight: 1.3, color: "var(--ha-primary-text)",
};
const cardSubtitle: React.CSSProperties = {
  fontSize: 12, color: "var(--ha-secondary-text)", marginTop: 1,
};
const stockChip = (low: boolean): React.CSSProperties => ({
  display: "flex", flexDirection: "column", alignItems: "center",
  padding: "5px 10px", borderRadius: 8,
  background: low ? "var(--ha-error-bg)" : "rgba(0,0,0,0.04)",
  color: low ? "var(--ha-error)" : "var(--ha-primary-text)",
  minWidth: 48, flexShrink: 0,
});
const orderedChip: React.CSSProperties = {
  display: "flex", flexDirection: "column", alignItems: "center",
  padding: "3px 8px", borderRadius: 8, gap: 1,
  background: "rgba(3,169,244,0.12)",
  color: "var(--ha-primary-color)",
  minWidth: 48, flexShrink: 0,
};

const specsRow: React.CSSProperties = {
  display: "flex", flexWrap: "wrap", gap: 4, padding: "0 16px 10px",
};
const colorsSection: React.CSSProperties = {
  borderTop: "1px solid var(--ha-divider)",
};
const colorsSectionHeader: React.CSSProperties = {
  padding: "8px 16px 4px",
};
const sectionLabel: React.CSSProperties = {
  fontSize: 11, fontWeight: 500, color: "var(--ha-secondary-text)",
  textTransform: "uppercase", letterSpacing: "0.06em",
};
const noColorsText: React.CSSProperties = {
  fontSize: 12, color: "var(--ha-disabled-text)",
  padding: "6px 16px 4px",
};
const colorEntityRow: React.CSSProperties = {
  padding: "10px 10px 10px 12px",
  margin: "4px 10px",
  borderRadius: 10,
  minHeight: 52,
};
const stepBtn: React.CSSProperties = {
  width: 20, height: 20,
  display: "flex", alignItems: "center", justifyContent: "center",
  background: "rgba(0,0,0,0.06)", border: "none",
  borderRadius: 4, color: "var(--ha-primary-text)",
  fontSize: 14, cursor: "pointer", lineHeight: 1,
};
const pillRow: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 6,
  marginLeft: "auto", flexShrink: 0,
};
const pillStack: React.CSSProperties = {
  display: "flex", flexDirection: "column", gap: 4,
};
const packagingPillWrap: React.CSSProperties = {
  display: "inline-flex", alignItems: "center", gap: 4,
  padding: "4px 6px", borderRadius: 8,
  border: "1px solid var(--ha-divider)",
  background: "rgba(0,0,0,0.02)",
};
const packagingPillCount: React.CSSProperties = {
  minWidth: 18, padding: "1px 6px", borderRadius: 4,
  fontSize: 12, fontWeight: 700, textAlign: "center",
};
const addRowBtn: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 5,
  width: "100%", padding: "8px 16px",
  background: "none", border: "none",
  color: "var(--ha-primary-color)", fontSize: 12,
  cursor: "pointer", textAlign: "left",
  borderTop: "1px solid var(--ha-divider)",
};
const addForm: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 6,
  padding: "6px 16px 8px",
  borderTop: "1px solid var(--ha-divider)",
  background: "rgba(0,0,0,0.01)",
};
const addInput: React.CSSProperties = {
  padding: "5px 8px", fontSize: 12,
  background: "#fff",
  border: "1px solid var(--ha-divider)",
  borderRadius: 4, color: "var(--ha-primary-text)", outline: "none",
};
const addSubmitBtn: React.CSSProperties = {
  padding: "5px 10px", background: "var(--ha-primary-color)",
  color: "#fff", border: "none", borderRadius: 4,
  fontSize: 12, fontWeight: 500, cursor: "pointer",
};
const cancelBtn: React.CSSProperties = {
  background: "none", border: "none",
  color: "var(--ha-disabled-text)", cursor: "pointer",
  fontSize: 13, padding: "2px 4px",
};
const actionRow: React.CSSProperties = {
  display: "flex", gap: 8, padding: "10px 16px 14px",
  borderTop: "1px solid var(--ha-divider)", marginTop: "auto",
};
const manageBtn: React.CSSProperties = {
  flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 5,
  padding: "7px 12px",
  background: "var(--ha-primary-color-light)", color: "var(--ha-primary-color)",
  border: "none", borderRadius: 4, fontSize: 13, fontWeight: 500, cursor: "pointer",
};
const buyBtn: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 5, padding: "7px 12px",
  background: "rgba(255,152,0,0.12)", color: "var(--ha-warning)",
  border: "none", borderRadius: 4, fontSize: 13, fontWeight: 500,
  textDecoration: "none", cursor: "pointer",
};
const profileBtn: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 5, padding: "7px 12px",
  background: "rgba(0,0,0,0.04)", color: "var(--ha-primary-text)",
  border: "1px solid var(--ha-divider)", borderRadius: 4,
  fontSize: 13, fontWeight: 500, cursor: "pointer",
};
const receiveBtn: React.CSSProperties = {
  display: "inline-flex", alignItems: "center", gap: 4,
  padding: "5px 10px", borderRadius: 6,
  fontSize: 11, fontWeight: 600,
  background: "#c2f2c1", color: "#036730",
  border: "1px solid #93da98",
  cursor: "pointer", whiteSpace: "nowrap",
};
const addSpoolBtnCompact: React.CSSProperties = {
  display: "inline-flex", alignItems: "center", justifyContent: "center",
  padding: "4px 8px", borderRadius: 6,
  fontSize: 11, fontWeight: 600,
  background: "#c2f2c1", color: "#036730",
  border: "1px solid #93da98",
  cursor: "pointer",
  whiteSpace: "nowrap",
};
const useBtnCompact: React.CSSProperties = {
  display: "inline-flex", alignItems: "center", justifyContent: "center",
  padding: "4px 8px", borderRadius: 6,
  fontSize: 11, fontWeight: 600,
  background: "#ffe0c8", color: "#7e2900",
  border: "1px solid #ffbb89",
  whiteSpace: "nowrap",
};
const addRefillBtnCompact: React.CSSProperties = {
  ...{
    display: "inline-flex", alignItems: "center", justifyContent: "center",
    padding: "4px 8px", borderRadius: 6,
    fontSize: 11, fontWeight: 600,
    whiteSpace: "nowrap", cursor: "pointer",
  },
  background: "#ffe0b2", color: "#bf360c",
  border: "1px solid #ffb74d",
};
const useRefillBtnCompact: React.CSSProperties = {
  display: "inline-flex", alignItems: "center", justifyContent: "center",
  padding: "4px 8px", borderRadius: 6,
  fontSize: 11, fontWeight: 600,
  background: "#fff3e0", color: "#bf360c",
  border: "1px solid #ffb74d",
  whiteSpace: "nowrap",
};
const reorderBtn: React.CSSProperties = {
  display: "inline-flex", alignItems: "center", gap: 4,
  padding: "5px 10px", borderRadius: 6,
  fontSize: 11, fontWeight: 600,
  background: "#dff3fc", color: "#006787",
  border: "1px solid #7bd4fb",
  cursor: "pointer", whiteSpace: "nowrap",
};
const sugBox: React.CSSProperties = {
  position: "absolute", top: "100%", left: 0, right: 0,
  background: "#fff", border: "1px solid var(--ha-divider)",
  borderRadius: 4, marginTop: 2, zIndex: 10,
  maxHeight: 150, overflowY: "auto", boxShadow: "0 8px 24px rgba(0,0,0,0.15)",
};
const sugItem: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 7,
  padding: "5px 10px", cursor: "pointer", fontSize: 12,
};
const iconColumn: React.CSSProperties = {
  display: "flex", flexDirection: "column", alignItems: "center", gap: 4,
  flexShrink: 0,
};
const printIconBtn: React.CSSProperties = {
  width: 28, height: 28,
  display: "flex", alignItems: "center", justifyContent: "center",
  background: "rgba(3,169,244,0.1)",
  border: "1px solid rgba(3,169,244,0.25)",
  borderRadius: 6, cursor: "pointer",
  color: "var(--ha-primary-color, #1976d2)",
  flexShrink: 0,
};
