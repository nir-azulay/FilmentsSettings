import { useCallback, useEffect, useState } from "react";
import { Alert, Filament, fetchAlerts, fetchFilaments, importProfiles } from "./api";
import AlertBanner from "./components/AlertBanner";
import Dashboard from "./components/Dashboard";

export default function App() {
  const [filaments, setFilaments] = useState<Filament[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  const reload = useCallback(async () => {
    const [f, a] = await Promise.all([fetchFilaments(), fetchAlerts()]);
    setFilaments(f);
    setAlerts(a);
  }, []);

  useEffect(() => {
    reload().finally(() => setLoading(false));
  }, [reload]);

  const handleImport = async () => {
    const result = await importProfiles();
    alert(`Imported: ${result.imported}, Skipped: ${result.skipped}`);
    await reload();
  };

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
        <p style={{ fontSize: "1.2rem", opacity: 0.7 }}>Loading...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem", maxWidth: "1400px", margin: "0 auto" }}>
      <header style={{ marginBottom: "2rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ fontSize: "1.8rem", fontWeight: 700 }}>Filaments Stock Management</h1>
          <p style={{ opacity: 0.6, marginTop: "0.25rem" }}>
            {filaments.length} filaments tracked
          </p>
        </div>
        <button onClick={handleImport} style={importBtnStyle}>
          Import from Profiles
        </button>
      </header>

      {alerts.length > 0 && <AlertBanner alerts={alerts} />}

      <Dashboard filaments={filaments} onUpdate={reload} />
    </div>
  );
}

const importBtnStyle: React.CSSProperties = {
  padding: "0.6rem 1.2rem",
  background: "#3b82f6",
  color: "#fff",
  border: "none",
  borderRadius: "8px",
  fontSize: "0.9rem",
  fontWeight: 500,
  cursor: "pointer",
};
