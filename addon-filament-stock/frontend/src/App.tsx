import { useCallback, useEffect, useState } from "react";
import {
  AddonConfig,
  Alert,
  DEFAULT_ADDON_CONFIG,
  Filament,
  StapleAlertIgnore,
  fetchAddonConfig,
  fetchAlertIgnores,
  fetchAlerts,
  fetchFilaments,
  ignoreStapleAlert,
  importProfiles,
} from "./api";
import AlertBanner from "./components/AlertBanner";
import AmsPanel from "./components/AmsPanel";
import CreateFilamentDialog from "./components/CreateFilamentDialog";
import Dashboard from "./components/Dashboard";
import EmptyState from "./components/EmptyState";
import QrScannerDialog from "./components/QrScannerDialog";
import ScanAssignDialog from "./components/ScanAssignDialog";
import SetupChecklist from "./components/SetupChecklist";
import BrandLogo, { uniqueBrandsFromFilaments } from "./components/BrandLogo";
import { SpoolIcon } from "./components/SpoolIcon";
import { totalAvailableSpools, totalOnOrderSpools } from "./stockUtils";

function jumpToFilament(filamentDbId: number) {
  const el = document.getElementById(`filament-${filamentDbId}`);
  if (!el) return;
  el.scrollIntoView({ behavior: "smooth", block: "center" });
  // Brief highlight so the user spots which card the AMS pointed to.
  el.style.transition = "box-shadow 0.4s ease-out";
  el.style.boxShadow = "0 0 0 3px var(--ha-primary-color)";
  setTimeout(() => {
    el.style.boxShadow = "";
  }, 1500);
}

