import { useCallback, useEffect, useState } from "react";
import {
  Alert,
  Filament,
  StapleAlertIgnore,
  deleteAlertIgnore,
  fetchAlertIgnores,
  fetchAlerts,
  fetchFilaments,
  ignoreStapleAlert,
  importProfiles,
} from "./api";
import AlertBanner from "./components/AlertBanner";
import Dashboard from "./components/Dashboard";
import { SpoolIcon } from "./components/SpoolIcon";
import { totalAvailableSpools, totalOnOrderSpools } from "./stockUtils";

export default function App() {
  const [filaments, setFilaments] = useState<Filament[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [alertIgnores, setAlertIgnores] = useState<StapleAlertIgnore[]>([]);
  const [loading, setLoading] = useState(true);
  const [importing, setImporting] = useState(false);
  const [importMsg, setImportMsg] = useState<{ text: string; ok: boolean } | null>(null);

  const reload = useCallback(async () => {
    const [f, a, ign] = await Promise.all([fetchFilaments(), fetchAlerts(), fetchAlertIgnores()]);
    setFilaments(f);
    setAlerts(a);
    setAlertIgnores(ign);
  }, []);

  useEffect(() => {
    reload().finally(() => setLoading(false));
  }, [reload]);

  const handleImport = async () => {
    setImporting(true);
    setImportMsg(null);
    try {
      const result = await importProfiles();
      setImportMsg({ text: `Imported ${result.imported} · Skipped ${result.skipped}`, ok: true });
      await reload();
      setTimeout(() => setImportMsg(null), 4000);
    } catch {
      setImportMsg({ text: "Import failed", ok: false });
    } finally {
      setImporting(false);
    }
  };

  const totalInStock  = totalAvailableSpools(filaments);
  const totalOrdered  = totalOnOrderSpools(filaments);
  const brandsSet     = new Set(filaments.map((f) => f.brand));

  if (loading) {
    return (
      <div style={loaderWrap}>
        <div style={loaderRing} />
        <p style={{ color: "var(--ha-secondary-text)", marginTop: 12, fontSize: 13 }}>
          Loading…
        </p>
      </div>
    );
  }


  return (
    <div className="ha-app-shell">
      {/* ── HA top toolbar ── */}
      <header className="ha-toolbar">
        {/* HA hamburger / logo zone */}
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="var(--ha-primary-color)">
            <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" />
          </svg>
          <span style={toolbarTitle}>Filament Stock</span>
        </div>

        {/* Right side */}
        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 10 }}>
          {importMsg && (
            <span style={{
              fontSize: 12,
              padding: "3px 10px",
              borderRadius: 12,
              background: importMsg.ok ? "var(--ha-success-bg)" : "var(--ha-error-bg)",
              color: importMsg.ok ? "var(--ha-success)" : "var(--ha-error)",
              animation: "fadeIn 0.2s ease-out",
            }}>
              {importMsg.text}
            </span>
          )}
          <button onClick={handleImport} disabled={importing} style={syncBtn}>
            {importing ? (
              <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <div style={btnSpinner} /> Syncing…
              </span>
            ) : (
              <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="1 4 1 10 7 10" />
                  <path d="M3.51 15a9 9 0 1 0 .49-5.1L1 10" />
                </svg>
                Sync Profiles
              </span>
            )}
          </button>
        </div>
      </header>

      <main style={mainWrap}>
        {/* ── Summary row — HA glance-card style ── */}
        <div style={summaryRow}>
          <SummaryCard value={filaments.length} label="Filaments"       color="var(--ha-primary-color)" />
          <SummaryCard value={totalInStock}     label="Spools Available" color="var(--ha-success)"   spoolColor="#43a047" />
          <SummaryCard value={totalOrdered}     label="On Order"        color="var(--ha-warning)"   spoolColor="#ff9800" />
          <SummaryCard value={brandsSet.size}   label="Brands"          color="#7a7a7a"              />
        </div>

        {(alerts.length > 0 || alertIgnores.length > 0) && (
          <AlertBanner
            alerts={alerts}
            ignores={alertIgnores}
            onIgnore={async (filamentType, colorName) => {
              await ignoreStapleAlert(filamentType, colorName);
              await reload();
            }}
            onUnignore={async (id) => {
              await deleteAlertIgnore(id);
              await reload();
            }}
          />
        )}

        <Dashboard filaments={filaments} alertIgnores={alertIgnores} onUpdate={reload} />
      </main>
    </div>
  );
}

function SummaryCard({
  value,
  label,
  color,
  icon,
  spoolColor,
}: {
  value: number;
  label: string;
  color: string;
  icon?: string;
  spoolColor?: string;
}) {
  return (
    <div className="ha-card" style={summaryCardStyle}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        {spoolColor ? (
          <SpoolIcon colorHex={spoolColor} size={32} count={value > 1 ? value : undefined} />
        ) : icon ? (
          <span style={{ fontSize: 13 }}>{icon}</span>
        ) : null}
        <p style={{ fontSize: 28, fontWeight: 600, color, lineHeight: 1, letterSpacing: "-0.01em" }}>{value}</p>
      </div>
      <p style={{ fontSize: 11, color: "var(--ha-secondary-text)", marginTop: 4, textTransform: "uppercase", letterSpacing: "0.06em" }}>{label}</p>
    </div>
  );
}

/* ─── Styles ─────────────────────────────────────────────────────────────── */
const loaderWrap: React.CSSProperties = {
  display: "flex", flexDirection: "column", alignItems: "center",
  justifyContent: "center", height: "100vh",
};
const loaderRing: React.CSSProperties = {
  width: 32, height: 32,
  border: "3px solid rgba(3,169,244,0.2)",
  borderTopColor: "var(--ha-primary-color)",
  borderRadius: "50%",
  animation: "spin 0.9s linear infinite",
};
const toolbarTitle: React.CSSProperties = {
  fontSize: 18, fontWeight: 400, color: "var(--ha-primary-text)", letterSpacing: 0,
};
const syncBtn: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 6,
  padding: "8px 16px",
  background: "var(--ha-primary-color)",
  color: "#fff",
  border: "none",
  borderRadius: "var(--ha-btn-radius)",
  fontSize: 13, fontWeight: 500,
  cursor: "pointer",
  letterSpacing: "0.01em",
};
const btnSpinner: React.CSSProperties = {
  width: 12, height: 12,
  border: "2px solid rgba(255,255,255,0.3)",
  borderTopColor: "#fff",
  borderRadius: "50%",
  animation: "spin 0.8s linear infinite",
};
const mainWrap: React.CSSProperties = {
  padding: "16px",
  maxWidth: 1440,
  width: "100%",
  margin: "0 auto",
  flex: 1,
};
const summaryRow: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(4, 1fr)",
  gap: 12,
  marginBottom: 16,
};
const summaryCardStyle: React.CSSProperties = {
  padding: "16px 20px",
  display: "flex",
  flexDirection: "column",
};
