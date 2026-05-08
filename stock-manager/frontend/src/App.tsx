import { useCallback, useEffect, useState } from "react";
import { Alert, Filament, fetchAlerts, fetchFilaments, importProfiles } from "./api";
import AlertBanner from "./components/AlertBanner";
import Dashboard from "./components/Dashboard";

export default function App() {
  const [filaments, setFilaments] = useState<Filament[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [importing, setImporting] = useState(false);

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
    try {
      const result = await importProfiles();
      alert(`Imported: ${result.imported}, Skipped: ${result.skipped}`);
      await reload();
    } finally {
      setImporting(false);
    }
  };

  const totalSpools = filaments.reduce((sum, f) => sum + f.current_stock, 0);
  const totalColors = filaments.reduce((sum, f) => sum + f.colors.length, 0);
  const brandsSet = new Set(filaments.map((f) => f.brand));

  if (loading) {
    return (
      <div style={loaderWrap}>
        <div style={loaderSpinner} />
        <p style={{ color: "var(--text-muted)", marginTop: "1rem" }}>Loading filaments...</p>
      </div>
    );
  }

  return (
    <div style={appContainer}>
      {/* Header */}
      <header style={headerStyle}>
        <div style={headerLeft}>
          <div style={logoWrap}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <circle cx="12" cy="12" r="3" />
              <path d="M12 2v4M12 18v4M2 12h4M18 12h4" />
            </svg>
          </div>
          <div>
            <h1 style={titleStyle}>Filament Stock</h1>
            <p style={subtitleStyle}>Manage your 3D printing inventory</p>
          </div>
        </div>
        <button
          onClick={handleImport}
          disabled={importing}
          style={importBtnStyle}
        >
          {importing ? (
            <span style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
              <div style={btnSpinner} /> Importing...
            </span>
          ) : (
            <>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              Import Profiles
            </>
          )}
        </button>
      </header>

      {/* Stats Bar */}
      <div style={statsBar}>
        <StatCard label="Filaments" value={filaments.length} icon="layers" />
        <StatCard label="Total Spools" value={totalSpools} icon="box" />
        <StatCard label="Colors" value={totalColors} icon="palette" />
        <StatCard label="Brands" value={brandsSet.size} icon="tag" />
      </div>

      {/* Alerts */}
      {alerts.length > 0 && <AlertBanner alerts={alerts} />}

      {/* Dashboard */}
      <Dashboard filaments={filaments} onUpdate={reload} />
    </div>
  );
}

function StatCard({ label, value, icon }: { label: string; value: number; icon: string }) {
  const icons: Record<string, JSX.Element> = {
    layers: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polygon points="12 2 2 7 12 12 22 7 12 2" />
        <polyline points="2 17 12 22 22 17" />
        <polyline points="2 12 12 17 22 12" />
      </svg>
    ),
    box: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--success)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
      </svg>
    ),
    palette: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--warning)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="13.5" cy="6.5" r="0.5" fill="var(--warning)" />
        <circle cx="17.5" cy="10.5" r="0.5" fill="var(--warning)" />
        <circle cx="8.5" cy="7.5" r="0.5" fill="var(--warning)" />
        <circle cx="6.5" cy="12.5" r="0.5" fill="var(--warning)" />
        <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z" />
      </svg>
    ),
    tag: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" />
        <line x1="7" y1="7" x2="7.01" y2="7" />
      </svg>
    ),
  };

  return (
    <div style={statCardStyle}>
      <div style={statIconWrap}>{icons[icon]}</div>
      <div>
        <p style={statValue}>{value}</p>
        <p style={statLabel}>{label}</p>
      </div>
    </div>
  );
}

const appContainer: React.CSSProperties = {
  padding: "1.5rem 2rem",
  maxWidth: "1440px",
  margin: "0 auto",
};

const headerStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: "1.5rem",
  paddingBottom: "1.5rem",
  borderBottom: "1px solid var(--border-subtle)",
};

const headerLeft: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: "0.75rem",
};

const logoWrap: React.CSSProperties = {
  width: "44px",
  height: "44px",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  background: "var(--accent-subtle)",
  borderRadius: "var(--radius-md)",
};

const titleStyle: React.CSSProperties = {
  fontSize: "1.4rem",
  fontWeight: 700,
  letterSpacing: "-0.02em",
};

const subtitleStyle: React.CSSProperties = {
  fontSize: "0.82rem",
  color: "var(--text-muted)",
  marginTop: "2px",
};

const importBtnStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: "0.5rem",
  padding: "0.6rem 1.2rem",
  background: "var(--accent)",
  color: "#fff",
  border: "none",
  borderRadius: "var(--radius-md)",
  fontSize: "0.85rem",
  fontWeight: 500,
  cursor: "pointer",
  transition: "var(--transition)",
  boxShadow: "var(--shadow-sm)",
};

const statsBar: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(4, 1fr)",
  gap: "1rem",
  marginBottom: "1.5rem",
};

const statCardStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: "0.75rem",
  padding: "1rem 1.2rem",
  background: "var(--bg-secondary)",
  borderRadius: "var(--radius-lg)",
  border: "1px solid var(--border-subtle)",
};

const statIconWrap: React.CSSProperties = {
  width: "36px",
  height: "36px",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  background: "var(--bg-tertiary)",
  borderRadius: "var(--radius-sm)",
};

const statValue: React.CSSProperties = {
  fontSize: "1.25rem",
  fontWeight: 700,
  lineHeight: 1.2,
};

const statLabel: React.CSSProperties = {
  fontSize: "0.75rem",
  color: "var(--text-muted)",
  textTransform: "uppercase",
  letterSpacing: "0.04em",
};

const loaderWrap: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  alignItems: "center",
  height: "100vh",
};

const loaderSpinner: React.CSSProperties = {
  width: "32px",
  height: "32px",
  border: "3px solid var(--border)",
  borderTopColor: "var(--accent)",
  borderRadius: "50%",
  animation: "spin 0.8s linear infinite",
};

const btnSpinner: React.CSSProperties = {
  width: "14px",
  height: "14px",
  border: "2px solid rgba(255,255,255,0.3)",
  borderTopColor: "#fff",
  borderRadius: "50%",
  animation: "spin 0.8s linear infinite",
};
