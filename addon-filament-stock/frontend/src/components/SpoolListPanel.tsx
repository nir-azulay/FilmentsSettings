import { useCallback, useEffect, useState } from "react";
import {
  AddonConfig,
  DEFAULT_ADDON_CONFIG,
  SpoolInstance,
  createSpool,
  deleteSpool,
  fetchAddonConfig,
  fetchSpools,
  markSpoolEmpty,
  unassignSpool,
  PackagingType,
} from "../api";
import LabelDialog from "./LabelDialog";

interface Props {
  colorStockId: number;
  colorHex: string;
  onStockChanged: () => Promise<void>;
}

const STATUS_BADGE: Record<string, { label: string; bg: string; color: string }> = {
  in_stock: { label: "In Stock", bg: "#e8f5e9", color: "#2e7d32" },
  in_tray: { label: "In Tray", bg: "#e3f2fd", color: "#1565c0" },
  empty: { label: "Empty", bg: "#f3f3f3", color: "#999" },
};

export default function SpoolListPanel({ colorStockId, colorHex, onStockChanged }: Props) {
  const [spools, setSpools] = useState<SpoolInstance[]>([]);
  const [loading, setLoading] = useState(true);
  const [config, setConfig] = useState<AddonConfig>(DEFAULT_ADDON_CONFIG);
  const [labelSpool, setLabelSpool] = useState<SpoolInstance | null>(null);
  const [adding, setAdding] = useState(false);
  const [addPkg, setAddPkg] = useState<PackagingType>("spool");

  const reload = useCallback(async () => {
    const rows = await fetchSpools(colorStockId);
    setSpools(rows);
  }, [colorStockId]);

  useEffect(() => {
    (async () => {
      const [rows, cfg] = await Promise.all([
        fetchSpools(colorStockId),
        fetchAddonConfig(),
      ]);
      setSpools(rows);
      setConfig(cfg);
      setLoading(false);
    })();
  }, [colorStockId]);

  const handleAdd = async () => {
    setAdding(true);
    try {
      await createSpool({ color_stock_id: colorStockId, packaging: addPkg });
      await reload();
      await onStockChanged();
    } finally {
      setAdding(false);
    }
  };

  const handleEmpty = async (uid: string) => {
    await markSpoolEmpty(uid);
    await reload();
    await onStockChanged();
  };

  const handleUnassign = async (uid: string) => {
    await unassignSpool(uid);
    await reload();
    await onStockChanged();
  };

  const handleDelete = async (uid: string) => {
    await deleteSpool(uid);
    await reload();
    await onStockChanged();
  };

  if (loading) return <div style={panelWrap}><span style={loadingText}>Loading spools...</span></div>;

  const activeSpools = spools.filter((s) => s.status !== "empty");
  const emptySpools = spools.filter((s) => s.status === "empty");

  return (
    <div style={panelWrap}>
      <div style={headerRow}>
        <span style={headerLabel}>Individual Spools</span>
        <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
          <select
            value={addPkg}
            onChange={(e) => setAddPkg(e.target.value as PackagingType)}
            style={selectStyle}
          >
            <option value="spool">Spool</option>
            <option value="refill">Refill</option>
          </select>
          <button onClick={handleAdd} disabled={adding} style={addBtn}>
            + Register
          </button>
        </div>
      </div>

      {activeSpools.length === 0 && emptySpools.length === 0 && (
        <p style={emptyText}>No individual spools registered yet. Click "+ Register" to add one and print a label.</p>
      )}

      {activeSpools.map((s) => {
        const badge = STATUS_BADGE[s.status] ?? STATUS_BADGE.in_stock;
        return (
          <div key={s.uid} style={spoolRow}>
            <div
              style={{
                width: 16, height: 16, borderRadius: 3,
                background: colorHex, border: "1px solid #ccc", flexShrink: 0,
              }}
            />
            <span style={uidText}>{s.uid}</span>
            <span style={{ ...statusBadge, background: badge.bg, color: badge.color }}>
              {badge.label}
            </span>
            {s.status === "in_tray" && s.remain_pct != null && (
              <span style={remainPct}>{s.remain_pct}%</span>
            )}
            <span style={pkgText}>{s.packaging}</span>
            <div style={actions}>
              <button
                onClick={() => setLabelSpool(s)}
                style={iconBtn}
                title="Print / download label"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="6 9 6 2 18 2 18 9" />
                  <path d="M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2" />
                  <rect x="6" y="14" width="12" height="8" />
                </svg>
              </button>
              {s.status === "in_tray" && (
                <button onClick={() => handleUnassign(s.uid)} style={iconBtn} title="Return to stock">
                  ↩
                </button>
              )}
              {s.status !== "empty" && (
                <button onClick={() => handleEmpty(s.uid)} style={iconBtn} title="Mark empty">
                  ✕
                </button>
              )}
              {s.status !== "in_tray" && (
                <button onClick={() => handleDelete(s.uid)} style={dangerIconBtn} title="Delete spool record">
                  🗑
                </button>
              )}
            </div>
          </div>
        );
      })}

      {emptySpools.length > 0 && (
        <details style={{ marginTop: 4 }}>
          <summary style={emptySummary}>
            {emptySpools.length} empty spool{emptySpools.length > 1 ? "s" : ""}
          </summary>
          {emptySpools.map((s) => (
            <div key={s.uid} style={{ ...spoolRow, opacity: 0.5 }}>
              <span style={uidText}>{s.uid}</span>
              <span style={{ ...statusBadge, ...STATUS_BADGE.empty }}>Empty</span>
              <span style={pkgText}>{s.packaging}</span>
              <div style={actions}>
                <button onClick={() => handleDelete(s.uid)} style={dangerIconBtn} title="Delete">
                  🗑
                </button>
              </div>
            </div>
          ))}
        </details>
      )}

      {labelSpool && (
        <LabelDialog
          spool={labelSpool}
          config={config}
          onClose={() => setLabelSpool(null)}
        />
      )}
    </div>
  );
}

