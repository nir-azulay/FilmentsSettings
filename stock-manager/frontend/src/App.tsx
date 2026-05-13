import { useCallback, useEffect, useState } from "react";
import { Alert, Filament, fetchAlerts, fetchFilaments, importProfiles } from "./api";
import AlertBanner from "./components/AlertBanner";
import Dashboard from "./components/Dashboard";

export default function App() {
  const [filaments, setFilaments] = useState<Filament[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [importing, setImporting] = useState(false);
  const [importMsg, setImportMsg] = useState<{ text: string; ok: boolean } | null>(null);

  const reload = useCallback(async () => {
    const [f, a] = await Promise.all([fetchFilaments(), fetchAlerts()]);
    setFilaments(f);
    setAlerts(a);
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

  const totalInStock  = filaments.reduce((sum, f) => sum + f.colors.filter(c => c.status === "in_stock").reduce((s, c) => s + (c.quantity - (c.quantity_used ?? 0)), 0), 0);
  const totalOrdered  = filaments.reduce((sum, f) => sum + f.colors.filter(c => c.status === "ordered").reduce((s, c) => s + c.quantity, 0), 0);
  const brandsSet     = new Set(filaments.map((f) => f.brand));
  const typesSet      = new Set(filaments.map((f) => f.material));

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
          <svg width="24" height="24" viewBox="0 0 24 24" fill="rgba(255,255,255,0.9)">
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
          <SummaryCard value={typesSet.size}    label="Filament Types" color="var(--ha-primary-color)" />
          <SummaryCard value={totalInStock}     label="Total Spools" color="var(--ha-success)"       icon="✓" />
          <SummaryCard value={totalOrdered}     label="Ordered"      color="var(--ha-primary-color)" icon="⏳" />
          <SummaryCard value={brandsSet.size}   label="Brands"     color="#9c27b0"                 />
        </div>

        {alerts.length > 0 && <AlertBanner alerts={alerts} />}

        <Dashboard filaments={filaments} onUpdate={reload} />
      </main>
    </div>
  );
}

function SummaryCard({ value, label, color, icon }: { value: number; label: string; color: string; icon?: string }) {
  return (
    <div className="ha-card" style={summaryCardStyle}>
      <div style={{ display: "flex", alignItems: "baseline", gap: 5 }}>
        {icon && <span style={{ fontSize: 13 }}>{icon}</span>}
        <p style={{ fontSize: 28, fontWeight: 400, color, lineHeight: 1, letterSpacing: "-0.01em" }}>{value}</p>
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
  fontSize: 18, fontWeight: 400, color: "#ffffff", letterSpacing: 0,
};
const syncBtn: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 6,
  padding: "8px 16px",
  background: "rgba(255,255,255,0.15)",
  color: "#fff",
  border: "1px solid rgba(255,255,255,0.3)",
  borderRadius: "var(--ha-btn-radius)",
  fontSize: 13, fontWeight: 500,
  cursor: "pointer",
  letterSpacing: "0.01em",
  backdropFilter: "blur(4px)",
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
