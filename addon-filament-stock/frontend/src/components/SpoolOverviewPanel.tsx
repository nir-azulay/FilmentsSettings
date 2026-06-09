import { useCallback, useEffect, useMemo, useState } from "react";
import {
  AddonConfig,
  DEFAULT_ADDON_CONFIG,
  SpoolInstance,
  SpoolStatus,
  SpoolsSummary,
  deleteSpool,
  fetchAddonConfig,
  fetchSpoolsSummary,
  logUsage,
  markSpoolEmpty,
  unassignSpool,
} from "../api";
import BatchLabelDialog from "./BatchLabelDialog";
import LabelDialog from "./LabelDialog";
import SpoolTimelineDialog from "./SpoolTimelineDialog";
import { SpoolIcon } from "./SpoolIcon";

interface Props {
  onStockChanged: () => void;
}

const STATUS_BADGE: Record<string, { label: string; bg: string; color: string }> = {
  in_stock: { label: "In Stock", bg: "var(--ha-pill-success-bg)", color: "var(--ha-pill-success-text)" },
  in_tray: { label: "In Tray", bg: "var(--ha-pill-info-bg)", color: "var(--ha-pill-info-text)" },
  empty: { label: "Empty", bg: "var(--ha-pill-gray-bg)", color: "var(--ha-pill-gray-text)" },
};

const COLLAPSE_KEY = "filament_stock_spool_overview_collapsed";