export default function App() {
  const [filaments, setFilaments] = useState<Filament[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [alertIgnores, setAlertIgnores] = useState<StapleAlertIgnore[]>([]);
  const [loading, setLoading] = useState(true);
  const [importing, setImporting] = useState(false);
  const [importMsg, setImportMsg] = useState<{ text: string; ok: boolean } | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  // Add-on config -- only used here to decide whether to mount the AMS
  // panel. Starts at the compiled-in fallback so the first paint isn't
  // delayed by /api/config; the real value lands as soon as the fetch
  // resolves. Individual child components (e.g. AmsPanel, AssignTrayDialog)
  // fetch the config separately for fields they care about.
  const [addonConfig, setAddonConfig] = useState<AddonConfig>(DEFAULT_ADDON_CONFIG);
  const [scanTarget, setScanTarget] = useState<string | null>(null);
  const [showScanner, setShowScanner] = useState(false);

  // Hash-based deep linking: #spool/SP-XXXXXXXX opens the scan-assign dialog
  useEffect(() => {
    const checkHash = () => {
      const hash = window.location.hash;
      const match = hash.match(/^#spool\/(SP-[A-F0-9]{8})$/i);
      if (match) {
        setScanTarget(match[1]);
        window.location.hash = "";
      }
    };
    checkHash();
    window.addEventListener("hashchange", checkHash);
    return () => window.removeEventListener("hashchange", checkHash);
  }, []);

  const reload = useCallback(async () => {
    const [f, a, ign] = await Promise.all([fetchFilaments(), fetchAlerts(), fetchAlertIgnores()]);
    setFilaments(f);
    setAlerts(a);
    setAlertIgnores(ign);
  }, []);

  useEffect(() => {
    reload().finally(() => setLoading(false));
  }, [reload]);

  useEffect(() => {
    let cancelled = false;
    void fetchAddonConfig().then((c) => {
      if (!cancelled) setAddonConfig(c);
    });
    return () => {
      cancelled = true;
    };
  }, []);

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
  const uniqueBrands = uniqueBrandsFromFilaments(filaments);

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
          <span style={{ fontSize: 10, color: "var(--ha-secondary-text)", opacity: 0.6 }}>v{addonConfig.addon_version}</span>
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
          <button onClick={() => setShowScanner(true)} style={scanBtn} title="Scan spool QR code">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 7V5a2 2 0 0 1 2-2h2" /><path d="M17 3h2a2 2 0 0 1 2 2v2" />
              <path d="M21 17v2a2 2 0 0 1-2 2h-2" /><path d="M7 21H5a2 2 0 0 1-2-2v-2" />
              <rect x="7" y="7" width="10" height="10" rx="1" />
            </svg>
            Scan
          </button>
          <button onClick={() => setShowCreateDialog(true)} style={addFilamentBtn}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            Add Filament
          </button>
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

      <main className="ha-main" style={mainWrap}>
        {/* ── Summary row — HA glance-card style ── */}
        <div className="ha-summary-row" style={summaryRow}>
          <SummaryCard value={filaments.length} label="Filaments"       color="var(--ha-primary-color)" />
          <SummaryCard value={totalInStock}     label="Spools Available" color="var(--ha-success)"   spoolColor="#43a047" />
          <SummaryCard value={totalOrdered}     label="On Order"        color="var(--ha-warning)"   spoolColor="#ff9800" />
          <BrandsSummaryCard brands={uniqueBrands} />
        </div>

        <SetupChecklist />

        <AlertBanner
          alerts={alerts}
          onIgnore={async (filamentType, colorName) => {
            await ignoreStapleAlert(filamentType, colorName);
            await reload();
          }}
        />

        {/* AMS panel is hidden when the user has opted out of the
            Bambu integration in the add-on Configuration tab. We avoid
            mounting the component at all so it never fires its
            /api/ams/trays poll. */}
        {!addonConfig.disable_bambu_integration && (
          <AmsPanel onJumpToFilament={jumpToFilament} onStockChanged={() => void reload()} />
        )}

        {filaments.length === 0 ? (
          <EmptyState
            onAddFilament={() => setShowCreateDialog(true)}
            onSeeded={() => void reload()}
          />
        ) : (
          <Dashboard filaments={filaments} alertIgnores={alertIgnores} onUpdate={reload} />
        )}
      </main>

      {showCreateDialog && (
        <CreateFilamentDialog
          onClose={() => setShowCreateDialog(false)}
          onCreated={reload}
        />
      )}

      {showScanner && (
        <QrScannerDialog
          onScanned={(uid) => {
            setShowScanner(false);
            setScanTarget(uid);
          }}
          onClose={() => setShowScanner(false)}
        />
      )}

      {scanTarget && (
        <ScanAssignDialog
          uid={scanTarget}
          onClose={() => setScanTarget(null)}
          onAssigned={() => void reload()}
        />
      )}
    </div>
  );
}

function BrandsSummaryCard({ brands }: { brands: { brand: string; logoUrl: string }[] }) {
  return (
    <div className="ha-card" style={summaryCardStyle}>
      <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap", minHeight: 36 }}>
        {brands.map((b) => (
          <BrandLogo key={b.brand} brand={b.brand} url={b.logoUrl} size={30} />
        ))}
      </div>
      <p style={{ fontSize: 11, color: "var(--ha-secondary-text)", marginTop: 6, textTransform: "uppercase", letterSpacing: "0.06em" }}>
        Brands · {brands.length}
      </p>
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
const scanBtn: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 5,
  padding: "7px 14px",
  background: "var(--ha-primary-color)",
  color: "#fff",
  border: "none",
  borderRadius: "var(--ha-btn-radius)",
  fontSize: 13, fontWeight: 600,
  cursor: "pointer",
};
const addFilamentBtn: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 6,
  padding: "8px 16px",
  background: "none",
  color: "var(--ha-primary-color)",
  border: "1px solid var(--ha-primary-color)",
  borderRadius: "var(--ha-btn-radius)",
  fontSize: 13, fontWeight: 500,
  cursor: "pointer",
  letterSpacing: "0.01em",
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
  width: "100%",
  margin: "0 auto",
  flex: 1,
};
const summaryRow: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
  gap: 12,
  marginBottom: 16,
};
const summaryCardStyle: React.CSSProperties = {
  padding: "16px 20px",
  display: "flex",
  flexDirection: "column",
};