const panelWrap: React.CSSProperties = {
  padding: "8px 12px", borderTop: "1px solid var(--ha-divider)",
  background: "rgba(0,0,0,0.015)",
};
const headerRow: React.CSSProperties = {
  display: "flex", justifyContent: "space-between", alignItems: "center",
  marginBottom: 6,
};
const headerLabel: React.CSSProperties = {
  fontSize: 11, fontWeight: 600, color: "var(--ha-secondary-text)",
  textTransform: "uppercase", letterSpacing: "0.05em",
};
const loadingText: React.CSSProperties = {
  fontSize: 12, color: "var(--ha-secondary-text)",
};
const emptyText: React.CSSProperties = {
  fontSize: 12, color: "var(--ha-disabled-text)", margin: "4px 0",
};
const selectStyle: React.CSSProperties = {
  fontSize: 11, padding: "3px 6px", borderRadius: 4,
  border: "1px solid var(--ha-divider)", background: "#fff",
};
const addBtn: React.CSSProperties = {
  fontSize: 11, fontWeight: 600, padding: "4px 10px",
  borderRadius: 4, border: "1px solid var(--ha-primary-color)",
  background: "var(--ha-primary-color-light)", color: "var(--ha-primary-color)",
  cursor: "pointer",
};
const spoolRow: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 6,
  padding: "5px 4px", borderRadius: 4, fontSize: 12,
};
const uidText: React.CSSProperties = {
  fontFamily: "monospace", fontSize: 11, fontWeight: 600,
  color: "var(--ha-primary-text)", minWidth: 90,
};
const statusBadge: React.CSSProperties = {
  fontSize: 10, fontWeight: 600, padding: "2px 6px",
  borderRadius: 4, textTransform: "uppercase", letterSpacing: "0.03em",
};
const remainPct: React.CSSProperties = {
  fontSize: 11, color: "var(--ha-primary-color)", fontWeight: 600,
};
const pkgText: React.CSSProperties = {
  fontSize: 10, color: "var(--ha-secondary-text)", textTransform: "uppercase",
};
const actions: React.CSSProperties = {
  marginLeft: "auto", display: "flex", gap: 4,
};
const iconBtn: React.CSSProperties = {
  width: 24, height: 24, display: "flex", alignItems: "center", justifyContent: "center",
  background: "rgba(0,0,0,0.05)", border: "none", borderRadius: 4,
  cursor: "pointer", fontSize: 12,
};
const dangerIconBtn: React.CSSProperties = {
  ...iconBtn,
  background: "rgba(244,67,54,0.08)", color: "var(--ha-error, #c62828)",
};
const emptySummary: React.CSSProperties = {
  fontSize: 11, color: "var(--ha-secondary-text)", cursor: "pointer",
  padding: "2px 0",
};
