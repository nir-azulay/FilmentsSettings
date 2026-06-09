import { useState } from "react";
import { createFilament } from "../api";

interface Props {
  onClose: () => void;
  onCreated: () => Promise<void>;
}

export default function CreateFilamentDialog({ onClose, onCreated }: Props) {
  const [brand, setBrand] = useState("");
  const [material, setMaterial] = useState("");
  const [filamentType, setFilamentType] = useState("PLA");
  const [filamentId, setFilamentId] = useState("");
  const [density, setDensity] = useState("");
  const [nozzleTempMin, setNozzleTempMin] = useState("");
  const [nozzleTempMax, setNozzleTempMax] = useState("");
  const [bedTemp, setBedTemp] = useState("");
  const [bedTempMax, setBedTempMax] = useState("");
  const [chamberTemp, setChamberTemp] = useState("");
  const [amazonUrl, setAmazonUrl] = useState("");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const canSubmit = brand.trim() && material.trim() && filamentType.trim();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit || submitting) return;
    setSubmitting(true);
    setError("");
    try {
      await createFilament({
        brand: brand.trim(),
        material: material.trim(),
        filament_type: filamentType.trim(),
        filament_id: filamentId.trim() || undefined,
        density: density ? parseFloat(density) : undefined,
        nozzle_temp_min: nozzleTempMin ? parseInt(nozzleTempMin) : undefined,
        nozzle_temp_max: nozzleTempMax ? parseInt(nozzleTempMax) : undefined,
        bed_temp: bedTemp ? parseInt(bedTemp) : undefined,
        bed_temp_max: bedTempMax ? parseInt(bedTempMax) : undefined,
        chamber_temp: chamberTemp ? parseInt(chamberTemp) : undefined,
        amazon_url: amazonUrl.trim(),
        notes: notes.trim(),
      } as any);
      await onCreated();
      onClose();
    } catch (err: any) {
      setError(err?.message || "Failed to create filament");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={overlay} onClick={onClose}>
      <div style={dialog} onClick={(e) => e.stopPropagation()}>
        <div style={dialogHeader}>
          <h2 style={dialogTitle}>Add New Filament</h2>
          <button onClick={onClose} style={closeBtn} aria-label="Close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <section style={section}>
            <p style={sectionLabel}>Required</p>
            <div style={fieldGrid}>
              <label style={fieldLabel}>
                Brand
                <input style={inputStyle} value={brand} onChange={(e) => setBrand(e.target.value)} placeholder="e.g. SUNLU, Jayo" required />
              </label>
              <label style={fieldLabel}>
                Material
                <input style={inputStyle} value={material} onChange={(e) => setMaterial(e.target.value)} placeholder="e.g. PLA Pro, PETG HS" required />
              </label>
              <label style={fieldLabel}>
                Type
                <select style={selectStyle} value={filamentType} onChange={(e) => setFilamentType(e.target.value)}>
                  <option>PLA</option>
                  <option>PETG</option>
                  <option>ASA</option>
                  <option>ABS</option>
                  <option>TPU</option>
                  <option>PA</option>
                  <option>PC</option>
                  <option>PVA</option>
                </select>
              </label>
            </div>
          </section>

          <section style={section}>
            <p style={sectionLabel}>Optional Details</p>
            <div style={fieldGrid}>
              <label style={fieldLabel}>
                Bambu Filament ID
                <input style={inputStyle} value={filamentId} onChange={(e) => setFilamentId(e.target.value)} placeholder="e.g. P759ffa0" />
              </label>
              <label style={fieldLabel}>
                Density (g/cm³)
                <input style={inputStyle} type="number" step="0.01" value={density} onChange={(e) => setDensity(e.target.value)} placeholder="e.g. 1.24" />
              </label>
              <label style={fieldLabel}>
                Nozzle Min (°C)
                <input style={inputStyle} type="number" value={nozzleTempMin} onChange={(e) => setNozzleTempMin(e.target.value)} placeholder="e.g. 190" />
              </label>
              <label style={fieldLabel}>
                Nozzle Max (°C)
                <input style={inputStyle} type="number" value={nozzleTempMax} onChange={(e) => setNozzleTempMax(e.target.value)} placeholder="e.g. 230" />
              </label>
              <label style={fieldLabel}>
                Bed Temp Min (°C)
                <input style={inputStyle} type="number" value={bedTemp} onChange={(e) => setBedTemp(e.target.value)} placeholder="e.g. 60" />
              </label>
              <label style={fieldLabel}>
                Bed Temp Max (°C)
                <input style={inputStyle} type="number" value={bedTempMax} onChange={(e) => setBedTempMax(e.target.value)} placeholder="e.g. 90" />
              </label>
              <label style={fieldLabel}>
                Chamber Temp (°C)
                <input style={inputStyle} type="number" value={chamberTemp} onChange={(e) => setChamberTemp(e.target.value)} placeholder="e.g. 50" />
              </label>
              <label style={fieldLabel}>
                Amazon URL
                <input style={inputStyle} value={amazonUrl} onChange={(e) => setAmazonUrl(e.target.value)} placeholder="https://..." />
              </label>
            </div>
            <label style={{ ...fieldLabel, marginTop: 8 }}>
              Notes
              <textarea style={{ ...inputStyle, minHeight: 48, resize: "vertical" }} value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Any notes about this filament..." />
            </label>
          </section>

          {error && (
            <div style={errorBanner}>{error}</div>
          )}

          <div style={footer}>
            <button type="button" onClick={onClose} style={cancelBtn}>Cancel</button>
            <button type="submit" disabled={!canSubmit || submitting} style={{
              ...primaryBtn,
              opacity: canSubmit && !submitting ? 1 : 0.5,
            }}>
              {submitting ? "Creating…" : "Create Filament"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

const overlay: React.CSSProperties = {
  position: "fixed", inset: 0,
  background: "var(--ha-overlay-bg)",
  backdropFilter: "blur(4px)",
  display: "flex", justifyContent: "center", alignItems: "center",
  zIndex: 1000,
  animation: "fadeIn 0.15s ease-out",
};
const dialog: React.CSSProperties = {
  background: "var(--ha-card-bg)",
  borderRadius: "var(--ha-card-radius)",
  width: "92%", maxWidth: 520, maxHeight: "90vh",
  overflowY: "auto",
  boxShadow: "var(--ha-dialog-shadow)",
  animation: "slideUp 0.2s ease-out",
};
const dialogHeader: React.CSSProperties = {
  display: "flex", justifyContent: "space-between", alignItems: "center",
  padding: "16px 20px",
  borderBottom: "1px solid var(--ha-divider)",
  position: "sticky", top: 0, background: "var(--ha-card-bg)", zIndex: 1,
};
const dialogTitle: React.CSSProperties = {
  fontSize: 16, fontWeight: 500, color: "var(--ha-primary-text)",
};
const closeBtn: React.CSSProperties = {
  background: "none", border: "none",
  color: "var(--ha-secondary-text)",
  width: 32, height: 32,
  display: "flex", alignItems: "center", justifyContent: "center",
  borderRadius: "50%", cursor: "pointer",
};
const section: React.CSSProperties = {
  padding: "14px 20px",
  borderBottom: "1px solid var(--ha-divider)",
};
const sectionLabel: React.CSSProperties = {
  fontSize: 12, fontWeight: 500,
  color: "var(--ha-secondary-text)",
  textTransform: "uppercase", letterSpacing: "0.06em",
  marginBottom: 10,
};
const fieldGrid: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "1fr 1fr",
  gap: 10,
};
const fieldLabel: React.CSSProperties = {
  display: "flex", flexDirection: "column", gap: 4,
  fontSize: 12, color: "var(--ha-secondary-text)", fontWeight: 500,
};
const inputStyle: React.CSSProperties = {
  padding: "7px 10px",
  background: "var(--ha-input-bg)",
  border: "1px solid var(--ha-divider)",
  borderRadius: "var(--ha-btn-radius)",
  color: "var(--ha-primary-text)",
  fontSize: 13, outline: "none",
  width: "100%", boxSizing: "border-box",
};
const selectStyle: React.CSSProperties = {
  ...inputStyle,
  cursor: "pointer",
};
const footer: React.CSSProperties = {
  display: "flex", justifyContent: "flex-end", gap: 8,
  padding: "14px 20px",
};
const cancelBtn: React.CSSProperties = {
  padding: "8px 16px",
  background: "none",
  border: "1px solid var(--ha-divider)",
  borderRadius: "var(--ha-btn-radius)",
  color: "var(--ha-primary-text)",
  fontSize: 13, fontWeight: 500,
  cursor: "pointer",
};
const primaryBtn: React.CSSProperties = {
  padding: "8px 18px",
  background: "var(--ha-primary-color)",
  color: "#fff",
  border: "none",
  borderRadius: "var(--ha-btn-radius)",
  fontSize: 13, fontWeight: 500,
  cursor: "pointer",
};
const errorBanner: React.CSSProperties = {
  margin: "0 20px",
  padding: "8px 12px",
  background: "var(--ha-error-bg)",
  color: "var(--ha-error)",
  borderRadius: "var(--ha-btn-radius)",
  fontSize: 12, fontWeight: 500,
};