function timeAgo(iso: string | null): string {
  if (!iso) return "";
  const ms = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(ms / 60_000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

export default function SpoolOverviewPanel({ onStockChanged }: Props) {
  const [data, setData] = useState<SpoolsSummary | null>(null);
  const [config, setConfig] = useState<AddonConfig>(DEFAULT_ADDON_CONFIG);
  const [loading, setLoading] = useState(true);
  const [collapsed, setCollapsed] = useState(
    () => localStorage.getItem(COLLAPSE_KEY) === "1",
  );
  const [statusFilter, setStatusFilter] = useState<SpoolStatus | "all">("all");
  const [search, setSearch] = useState("");
  const [labelSpool, setLabelSpool] = useState<SpoolInstance | null>(null);
  const [timelineUid, setTimelineUid] = useState<string | null>(null);
  const [selected, setSelected] = useState<Set<string>>(() => new Set());
  const [showBatchPrint, setShowBatchPrint] = useState(false);

  const reload = useCallback(async () => {
    const [summary, cfg] = await Promise.all([
      fetchSpoolsSummary(),
      fetchAddonConfig(),
    ]);
    setData(summary);
    setConfig(cfg);
  }, []);

  useEffect(() => {
    reload().finally(() => setLoading(false));
  }, [reload]);

  const toggleCollapse = () => {
    setCollapsed((prev) => {
      localStorage.setItem(COLLAPSE_KEY, prev ? "0" : "1");
      return !prev;
    });
  };

  const filtered = useMemo(() => {
    if (!data) return [];
    let list = data.spools;
    if (statusFilter !== "all") {
      list = list.filter((s) => s.status === statusFilter);
    }
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      list = list.filter(
        (s) =>
          s.uid.toLowerCase().includes(q) ||
          (s.brand ?? "").toLowerCase().includes(q) ||
          (s.material ?? "").toLowerCase().includes(q) ||
          (s.color_name ?? "").toLowerCase().includes(q),
      );
    }
    return list;
  }, [data, statusFilter, search]);

  const toggleSelect = (uid: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(uid)) next.delete(uid); else next.add(uid);
      return next;
    });
  };

  const toggleSelectAll = () => {
    if (selected.size === filtered.length) {
      setSelected(new Set());
    } else {
      setSelected(new Set(filtered.map((s) => s.uid)));
    }
  };

  const selectedSpools = useMemo(
    () => (data?.spools ?? []).filter((s) => selected.has(s.uid)),
    [data, selected],
  );

  const handleUnassign = async (uid: string) => {
    await unassignSpool(uid);
    await reload();
    onStockChanged();
  };

  const handleEmpty = async (uid: string) => {
    await markSpoolEmpty(uid);
    await reload();
    onStockChanged();
  };

  const handleDelete = async (uid: string) => {
    await deleteSpool(uid);
    await reload();
    onStockChanged();
  };

  const handleLogUsage = async (spool: SpoolInstance) => {
    const gramsStr = window.prompt(`Log usage for ${spool.uid}\n\nEnter grams used:`);
    if (!gramsStr) return;
    const grams = parseFloat(gramsStr);
    if (isNaN(grams) || grams <= 0) { window.alert("Invalid amount"); return; }
    const printName = window.prompt("Print name (optional):") ?? "";
    try {
      await logUsage({
        color_stock_id: spool.color_stock_id,
        spool_instance_id: spool.id,
        grams_used: grams,
        source: "manual",
        print_name: printName,
      });
    } catch (e: any) {
      window.alert(`Failed to log usage: ${e.message}`);
    }
  };

  return (
    <section className="ha-card" style={card}>
      <div style={headerRow} onClick={toggleCollapse} role="button">
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <svg
            width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="var(--ha-primary-text)" strokeWidth="2"
            strokeLinecap="round" strokeLinejoin="round"
            style={{ transform: collapsed ? "rotate(-90deg)" : "rotate(0)", transition: "transform 0.2s" }}
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
          <h3 style={sectionTitle}>All Spools</h3>
          {data && (
            <div style={pillRow}>
              <span style={{ ...pill, ...pillGreen }}>{data.in_stock} In Stock</span>
              <span style={{ ...pill, ...pillBlue }}>{data.in_tray} In Tray</span>
              <span style={{ ...pill, ...pillGray }}>{data.empty} Empty</span>
            </div>
          )}
        </div>
      </div>

      {!collapsed && (
        <div style={bodyWrap}>
          {loading && <p style={infoText}>Loading spools...</p>}

          {!loading && data && (
            <>
              <div style={controlsRow}>
                <div style={filterRow}>
                  {(["all", "in_stock", "in_tray", "empty"] as const).map((f) => (
                    <button
                      key={f}
                      onClick={() => setStatusFilter(f)}
                      style={statusFilter === f ? filterBtnActive : filterBtn}
                    >
                      {f === "all" ? "All" : STATUS_BADGE[f]?.label ?? f}
                    </button>
                  ))}
                </div>
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search UID, brand, material, color..."
                  style={searchInput}
                />
              </div>

              {filtered.length > 0 && (
                <div style={batchBar}>
                  <label style={selectAllLabel}>
                    <input
                      type="checkbox"
                      checked={selected.size > 0 && selected.size === filtered.length}
                      ref={(el) => {
                        if (el) el.indeterminate = selected.size > 0 && selected.size < filtered.length;
                      }}
                      onChange={toggleSelectAll}
                    />
                    {selected.size > 0 ? `${selected.size} selected` : "Select all"}
                  </label>
                  {selected.size > 0 && (
                    <button
                      onClick={() => setShowBatchPrint(true)}
                      style={batchPrintBtn}
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="6 9 6 2 18 2 18 9" />
                        <path d="M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2" />
                        <rect x="6" y="14" width="12" height="8" />
                      </svg>
                      Print {selected.size} Label{selected.size > 1 ? "s" : ""}
                    </button>
                  )}
                </div>
              )}

              {filtered.length === 0 ? (
                <p style={infoText}>No spools match your filters.</p>
              ) : (
                <div style={listWrap}>
                  {filtered.map((s) => {
                    const badge = STATUS_BADGE[s.status] ?? STATUS_BADGE.in_stock;
                    const stateTs =
                      s.status === "empty" ? s.emptied_at :
                      s.status === "in_tray" ? s.assigned_at :
                      s.created_at;

                    return (
                      <div
                        key={s.uid}
                        style={spoolRow}
                        draggable={s.status === "in_stock"}
                        onDragStart={(e) => {
                          e.dataTransfer.setData("application/x-spool-uid", s.uid);
                          e.dataTransfer.effectAllowed = "move";
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={selected.has(s.uid)}
                          onChange={() => toggleSelect(s.uid)}
                          style={rowCheckbox}
                        />
                        <SpoolIcon colorHex={s.color_hex ?? "#808080"} size={22} />
                        <span style={uidText}>{s.uid}</span>
                        <span style={brandText}>
                          {s.brand} {s.material}
                        </span>
                        <span style={colorText}>{s.color_name}</span>
                        <span style={{ ...statusBadgeSt, background: badge.bg, color: badge.color }}>
                          {badge.label}
                        </span>
                        <span style={agoText}>{timeAgo(stateTs)}</span>
                        <div style={actions}>
                          <button onClick={() => setLabelSpool(s)} style={iconBtn} title="Label">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <polyline points="6 9 6 2 18 2 18 9" />
                              <path d="M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2" />
                              <rect x="6" y="14" width="12" height="8" />
                            </svg>
                          </button>
                          <button onClick={() => setTimelineUid(s.uid)} style={iconBtn} title="Timeline">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
                            </svg>
                          </button>
                          {s.status !== "empty" && (
                            <button onClick={() => handleLogUsage(s)} style={iconBtn} title="Log usage">
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M12 20V10M6 20V14M18 20V4" />
                              </svg>
                            </button>
                          )}
                          {s.status === "in_tray" && (
                            <button onClick={() => handleUnassign(s.uid)} style={iconBtn} title="Return to stock">↩</button>
                          )}
                          {s.status !== "empty" && (
                            <button onClick={() => handleEmpty(s.uid)} style={iconBtn} title="Mark empty">✕</button>
                          )}
                          {s.status !== "in_tray" && (
                            <button onClick={() => handleDelete(s.uid)} style={dangerBtn} title="Delete">🗑</button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </>
          )}
        </div>
      )}

      {labelSpool && (
        <LabelDialog spool={labelSpool} config={config} onClose={() => setLabelSpool(null)} />
      )}
      {timelineUid && (
        <SpoolTimelineDialog uid={timelineUid} onClose={() => setTimelineUid(null)} />
      )}
      {showBatchPrint && selectedSpools.length > 0 && (
        <BatchLabelDialog
          spools={selectedSpools}
          config={config}
          onClose={() => { setShowBatchPrint(false); setSelected(new Set()); }}
        />
      )}
    </section>
  );
}

const card: React.CSSProperties = {
  marginBottom: 16,
};
const headerRow: React.CSSProperties = {
  display: "flex", alignItems: "center", justifyContent: "space-between",
  padding: "14px 20px", cursor: "pointer",
  userSelect: "none",
};
const sectionTitle: React.CSSProperties = {
  margin: 0, fontSize: 16, fontWeight: 600, color: "var(--ha-primary-text)",
};
const pillRow: React.CSSProperties = {
  display: "flex", gap: 6,
};
const pill: React.CSSProperties = {
  fontSize: 10, fontWeight: 600, padding: "2px 8px",
  borderRadius: 10, textTransform: "uppercase", letterSpacing: "0.03em",
};
const pillGreen: React.CSSProperties = { background: "var(--ha-pill-success-bg)", color: "var(--ha-pill-success-text)" };
const pillBlue: React.CSSProperties = { background: "var(--ha-pill-info-bg)", color: "var(--ha-pill-info-text)" };
const pillGray: React.CSSProperties = { background: "var(--ha-pill-gray-bg)", color: "var(--ha-pill-gray-text)" };
const bodyWrap: React.CSSProperties = {
  padding: "0 20px 16px",
};
const infoText: React.CSSProperties = {
  fontSize: 13, color: "var(--ha-secondary-text)", textAlign: "center",
  padding: "12px 0",
};
const controlsRow: React.CSSProperties = {
  display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 10,
  alignItems: "center",
};
const filterRow: React.CSSProperties = {
  display: "flex", gap: 2, padding: 2,
  background: "var(--ha-subtle-bg)", borderRadius: 8,
};
const filterBtn: React.CSSProperties = {
  padding: "5px 12px", fontSize: 11, fontWeight: 500,
  background: "transparent", color: "var(--ha-primary-text)",
  border: "none", borderRadius: 6, cursor: "pointer",
};
const filterBtnActive: React.CSSProperties = {
  ...filterBtn,
  background: "var(--ha-card-bg, #fff)",
  boxShadow: "0 1px 3px rgba(0,0,0,0.12)",
  fontWeight: 600,
};
const searchInput: React.CSSProperties = {
  flex: 1, minWidth: 150, padding: "6px 10px",
  fontSize: 12, border: "1px solid var(--ha-divider)",
  borderRadius: 6, background: "var(--ha-input-bg, #fff)",
  color: "var(--ha-primary-text)",
};
const batchBar: React.CSSProperties = {
  display: "flex", alignItems: "center", justifyContent: "space-between",
  gap: 8, marginBottom: 6,
};
const selectAllLabel: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 6,
  fontSize: 12, color: "var(--ha-primary-text)", cursor: "pointer",
};
const batchPrintBtn: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 6,
  padding: "6px 14px",
  background: "var(--ha-primary-color, #1976d2)", color: "#fff",
  border: "none", borderRadius: 6,
  fontSize: 12, fontWeight: 600, cursor: "pointer",
};
const rowCheckbox: React.CSSProperties = {
  width: 14, height: 14, cursor: "pointer", flexShrink: 0,
};
const listWrap: React.CSSProperties = {
  display: "flex", flexDirection: "column", gap: 2,
  border: "1px solid var(--ha-divider)", borderRadius: 8,
  padding: 4, maxHeight: 400, overflowY: "auto",
};
const spoolRow: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 8,
  padding: "6px 8px", borderRadius: 6, fontSize: 12,
};
const uidText: React.CSSProperties = {
  fontFamily: "monospace", fontSize: 11, fontWeight: 600,
  color: "var(--ha-primary-text)", minWidth: 88,
};
const brandText: React.CSSProperties = {
  fontSize: 12, fontWeight: 500, color: "var(--ha-primary-text)",
  minWidth: 100, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
};
const colorText: React.CSSProperties = {
  fontSize: 11, color: "var(--ha-secondary-text)",
  minWidth: 60, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
};
const statusBadgeSt: React.CSSProperties = {
  fontSize: 9, fontWeight: 600, padding: "2px 6px",
  borderRadius: 4, textTransform: "uppercase", letterSpacing: "0.03em",
  whiteSpace: "nowrap",
};
const agoText: React.CSSProperties = {
  fontSize: 10, color: "var(--ha-secondary-text)",
  minWidth: 50, textAlign: "right",
};
const actions: React.CSSProperties = {
  marginLeft: "auto", display: "flex", gap: 3, flexShrink: 0,
};
const iconBtn: React.CSSProperties = {
  width: 22, height: 22, display: "flex", alignItems: "center", justifyContent: "center",
  background: "var(--ha-subtle-bg)", border: "none", borderRadius: 4,
  cursor: "pointer", fontSize: 11,
};
const dangerBtn: React.CSSProperties = {
  ...iconBtn,
  background: "rgba(244,67,54,0.08)", color: "var(--ha-error, #c62828)",
};
