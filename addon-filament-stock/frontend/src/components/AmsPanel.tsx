import { useCallback, useEffect, useState } from "react";
import { AmsTray, AmsTraysResponse, fetchAmsTrays } from "../api";
import { SpoolIcon } from "./SpoolIcon";

const POLL_MS = 15000; // 15s -- same cadence as a typical HA sensor refresh

interface Props {
  /** Called when the user clicks the "in stock" pill so the parent can scroll
   *  to / highlight the matching filament card. Optional. */
  onJumpToFilament?: (filamentDbId: number) => void;
}

export default function AmsPanel({ onJumpToFilament }: Props) {
  const [data, setData] = useState<AmsTraysResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastFetched, setLastFetched] = useState<Date | null>(null);

  const load = useCallback(async (initial: boolean) => {
    if (initial) setLoading(true);
    else setRefreshing(true);
    try {
      const resp = await fetchAmsTrays();
      setData(resp);
      setLastFetched(new Date());
    } catch (exc) {
      setData({
        available: false,
        error: `Could not reach the add-on backend: ${(exc as Error).message}`,
        trays: [],
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    void load(true);
    const id = setInterval(() => void load(false), POLL_MS);
    return () => clearInterval(id);
  }, [load]);

  if (loading) {
    return (
      <section className="ha-card" style={wrap}>
        <Header onRefresh={() => void load(false)} refreshing={refreshing} lastFetched={lastFetched} />
        <p style={emptyText}>Loading AMS state…</p>
      </section>
    );
  }

  if (!data || !data.available) {
    return (
      <section className="ha-card" style={wrap}>
        <Header onRefresh={() => void load(false)} refreshing={refreshing} lastFetched={lastFetched} />
        <div style={errorBox}>
          <strong>AMS view unavailable.</strong>
          <p style={{ marginTop: 6, fontSize: 12 }}>
            {data?.error ?? "Unknown error."}
          </p>
          <p style={{ marginTop: 6, fontSize: 12, color: "var(--ha-secondary-text)" }}>
            The add-on needs <code>homeassistant_api: true</code> in its
            config. After the 0.5.0 update it should be set automatically —
            restart the add-on once if you still see this.
          </p>
        </div>
      </section>
    );
  }

  if (data.trays.length === 0) {
    return (
      <section className="ha-card" style={wrap}>
        <Header onRefresh={() => void load(false)} refreshing={refreshing} lastFetched={lastFetched} />
        <div style={emptyBox}>
          <strong>No AMS trays found.</strong>
          <p style={{ marginTop: 6, fontSize: 12 }}>
            Install the{" "}
            <a
              href="https://github.com/greghesp/ha-bambulab"
              target="_blank"
              rel="noopener"
              style={{ color: "var(--ha-primary-color)" }}
            >
              ha-bambulab
            </a>{" "}
            HACS integration and add your printer. The per-tray sensors
            (e.g. <code>sensor.h2s_…_ams_1_tray_4</code>) will then show up
            here.
          </p>
          {data.error && (
            <p style={{ marginTop: 6, fontSize: 11, color: "var(--ha-secondary-text)" }}>
              {data.error}
            </p>
          )}
        </div>
      </section>
    );
  }

  // Group by (printer, ams_idx) so multi-AMS setups render naturally.
  const groups = groupTrays(data.trays);

  return (
    <section className="ha-card" style={wrap}>
      <Header onRefresh={() => void load(false)} refreshing={refreshing} lastFetched={lastFetched} />
      <div style={groupsWrap}>
        {groups.map((g) => (
          <div key={g.key} style={groupBlock}>
            <div style={groupHeader}>
              <span style={groupTitle}>{g.title}</span>
              <span style={groupCount}>
                {g.trays.filter((t) => t.loaded).length}/{g.trays.length} loaded
              </span>
            </div>
            <div style={trayGrid}>
              {g.trays.map((t) => (
                <TrayCard key={t.entity_id} tray={t} onJumpToFilament={onJumpToFilament} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

// ── Sub-components ──────────────────────────────────────────────────────────

function Header({
  onRefresh,
  refreshing,
  lastFetched,
}: {
  onRefresh: () => void;
  refreshing: boolean;
  lastFetched: Date | null;
}) {
  return (
    <div style={headerRow}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: "var(--ha-primary-color)" }}>
          <rect x="3" y="8" width="18" height="12" rx="2" />
          <path d="M7 8V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v3" />
          <line x1="7" y1="14" x2="7" y2="14.01" />
          <line x1="12" y1="14" x2="12" y2="14.01" />
          <line x1="17" y1="14" x2="17" y2="14.01" />
        </svg>
        <h3 style={panelTitle}>AMS Status</h3>
        {lastFetched && (
          <span style={updatedHint} title={lastFetched.toISOString()}>
            updated {lastFetched.toLocaleTimeString()}
          </span>
        )}
      </div>
      <button type="button" onClick={onRefresh} disabled={refreshing} style={refreshBtn}>
        {refreshing ? "Refreshing…" : "Refresh"}
      </button>
    </div>
  );
}

function TrayCard({
  tray,
  onJumpToFilament,
}: {
  tray: AmsTray;
  onJumpToFilament?: (filamentDbId: number) => void;
}) {
  const swatch = tray.loaded ? tray.color_hex ?? "#9e9e9e" : "#cfd8dc";

  return (
    <div style={trayCard(tray.loaded)}>
      <div style={trayHeaderRow}>
        <span style={trayLocationLabel}>{tray.location_label}</span>
        {tray.remain_pct !== null && tray.loaded && (
          <span style={remainPill(tray.remain_pct)}>{tray.remain_pct}%</span>
        )}
      </div>

      <div style={trayBodyRow}>
        <SpoolIcon colorHex={swatch} size={36} muted={!tray.loaded} />
        <div style={{ minWidth: 0, flex: 1 }}>
          {tray.loaded ? (
            <>
              <div style={trayName} title={tray.name ?? ""}>
                {tray.name ?? tray.raw_state ?? "Loaded"}
              </div>
              <div style={trayMeta}>
                {tray.material ?? "—"}
                {tray.color_hex && (
                  <>
                    {" · "}
                    <span style={{ fontFamily: "monospace" }}>{tray.color_hex}</span>
                  </>
                )}
              </div>
            </>
          ) : (
            <>
              <div style={{ ...trayName, color: "var(--ha-disabled-text)" }}>Empty</div>
              <div style={trayMeta}>No filament loaded</div>
            </>
          )}
        </div>
      </div>

      {tray.loaded && <StockBadge tray={tray} onJumpToFilament={onJumpToFilament} />}
    </div>
  );
}

function StockBadge({
  tray,
  onJumpToFilament,
}: {
  tray: AmsTray;
  onJumpToFilament?: (filamentDbId: number) => void;
}) {
  const stock = tray.stock;
  if (!stock.matched) {
    if (stock.reason === "no_filament_id") {
      return (
        <div style={{ ...stockBadge, ...stockBadgeWarn }}>
          ⚠ Bambu integration didn't expose a filament_id for this tray
        </div>
      );
    }
    return (
      <div style={{ ...stockBadge, ...stockBadgeWarn }}>
        ⚠ Not tracked in stock
        {stock.filament_id && (
          <span style={{ marginLeft: 4, fontFamily: "monospace", opacity: 0.7 }}>
            ({stock.filament_id})
          </span>
        )}
      </div>
    );
  }

  if (!stock.color_matched) {
    return (
      <div
        style={{ ...stockBadge, ...stockBadgeInfo, cursor: onJumpToFilament ? "pointer" : "default" }}
        onClick={() => onJumpToFilament?.(stock.filament_db_id)}
        title="Filament is in stock but this exact color isn't"
      >
        ◐ {stock.brand} {stock.material} — color not in stock
      </div>
    );
  }

  const total = stock.available_total ?? 0;
  const sp = stock.available_spool ?? 0;
  const rf = stock.available_refill ?? 0;
  const ok = total > 0;
  return (
    <div
      style={{
        ...stockBadge,
        ...(ok ? stockBadgeOk : stockBadgeError),
        cursor: onJumpToFilament ? "pointer" : "default",
      }}
      onClick={() => onJumpToFilament?.(stock.filament_db_id)}
      title={`Click to jump to ${stock.brand} ${stock.material}`}
    >
      {ok ? "✓" : "✗"} {stock.color_name} in stock:{" "}
      <strong>
        {sp} spool{sp === 1 ? "" : "s"} · {rf} refill{rf === 1 ? "" : "s"}
      </strong>
    </div>
  );
}

// ── Grouping helper ─────────────────────────────────────────────────────────

interface TrayGroup {
  key: string;
  title: string;
  trays: AmsTray[];
}

function groupTrays(trays: AmsTray[]): TrayGroup[] {
  const map = new Map<string, TrayGroup>();
  for (const t of trays) {
    const key =
      t.kind === "external"
        ? `${t.printer}__ext`
        : `${t.printer}__ams_${t.ams_idx ?? "?"}`;
    const title =
      t.kind === "external"
        ? `${t.printer} · External spool`
        : `${t.printer} · AMS ${t.ams_idx}`;
    if (!map.has(key)) map.set(key, { key, title, trays: [] });
    map.get(key)!.trays.push(t);
  }
  return Array.from(map.values()).map((g) => ({
    ...g,
    trays: [...g.trays].sort((a, b) => a.tray_idx - b.tray_idx),
  }));
}

// ── Styles ──────────────────────────────────────────────────────────────────

const wrap: React.CSSProperties = {
  padding: "14px 18px",
  marginBottom: 16,
};
const headerRow: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  marginBottom: 10,
  gap: 12,
};
const panelTitle: React.CSSProperties = {
  fontSize: 14,
  fontWeight: 600,
  color: "var(--ha-primary-text)",
  letterSpacing: "0.02em",
  textTransform: "uppercase",
};
const updatedHint: React.CSSProperties = {
  fontSize: 11,
  color: "var(--ha-secondary-text)",
};
const refreshBtn: React.CSSProperties = {
  padding: "5px 12px",
  fontSize: 12,
  fontWeight: 500,
  background: "rgba(0,0,0,0.04)",
  color: "var(--ha-primary-text)",
  border: "1px solid var(--ha-divider)",
  borderRadius: 6,
  cursor: "pointer",
};
const groupsWrap: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 14,
};
const groupBlock: React.CSSProperties = {};
const groupHeader: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  marginBottom: 6,
};
const groupTitle: React.CSSProperties = {
  fontSize: 11,
  fontWeight: 600,
  textTransform: "uppercase",
  letterSpacing: "0.06em",
  color: "var(--ha-secondary-text)",
};
const groupCount: React.CSSProperties = {
  fontSize: 11,
  color: "var(--ha-secondary-text)",
};
const trayGrid: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
  gap: 8,
};
const trayCard = (loaded: boolean): React.CSSProperties => ({
  padding: "10px 12px",
  borderRadius: 10,
  border: "1px solid var(--ha-divider)",
  background: loaded ? "rgba(76,175,80,0.04)" : "rgba(0,0,0,0.02)",
  display: "flex",
  flexDirection: "column",
  gap: 6,
});
const trayHeaderRow: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: 6,
};
const trayLocationLabel: React.CSSProperties = {
  fontSize: 10,
  fontWeight: 600,
  textTransform: "uppercase",
  letterSpacing: "0.06em",
  color: "var(--ha-secondary-text)",
};
const remainPill = (pct: number): React.CSSProperties => ({
  fontSize: 10,
  fontWeight: 700,
  padding: "1px 7px",
  borderRadius: 9,
  background:
    pct >= 50
      ? "rgba(76,175,80,0.18)"
      : pct >= 20
      ? "rgba(255,152,0,0.18)"
      : "rgba(244,67,54,0.18)",
  color:
    pct >= 50
      ? "#2e7d32"
      : pct >= 20
      ? "#e65100"
      : "var(--ha-error)",
});
const trayBodyRow: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 10,
};
const trayName: React.CSSProperties = {
  fontSize: 13,
  fontWeight: 600,
  color: "var(--ha-primary-text)",
  whiteSpace: "nowrap",
  overflow: "hidden",
  textOverflow: "ellipsis",
};
const trayMeta: React.CSSProperties = {
  fontSize: 11,
  color: "var(--ha-secondary-text)",
  marginTop: 1,
};
const stockBadge: React.CSSProperties = {
  fontSize: 11,
  fontWeight: 600,
  padding: "4px 8px",
  borderRadius: 6,
  border: "1px solid transparent",
};
const stockBadgeOk: React.CSSProperties = {
  background: "rgba(76,175,80,0.12)",
  color: "#2e7d32",
  borderColor: "rgba(76,175,80,0.35)",
};
const stockBadgeError: React.CSSProperties = {
  background: "rgba(244,67,54,0.12)",
  color: "var(--ha-error)",
  borderColor: "rgba(244,67,54,0.35)",
};
const stockBadgeWarn: React.CSSProperties = {
  background: "rgba(255,152,0,0.12)",
  color: "#bf360c",
  borderColor: "rgba(255,152,0,0.35)",
};
const stockBadgeInfo: React.CSSProperties = {
  background: "rgba(3,169,244,0.12)",
  color: "#0277bd",
  borderColor: "rgba(3,169,244,0.35)",
};
const emptyBox: React.CSSProperties = {
  padding: "12px 14px",
  borderRadius: 8,
  background: "rgba(0,0,0,0.03)",
  fontSize: 13,
  color: "var(--ha-primary-text)",
};
const errorBox: React.CSSProperties = {
  padding: "12px 14px",
  borderRadius: 8,
  background: "var(--ha-error-bg)",
  color: "var(--ha-error)",
  fontSize: 13,
};
const emptyText: React.CSSProperties = {
  fontSize: 12,
  color: "var(--ha-secondary-text)",
  padding: "8px 0",
};
