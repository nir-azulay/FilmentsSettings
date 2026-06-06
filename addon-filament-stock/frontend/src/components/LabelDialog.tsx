import { useState } from "react";
import { AddonConfig, SpoolInstance, printSpoolLabel, spoolLabelUrl } from "../api";

interface Props {
  spool: SpoolInstance;
  config: AddonConfig;
  onClose: () => void;
}

export default function LabelDialog({ spool, config, onClose }: Props) {
  const [printing, setPrinting] = useState(false);
  const [printResult, setPrintResult] = useState<{ ok: boolean; msg: string } | null>(null);
  const labelUrl = spoolLabelUrl(spool.uid);
  const printerConfigured = Boolean(config.niimbot_address);

  const handleDownload = () => {
    const a = document.createElement("a");
    a.href = labelUrl;
    a.download = `${spool.uid}.png`;
    a.click();
  };

  const handlePrint = async () => {
    setPrinting(true);
    setPrintResult(null);
    try {
      const res = await printSpoolLabel(spool.uid);
      if (res.ok) {
        setPrintResult({ ok: true, msg: `Printed in ${res.duration ?? "?"}s` });
      } else {
        setPrintResult({ ok: false, msg: res.error || "Print failed" });
      }
    } catch (e: any) {
      setPrintResult({ ok: false, msg: e.message || "Print failed" });
    } finally {
      setPrinting(false);
    }
  };

  return (
    <div style={overlay} onClick={onClose}>
      <div style={dialog} onClick={(e) => e.stopPropagation()}>
        <h3 style={title}>Spool Label</h3>

        <div style={spoolHeader}>
          <div
            style={{
              width: 24, height: 24, borderRadius: 4,
              background: spool.color_hex ?? "#808080",
              border: "1px solid #ccc", flexShrink: 0,
            }}
          />
          <span style={{ fontWeight: 600 }}>{spool.brand} {spool.material}</span>
          <span style={{ color: "var(--ha-secondary-text)", fontSize: 12 }}>
            {spool.color_name} &middot; {spool.uid}
          </span>
        </div>

        {/* Label preview */}
        <div style={previewWrap}>
          <img
            src={labelUrl}
            alt={`Label for ${spool.uid}`}
            style={previewImg}
          />
        </div>

        {/* Print result */}
        {printResult && (
          <div
            style={{
              padding: "6px 10px", borderRadius: 6, fontSize: 13, marginTop: 8,
              background: printResult.ok ? "#e8f5e9" : "#ffebee",
              color: printResult.ok ? "#2e7d32" : "#c62828",
            }}
          >
            {printResult.msg}
          </div>
        )}

        {/* Actions */}
        <div style={footer}>
          <button onClick={onClose} style={cancelBtn}>Close</button>
          <button onClick={handleDownload} style={downloadBtn}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            Download PNG
          </button>
          <button
            onClick={handlePrint}
            disabled={!printerConfigured || printing}
            style={{
              ...printBtn,
              opacity: !printerConfigured || printing ? 0.5 : 1,
            }}
            title={printerConfigured ? "Print to Niimbot" : "Configure niimbot_address in add-on settings first"}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="6 9 6 2 18 2 18 9" />
              <path d="M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2" />
              <rect x="6" y="14" width="12" height="8" />
            </svg>
            {printing ? "Printing..." : "Print"}
          </button>
        </div>

        {!printerConfigured && (
          <p style={{ fontSize: 11, color: "var(--ha-secondary-text)", marginTop: 6, textAlign: "right" }}>
            Set <code>niimbot_address</code> in add-on settings to enable direct printing.
          </p>
        )}
      </div>
    </div>
  );
}

const overlay: React.CSSProperties = {
  position: "fixed", inset: 0, background: "rgba(0,0,0,0.45)",
  display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000,
};
const dialog: React.CSSProperties = {
  background: "var(--ha-card-bg, #fff)", borderRadius: 12, padding: 20,
  width: "min(440px, 90vw)", maxHeight: "85vh", overflowY: "auto",
  boxShadow: "0 8px 32px rgba(0,0,0,0.2)",
};
const title: React.CSSProperties = {
  margin: "0 0 12px", fontSize: 18, fontWeight: 600,
  color: "var(--ha-primary-text)",
};
const spoolHeader: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 8, marginBottom: 12,
  fontSize: 14,
};
const previewWrap: React.CSSProperties = {
  border: "1px solid var(--ha-divider, #e0e0e0)", borderRadius: 8,
  padding: 8, background: "#fafafa", textAlign: "center",
};
const previewImg: React.CSSProperties = {
  maxWidth: "100%", height: "auto", borderRadius: 4,
  imageRendering: "auto",
};
const footer: React.CSSProperties = {
  display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 16,
  borderTop: "1px solid var(--ha-divider)", paddingTop: 12,
};
const cancelBtn: React.CSSProperties = {
  padding: "8px 16px", border: "1px solid var(--ha-divider)",
  borderRadius: 6, background: "transparent", cursor: "pointer",
  fontSize: 13, color: "var(--ha-primary-text)",
};
const downloadBtn: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 6,
  padding: "8px 16px", border: "1px solid var(--ha-divider)",
  borderRadius: 6, background: "rgba(0,0,0,0.04)", cursor: "pointer",
  fontSize: 13, fontWeight: 500, color: "var(--ha-primary-text)",
};
const printBtn: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 6,
  padding: "8px 16px", border: "none", borderRadius: 6,
  background: "var(--ha-primary-color, #1976d2)", color: "#fff",
  cursor: "pointer", fontSize: 13, fontWeight: 600,
};
