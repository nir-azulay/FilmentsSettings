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
  markSpoolEmpty,
  unassignSpool,
} from "../api";
import LabelDialog from "./LabelDialog";
import SpoolTimelineDialog from "./SpoolTimelineDialog";
import { SpoolIcon } from "./SpoolIcon";

interface Props {
  onStockChanged: () => void;
}

const STATUS_BADGE: Record<string, { label: string; bg: string; color: string }> = {
  in_stock: { label: "In Stock", bg: "#e8f5e9", color: "#2e7d32" },
  in_tray: { label: "In Tray", bg: "#e3f2fd", color: "#1565c0" },
  empty: { label: "Empty", bg: "#f3f3f3", color: "#999" },
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
                      <div key={s.uid} style={spoolRow}>
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
const pillGreen: React.CSSProperties = { background: "#e8f5e9", color: "#2e7d32" };
const pillBlue: React.CSSProperties = { background: "#e3f2fd", color: "#1565c0" };
const pillGray: React.CSSProperties = { background: "#f3f3f3", color: "#999" };
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
  background: "rgba(0,0,0,0.04)", borderRadius: 8,
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
  background: "rgba(0,0,0,0.05)", border: "none", borderRadius: 4,
  cursor: "pointer", fontSize: 11,
};
const dangerBtn: React.CSSProperties = {
  ...iconBtn,
  background: "rgba(244,67,54,0.08)", color: "var(--ha-error, #c62828)",
};
