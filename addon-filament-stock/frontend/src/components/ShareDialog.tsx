import { useEffect, useState } from "react";
import { ShareResponse, shareFilament, shareQrUrl } from "../api";

interface Props {
  filamentId: number;
  filamentName: string;
  onClose: () => void;
}

export default function ShareDialog({ filamentId, filamentName, onClose }: Props) {
  const [data, setData] = useState<ShareResponse | null>(null);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    shareFilament(filamentId)
      .then(setData)
      .catch((e) => setError(e.message));
  }, [filamentId]);

  const handleCopyJson = async () => {
    if (!data) return;
    try {
      await navigator.clipboard.writeText(data.encoded);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = data.encoded;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data.payload, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${filamentName.replace(/\s+/g, "_")}_share.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const fil = data?.payload.filament;

  return (
    <div style={overlay} onClick={onClose}>
      <div style={dialog} onClick={(e) => e.stopPropagation()}>
        <h3 style={title}>Share Filament</h3>

        <div style={nameRow}>
          <span style={{ fontWeight: 600, fontSize: 15 }}>{filamentName}</span>
        </div>

        {error && <p style={errorText}>{error}</p>}

        {!data && !error && <p style={loadingText}>Generating share data…</p>}

        {data && (
          <>
            {/* QR code */}
            <div style={qrWrap}>
              <img
                src={shareQrUrl(filamentId)}
                alt={`QR code for ${filamentName}`}
                style={qrImg}
              />
            </div>

            {/* Key parameters */}
            {fil && (
              <div style={paramsGrid}>
                {fil.nozzle_temp_min != null && fil.nozzle_temp_max != null && (
                  <ParamChip label="Nozzle" value={`${fil.nozzle_temp_min}–${fil.nozzle_temp_max}°C`} />
                )}
                {fil.bed_temp != null && (
                  <ParamChip
                    label="Bed"
                    value={
                      fil.bed_temp_max != null && fil.bed_temp_max !== fil.bed_temp
                        ? `${fil.bed_temp}–${fil.bed_temp_max}°C`
                        : `${fil.bed_temp}°C`
                    }
                  />
                )}
                {fil.density != null && (
                  <ParamChip label="Density" value={`${fil.density} g/cm³`} />
                )}
                {fil.chamber_temp != null && (
                  <ParamChip label="Chamber" value={`${fil.chamber_temp}°C`} />
                )}
                {fil.dry_temp != null && fil.dry_time != null && (
                  <ParamChip label="Drying" value={`${fil.dry_temp}°C / ${fil.dry_time}h`} />
                )}
              </div>
            )}

            {/* Colors */}
            {data.payload.colors.length > 0 && (
              <div style={colorsRow}>
                <span style={{ fontSize: 12, color: "var(--ha-secondary-text)" }}>
                  Colors included:
                </span>
                <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                  {data.payload.colors.map((c, i) => (
                    <span key={i} style={colorChip}>
                      <span
                        style={{
                          width: 12, height: 12, borderRadius: 3,
                          background: c.color_hex, display: "inline-block",
                          border: "1px solid var(--ha-divider)",
                        }}
                      />
                      {c.color_name}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {/* Actions */}
        <div style={footer}>
          <button onClick={onClose} style={cancelBtn}>Close</button>
          <button onClick={handleDownload} disabled={!data} style={downloadBtn}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            Download JSON
          </button>
          <button onClick={handleCopyJson} disabled={!data} style={copyBtn}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
              <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
            </svg>
            {copied ? "Copied!" : "Copy Encoded"}
          </button>
        </div>
      </div>
    </div>
  );
}

function ParamChip({ label, value }: { label: string; value: string }) {
  return (
    <div style={paramChipStyle}>
      <span style={{ fontSize: 11, color: "var(--ha-secondary-text)", fontWeight: 500 }}>{label}</span>
      <span style={{ fontSize: 13, fontWeight: 600 }}>{value}</span>
    </div>
  );
}

const overlay: React.CSSProperties = {
  position: "fixed", inset: 0, background: "var(--ha-overlay-bg)",
  display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000,
};
const dialog: React.CSSProperties = {
  background: "var(--ha-card-bg, #fff)", borderRadius: 12, padding: 20,
  width: "min(480px, 90vw)", maxHeight: "85vh", overflowY: "auto",
  boxShadow: "0 8px 32px rgba(0,0,0,0.2)",
};
const title: React.CSSProperties = {
  margin: "0 0 12px", fontSize: 18, fontWeight: 600,
  color: "var(--ha-primary-text)",
};
const nameRow: React.CSSProperties = {
  marginBottom: 12, color: "var(--ha-primary-text)",
};
const errorText: React.CSSProperties = {
  color: "var(--ha-error)", fontSize: 13, padding: "8px 12px",
  background: "var(--ha-error-bg)", borderRadius: 6,
};
const loadingText: React.CSSProperties = {
  color: "var(--ha-secondary-text)", fontSize: 13, textAlign: "center",
  padding: "24px 0",
};
const qrWrap: React.CSSProperties = {
  border: "1px solid var(--ha-divider, #e0e0e0)", borderRadius: 8,
  padding: 12, background: "var(--ha-preview-bg)", textAlign: "center", marginBottom: 12,
};
const qrImg: React.CSSProperties = {
  maxWidth: 200, height: "auto",
};
const paramsGrid: React.CSSProperties = {
  display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 12,
};
const paramChipStyle: React.CSSProperties = {
  display: "flex", flexDirection: "column", gap: 2,
  padding: "6px 10px", borderRadius: 6,
  background: "var(--ha-subtle-bg)", fontSize: 13,
};
const colorsRow: React.CSSProperties = {
  display: "flex", flexDirection: "column", gap: 6, marginBottom: 8,
};
const colorChip: React.CSSProperties = {
  display: "inline-flex", alignItems: "center", gap: 4,
  padding: "2px 8px", borderRadius: 4, fontSize: 12,
  background: "var(--ha-subtle-bg)",
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
const copyBtn: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 6,
  padding: "8px 16px", border: "none", borderRadius: 6,
  background: "var(--ha-primary-color, #1976d2)", color: "#fff",
  cursor: "pointer", fontSize: 13, fontWeight: 600,
};
