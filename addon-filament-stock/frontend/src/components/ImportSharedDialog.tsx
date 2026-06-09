import { useRef, useState } from "react";
import { SharePayload, importSharedFilament } from "../api";

interface Props {
  onClose: () => void;
  onImported: () => void;
}

type ParsedPreview = {
  payload: SharePayload;
  source: "json" | "encoded";
};

export default function ImportSharedDialog({ onClose, onImported }: Props) {
  const [rawText, setRawText] = useState("");
  const [preview, setPreview] = useState<ParsedPreview | null>(null);
  const [parseError, setParseError] = useState("");
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState<{ ok: boolean; msg: string } | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const tryParse = (text: string) => {
    setRawText(text);
    setParseError("");
    setPreview(null);
    setResult(null);
    if (!text.trim()) return;

    try {
      const parsed = JSON.parse(text.trim());
      if (parsed.share_version && parsed.filament) {
        setPreview({ payload: parsed, source: "json" });
        return;
      }
      if (parsed.filament) {
        setPreview({ payload: parsed as SharePayload, source: "json" });
        return;
      }
      setParseError("JSON doesn't look like a filament share payload");
    } catch {
      try {
        const decoded = atob(text.trim().replace(/-/g, "+").replace(/_/g, "/"));
        const parsed = JSON.parse(decoded);
        if (parsed.filament) {
          setPreview({ payload: parsed, source: "encoded" });
          return;
        }
        setParseError("Decoded data doesn't contain filament info");
      } catch {
        setParseError("Could not parse as JSON or base64-encoded share data");
      }
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === "string") {
        tryParse(reader.result);
      }
    };
    reader.readAsText(file);
  };

  const handleImport = async () => {
    if (!preview) return;
    setImporting(true);
    setResult(null);
    try {
      const res = await importSharedFilament(preview.payload);
      setResult({
        ok: true,
        msg: `Imported "${preview.payload.filament.brand} ${preview.payload.filament.material}" with ${res.colors_added} color(s).`,
      });
      onImported();
    } catch (e: any) {
      setResult({ ok: false, msg: e.message || "Import failed" });
    } finally {
      setImporting(false);
    }
  };

  const fil = preview?.payload.filament;

  return (
    <div style={overlay} onClick={onClose}>
      <div style={dialog} onClick={(e) => e.stopPropagation()}>
        <h3 style={title}>Import Shared Filament</h3>

        <p style={desc}>
          Paste a shared filament JSON or encoded string below, or upload a file.
        </p>

        {/* Textarea input */}
        <textarea
          value={rawText}
          onChange={(e) => tryParse(e.target.value)}
          placeholder="Paste JSON payload or encoded share string…"
          style={textarea}
          rows={5}
        />

        {/* File upload */}
        <div style={fileRow}>
          <input
            ref={fileRef}
            type="file"
            accept=".json,.txt"
            onChange={handleFileUpload}
            style={{ display: "none" }}
          />
          <button onClick={() => fileRef.current?.click()} style={fileBtn}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            Upload File
          </button>
        </div>

        {parseError && <p style={errorText}>{parseError}</p>}

        {/* Preview */}
        {preview && fil && (
          <div style={previewBox}>
            <h4 style={previewTitle}>Preview</h4>
            <div style={previewRow}>
              <strong>{fil.brand} {fil.material}</strong>
              <span style={previewTag}>{fil.filament_type}</span>
            </div>
            <div style={previewDetails}>
              {fil.nozzle_temp_min != null && fil.nozzle_temp_max != null && (
                <span>Nozzle: {fil.nozzle_temp_min}–{fil.nozzle_temp_max}°C</span>
              )}
              {fil.bed_temp != null && <span>Bed: {fil.bed_temp}°C</span>}
              {fil.density != null && <span>Density: {fil.density} g/cm³</span>}
            </div>
            {preview.payload.colors.length > 0 && (
              <div style={previewColors}>
                {preview.payload.colors.map((c, i) => (
                  <span key={i} style={colorChip}>
                    <span
                      style={{
                        width: 10, height: 10, borderRadius: 2,
                        background: c.color_hex, display: "inline-block",
                        border: "1px solid var(--ha-divider)",
                      }}
                    />
                    {c.color_name}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Result message */}
        {result && (
          <div
            style={{
              padding: "8px 12px", borderRadius: 6, fontSize: 13, marginTop: 8,
              background: result.ok ? "var(--ha-pill-success-bg)" : "var(--ha-error-bg)",
              color: result.ok ? "var(--ha-pill-success-text)" : "var(--ha-error)",
            }}
          >
            {result.msg}
          </div>
        )}

        {/* Actions */}
        <div style={footer}>
          <button onClick={onClose} style={cancelBtn}>
            {result?.ok ? "Done" : "Cancel"}
          </button>
          {!result?.ok && (
            <button
              onClick={handleImport}
              disabled={!preview || importing}
              style={{
                ...importBtn,
                opacity: !preview || importing ? 0.5 : 1,
              }}
            >
              {importing ? "Importing…" : "Import"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

const overlay: React.CSSProperties = {
  position: "fixed", inset: 0, background: "var(--ha-overlay-bg)",
  display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000,
};
const dialog: React.CSSProperties = {
  background: "var(--ha-card-bg, #fff)", borderRadius: 12, padding: 20,
  width: "min(500px, 90vw)", maxHeight: "85vh", overflowY: "auto",
  boxShadow: "0 8px 32px rgba(0,0,0,0.2)",
};
const title: React.CSSProperties = {
  margin: "0 0 8px", fontSize: 18, fontWeight: 600,
  color: "var(--ha-primary-text)",
};
const desc: React.CSSProperties = {
  margin: "0 0 12px", fontSize: 13, color: "var(--ha-secondary-text)",
};
const textarea: React.CSSProperties = {
  width: "100%", padding: "10px 12px", borderRadius: 6, fontSize: 13,
  border: "1px solid var(--ha-divider, #ccc)",
  background: "var(--ha-card-bg, #fff)", color: "var(--ha-primary-text)",
  fontFamily: "monospace", resize: "vertical", boxSizing: "border-box",
};
const fileRow: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 8, margin: "8px 0",
};
const fileBtn: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 6,
  padding: "6px 14px", border: "1px solid var(--ha-divider)",
  borderRadius: 6, background: "var(--ha-subtle-bg)", cursor: "pointer",
  fontSize: 13, color: "var(--ha-primary-text)",
};
const errorText: React.CSSProperties = {
  color: "var(--ha-error)", fontSize: 13, padding: "8px 12px",
  background: "var(--ha-error-bg)", borderRadius: 6, margin: "8px 0",
};
const previewBox: React.CSSProperties = {
  border: "1px solid var(--ha-divider, #e0e0e0)", borderRadius: 8,
  padding: 12, marginTop: 8, background: "var(--ha-tray-empty-bg)",
};
const previewTitle: React.CSSProperties = {
  margin: "0 0 8px", fontSize: 14, fontWeight: 600,
  color: "var(--ha-primary-text)",
};
const previewRow: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 8, marginBottom: 6,
  fontSize: 14, color: "var(--ha-primary-text)",
};
const previewTag: React.CSSProperties = {
  padding: "2px 8px", borderRadius: 4, fontSize: 11, fontWeight: 600,
  background: "var(--ha-primary-color, #1976d2)", color: "#fff",
};
const previewDetails: React.CSSProperties = {
  display: "flex", flexWrap: "wrap", gap: 12, fontSize: 12,
  color: "var(--ha-secondary-text)", marginBottom: 6,
};
const previewColors: React.CSSProperties = {
  display: "flex", gap: 4, flexWrap: "wrap", marginTop: 4,
};
const colorChip: React.CSSProperties = {
  display: "inline-flex", alignItems: "center", gap: 4,
  padding: "2px 8px", borderRadius: 4, fontSize: 11,
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
const importBtn: React.CSSProperties = {
  padding: "8px 20px", border: "none", borderRadius: 6,
  background: "var(--ha-primary-color, #1976d2)", color: "#fff",
  cursor: "pointer", fontSize: 13, fontWeight: 600,
};
