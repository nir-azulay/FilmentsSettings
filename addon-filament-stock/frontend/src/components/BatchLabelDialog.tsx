import { useState } from "react";
import {
  AddonConfig,
  SpoolInstance,
  batchLabelsUrl,
  batchPrintLabels,
  spoolLabelUrl,
} from "../api";

interface Props {
  spools: SpoolInstance[];
  config: AddonConfig;
  onClose: () => void;
}

export default function BatchLabelDialog({ spools, config, onClose }: Props) {
  const [printing, setPrinting] = useState(false);
  const [printResults, setPrintResults] = useState<
    { uid: string; ok: boolean; error: string }[] | null
  >(null);

  const printerConfigured = Boolean(config.niimbot_address);
  const uids = spools.map((s) => s.uid);

  const handleDownloadAll = () => {
    const a = document.createElement("a");
    a.href = batchLabelsUrl(uids);
    a.download = "batch-labels.png";
    a.click();
  };

  const handlePrintAll = async () => {
    setPrinting(true);
    setPrintResults(null);
    try {
      const resp = await batchPrintLabels(uids);
      setPrintResults(resp.results);
    } catch (e: any) {
      setPrintResults(uids.map((uid) => ({ uid, ok: false, error: e.message })));
    } finally {
      setPrinting(false);
    }
  };

  const successCount = printResults?.filter((r) => r.ok).length ?? 0;
  const failCount = printResults?.filter((r) => !r.ok).length ?? 0;

  return (
    <div style={overlay} onClick={onClose}>
      <div style={dialog} onClick={(e) => e.stopPropagation()}>
        <h3 style={title}>
          {spools.length} Label{spools.length > 1 ? "s" : ""} Created
        </h3>

        <div style={previewScroll}>
          {spools.map((s) => (
            <div key={s.uid} style={previewCard}>
              <img
                src={spoolLabelUrl(s.uid)}
                alt={`Label ${s.uid}`}
                style={previewImg}
              />
              <span style={uidLabel}>{s.uid}</span>
            </div>
          ))}
        </div>

        {printResults && (
          <div
            style={{
              padding: "6px 10px",
              borderRadius: 6,
              fontSize: 13,
              marginTop: 8,
              background: failCount === 0 ? "var(--ha-pill-success-bg)" : "var(--ha-pill-warn-bg)",
              color: failCount === 0 ? "var(--ha-pill-success-text)" : "var(--ha-pill-warn-text)",
            }}
          >
            {failCount === 0
              ? `All ${successCount} labels printed successfully`
              : `${successCount} printed, ${failCount} failed`}
          </div>
        )}

        <div style={footer}>
          <button onClick={onClose} style={cancelBtn}>
            Close
          </button>
          <button onClick={handleDownloadAll} style={downloadBtn}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            Download All
          </button>
          <button
            onClick={handlePrintAll}
            disabled={!printerConfigured || printing}
            style={{
              ...printBtn,
              opacity: !printerConfigured || printing ? 0.5 : 1,
            }}
            title={
              printerConfigured
                ? "Print all labels to Niimbot"
                : "Configure niimbot_address first"
            }
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="6 9 6 2 18 2 18 9" />
              <path d="M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2" />
              <rect x="6" y="14" width="12" height="8" />
            </svg>
            {printing ? "Printing..." : `Print All (${spools.length})`}
          </button>
        </div>
      </div>
    </div>
  );
}

const overlay: React.CSSProperties = {
  position: "fixed", inset: 0, background: "var(--ha-overlay-bg)",
  display: "flex", alignItems: "center", justifyContent: "center",
  zIndex: 1100,
};
const dialog: React.CSSProperties = {
  background: "var(--ha-card-bg, #fff)", borderRadius: 12, padding: 20,
  width: "min(500px, 92vw)", maxHeight: "85vh", overflowY: "auto",
  boxShadow: "0 8px 32px rgba(0,0,0,0.25)",
};
const title: React.CSSProperties = {
  margin: "0 0 12px", fontSize: 18, fontWeight: 600,
  color: "var(--ha-primary-text)",
};
const previewScroll: React.CSSProperties = {
  display: "flex", flexDirection: "column", gap: 8,
  maxHeight: 400, overflowY: "auto",
  border: "1px solid var(--ha-divider, #e0e0e0)", borderRadius: 8,
  padding: 8, background: "var(--ha-preview-bg)",
};
const previewCard: React.CSSProperties = {
  display: "flex", flexDirection: "column", alignItems: "center", gap: 4,
};
const previewImg: React.CSSProperties = {
  maxWidth: "100%", height: "auto", borderRadius: 4,
};
const uidLabel: React.CSSProperties = {
  fontSize: 11, fontFamily: "monospace", color: "var(--ha-secondary-text)",
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
  borderRadius: 6, background: "var(--ha-subtle-bg)", cursor: "pointer",
  fontSize: 13, fontWeight: 500, color: "var(--ha-primary-text)",
};
const printBtn: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 6,
  padding: "8px 16px", border: "none", borderRadius: 6,
  background: "var(--ha-primary-color, #1976d2)", color: "#fff",
  cursor: "pointer", fontSize: 13, fontWeight: 600,
};
