import { useEffect, useState } from "react";
import {
  Filament,
  ProfileMetadata,
  fetchProfileMetadata,
  profileFileUrl,
  profileZipUrl,
  updateFilament,
} from "../api";

interface Props {
  filament: Filament;
  onUpdate?: () => Promise<void>;
}

/** Expandable per-filament panel that shows the stock metadata you already
 *  store + the BambuStudio profile bundled into the add-on image (if any),
 *  with one-click downloads for individual nozzle files and a full-bundle zip. */
export default function FilamentProfilePanel({ filament, onUpdate }: Props) {
  const [meta, setMeta] = useState<ProfileMetadata | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchProfileMetadata(filament.id)
      .then((m) => {
        if (!cancelled) setMeta(m);
      })
      .catch((e) => {
        if (!cancelled) setError(String(e));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [filament.id]);

  return (
    <div style={panelWrap}>
      <section>
        <h4 style={sectionTitle}>Filament configuration</h4>
        <StockMetadataView filament={filament} onUpdate={onUpdate} />
      </section>

      <section style={{ marginTop: 14 }}>
        <h4 style={sectionTitle}>BambuStudio profile</h4>
        {loading && <p style={muted}>Loading…</p>}
        {error && <p style={errorText}>{error}</p>}
        {!loading && !error && meta && <ProfileView filamentId={filament.id} meta={meta} />}
      </section>
    </div>
  );
}

/* ── Stock metadata table (with inline edit) ─────────────────────────────── */

interface EditState {
  brand: string;
  material: string;
  filament_type: string;
  filament_id: string;
  nozzle_temp_min: string;
  nozzle_temp_max: string;
  bed_temp: string;
  bed_temp_max: string;
  chamber_temp: string;
  density: string;
  low_stock_threshold: string;
  amazon_url: string;
  notes: string;
}

function initEditState(f: Filament): EditState {
  return {
    brand: f.brand,
    material: f.material,
    filament_type: f.filament_type,
    filament_id: f.filament_id ?? "",
    nozzle_temp_min: f.nozzle_temp_min != null ? String(f.nozzle_temp_min) : "",
    nozzle_temp_max: f.nozzle_temp_max != null ? String(f.nozzle_temp_max) : "",
    bed_temp: f.bed_temp != null ? String(f.bed_temp) : "",
    bed_temp_max: f.bed_temp_max != null ? String(f.bed_temp_max) : "",
    chamber_temp: f.chamber_temp != null ? String(f.chamber_temp) : "",
    density: f.density != null ? String(f.density) : "",
    low_stock_threshold: String(f.low_stock_threshold),
    amazon_url: f.amazon_url ?? "",
    notes: f.notes ?? "",
  };
}

function StockMetadataView({ filament, onUpdate }: { filament: Filament; onUpdate?: () => Promise<void> }) {
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<EditState>(initEditState(filament));
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState("");

  useEffect(() => { setForm(initEditState(filament)); }, [filament]);

  const set = (key: keyof EditState) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm((prev) => ({ ...prev, [key]: e.target.value }));

  const handleSave = async () => {
    setSaving(true);
    setSaveError("");
    try {
      const intOrNull = (v: string) => v ? parseInt(v) : null;
      const floatOrNull = (v: string) => v ? parseFloat(v) : null;
      await updateFilament(filament.id, {
        brand: form.brand.trim(),
        material: form.material.trim(),
        filament_type: form.filament_type.trim(),
        filament_id: form.filament_id.trim() || null,
        nozzle_temp_min: intOrNull(form.nozzle_temp_min),
        nozzle_temp_max: intOrNull(form.nozzle_temp_max),
        bed_temp: intOrNull(form.bed_temp),
        bed_temp_max: intOrNull(form.bed_temp_max),
        chamber_temp: intOrNull(form.chamber_temp),
        density: floatOrNull(form.density),
        low_stock_threshold: parseInt(form.low_stock_threshold) || 1,
        amazon_url: form.amazon_url.trim(),
        notes: form.notes.trim(),
      } as any);
      setEditing(false);
      if (onUpdate) await onUpdate();
    } catch (err: any) {
      setSaveError(err?.message || "Save failed");
    } finally {
      setSaving(false);
    }
  };

  if (!editing) {
    const rows: Array<[string, React.ReactNode]> = [
      ["Brand", filament.brand],
      ["Material", filament.material],
      ["Material type", filament.filament_type],
      ["Filament ID", filament.filament_id ?? <em style={muted}>not set</em>],
      [
        "Nozzle temp range",
        filament.nozzle_temp_min && filament.nozzle_temp_max
          ? `${filament.nozzle_temp_min}–${filament.nozzle_temp_max}°C`
          : <em style={muted}>not set</em>,
      ],
      [
        "Bed temp",
        filament.bed_temp && filament.bed_temp_max && filament.bed_temp !== filament.bed_temp_max
          ? `${filament.bed_temp}–${filament.bed_temp_max}°C`
          : filament.bed_temp
            ? `${filament.bed_temp}°C`
            : <em style={muted}>not set</em>,
      ],
      ["Chamber temp", filament.chamber_temp != null ? `${filament.chamber_temp}°C` : <em style={muted}>not set</em>],
      ["Density", filament.density ? `${filament.density} g/cm³` : <em style={muted}>not set</em>],
      ["Low-stock threshold", filament.low_stock_threshold],
      [
        "Amazon URL",
        filament.amazon_url ? (
          <a href={filament.amazon_url} target="_blank" rel="noopener" style={linkStyle}>
            {filament.amazon_url}
          </a>
        ) : (
          <em style={muted}>not set</em>
        ),
      ],
    ];
    return (
      <div>
        <table style={metaTable}>
          <tbody>
            {rows.map(([k, v]) => (
              <tr key={k}>
                <td style={metaKey}>{k}</td>
                <td style={metaVal}>{v}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <button onClick={() => { setForm(initEditState(filament)); setEditing(true); }} style={editBtn}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
          </svg>
          Edit
        </button>
      </div>
    );
  }

  const editRows: Array<[string, keyof EditState, string, string?]> = [
    ["Brand", "brand", "text"],
    ["Material", "material", "text"],
    ["Material type", "filament_type", "text"],
    ["Filament ID", "filament_id", "text"],
    ["Nozzle temp min (°C)", "nozzle_temp_min", "number"],
    ["Nozzle temp max (°C)", "nozzle_temp_max", "number"],
    ["Bed temp min (°C)", "bed_temp", "number"],
    ["Bed temp max (°C)", "bed_temp_max", "number"],
    ["Chamber temp (°C)", "chamber_temp", "number"],
    ["Density (g/cm³)", "density", "number", "0.01"],
    ["Low-stock threshold", "low_stock_threshold", "number"],
    ["Amazon URL", "amazon_url", "text"],
  ];

  return (
    <div>
      <table style={metaTable}>
        <tbody>
          {editRows.map(([label, key, type, step]) => (
            <tr key={key}>
              <td style={metaKey}>{label}</td>
              <td style={metaVal}>
                <input
                  style={editInput}
                  type={type}
                  step={step}
                  value={form[key]}
                  onChange={set(key)}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {saveError && <div style={editError}>{saveError}</div>}
      <div style={editActions}>
        <button onClick={() => setEditing(false)} style={editCancelBtn} disabled={saving}>Cancel</button>
        <button onClick={handleSave} style={editSaveBtn} disabled={saving}>
          {saving ? "Saving…" : "Save"}
        </button>
      </div>
    </div>
  );
}

/* ── BambuStudio profile view ─────────────────────────────────────────────── */

function ProfileView({ filamentId, meta }: { filamentId: number; meta: ProfileMetadata }) {
  if (!meta.available) {
    return (
      <div style={emptyState}>
        <p style={{ margin: 0 }}>
          No bundled BambuStudio profile for <strong>{meta.product}</strong>.
        </p>
        <p style={{ margin: "6px 0 0", fontSize: 11, color: "var(--ha-secondary-text)" }}>
          The add-on ships profiles for the filaments tracked in the maintainer's
          repo (SUNLU, Inslogic on the Bambu Lab H2S). To add a new one, follow
          <code style={code}> .cursor/rules/add-filament.mdc</code> and re-sync
          with <code style={code}>./sync_profiles.sh</code>.
        </p>
      </div>
    );
  }

  return (
    <>
      <p style={{ margin: "0 0 8px", fontSize: 12, color: "var(--ha-secondary-text)" }}>
        <strong style={{ color: "var(--ha-primary-text)" }}>{meta.product}</strong> -- one base
        filament profile listing all H2S nozzle sizes in <code style={code}>compatible_printers</code>,
        a user preset, and {meta.nozzles.length} process preset(s).
      </p>

      <SummaryTable summary={meta.summary} />

      <h5 style={subTitle}>Per-nozzle process presets</h5>
      <table style={nozzleTable}>
        <thead>
          <tr>
            <th style={th}>Nozzle</th>
            <th style={th}>Layer height</th>
            <th style={th}>File name</th>
            <th style={th}></th>
          </tr>
        </thead>
        <tbody>
          {meta.nozzles.map((n) => (
            <tr key={n.file_name}>
              <td style={td}>{n.nozzle_mm} mm</td>
              <td style={td}>{n.layer_height_mm} mm</td>
              <td style={{ ...td, fontFamily: "ui-monospace, monospace", fontSize: 11 }}>{n.file_name}</td>
              <td style={td}>
                <a href={profileFileUrl(filamentId, n.file_name)} download style={downloadLink}>
                  Download JSON
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h5 style={subTitle}>Base + user preset</h5>
      <ul style={fileList}>
        {meta.base_file && (
          <li>
            <a href={profileFileUrl(filamentId, meta.base_file)} download style={downloadLink}>
              {meta.base_file}
            </a>
            <span style={muted}> — base filament profile</span>
          </li>
        )}
        {meta.preset_file && (
          <li>
            <a href={profileFileUrl(filamentId, meta.preset_file)} download style={downloadLink}>
              {meta.preset_file}
            </a>
            <span style={muted}> — user preset (inherits from base)</span>
          </li>
        )}
      </ul>

      <div style={{ marginTop: 12, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={muted}>{meta.files.length} files total ({meta.files.filter((f) => f.endsWith(".json")).length} JSON + {meta.files.filter((f) => f.endsWith(".info")).length} sidecars).</span>
        <a href={profileZipUrl(filamentId)} download style={zipBtn}>
          ⬇ Download all (.zip)
        </a>
      </div>

      <p style={{ marginTop: 10, marginBottom: 0, fontSize: 11, color: "var(--ha-secondary-text)" }}>
        Drop the unzipped files into BambuStudio's user folder:
        <br />
        <code style={code}>%APPDATA%\BambuStudio\user\&lt;your-id&gt;\filament\base\</code> (base + base.info)
        <br />
        <code style={code}>%APPDATA%\BambuStudio\user\&lt;your-id&gt;\filament\</code> (preset + preset.info)
        <br />
        <code style={code}>%APPDATA%\BambuStudio\user\&lt;your-id&gt;\process\</code> (per-nozzle process files + their .info)
      </p>
    </>
  );
}

/* ── Summary of the most useful base-profile fields ───────────────────────── */

const SUMMARY_LABELS: Array<[string, string]> = [
  ["filament_density", "Density (g/cm³)"],
  ["filament_diameter", "Diameter (mm)"],
  ["nozzle_temperature", "Nozzle temp (°C)"],
  ["nozzle_temperature_initial_layer", "Nozzle temp, 1st layer (°C)"],
  ["hot_plate_temp", "Hot plate (°C)"],
  ["textured_plate_temp", "Textured PEI (°C)"],
  ["eng_plate_temp", "Engineering plate (°C)"],
  ["filament_max_volumetric_speed", "Max vol speed (mm³/s)"],
  ["filament_retraction_length", "Retraction (mm)"],
  ["filament_retraction_speed", "Retraction speed (mm/s)"],
  ["temperature_vitrification", "Tg (°C)"],
];

function SummaryTable({ summary }: { summary: ProfileMetadata["summary"] }) {
  const variants = (summary.filament_extruder_variant as string[]) ?? ["Standard"];
  const hasHighFlow = variants.length > 1;
  const present = SUMMARY_LABELS.filter(([key]) => summary[key] !== undefined && summary[key] !== null);
  if (!present.length) return null;

  return (
    <div style={{ overflowX: "auto", marginBottom: 10 }}>
      <table style={summaryTable}>
        <thead>
          <tr>
            <th style={th}>Field</th>
            <th style={th}>{variants[0] ?? "Standard"}</th>
            {hasHighFlow && <th style={th}>{variants[1]}</th>}
          </tr>
        </thead>
        <tbody>
          {present.map(([key, label]) => {
            const v = summary[key];
            const arr = Array.isArray(v) ? v : [String(v)];
            return (
              <tr key={key}>
                <td style={td}>{label}</td>
                <td style={td}>{arr[0] ?? "—"}</td>
                {hasHighFlow && <td style={td}>{arr[1] ?? arr[0] ?? "—"}</td>}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

/* ── Styles ───────────────────────────────────────────────────────────────── */

const panelWrap: React.CSSProperties = {
  padding: "12px 16px",
  borderTop: "1px solid var(--ha-divider)",
  background: "rgba(0,0,0,0.02)",
};
const sectionTitle: React.CSSProperties = {
  margin: "0 0 8px",
  fontSize: 11,
  textTransform: "uppercase",
  letterSpacing: "0.08em",
  color: "var(--ha-secondary-text)",
  fontWeight: 600,
};
const subTitle: React.CSSProperties = {
  margin: "10px 0 4px",
  fontSize: 11,
  fontWeight: 600,
  color: "var(--ha-primary-text)",
};
const metaTable: React.CSSProperties = { width: "100%", borderCollapse: "collapse", fontSize: 12 };
const metaKey: React.CSSProperties = {
  padding: "3px 8px 3px 0",
  color: "var(--ha-secondary-text)",
  fontWeight: 500,
  whiteSpace: "nowrap",
  verticalAlign: "top",
  width: "1%",
};
const metaVal: React.CSSProperties = { padding: "3px 0", color: "var(--ha-primary-text)" };
const muted: React.CSSProperties = { color: "var(--ha-secondary-text)" };
const errorText: React.CSSProperties = { color: "var(--ha-error)", fontSize: 12 };
const code: React.CSSProperties = {
  background: "rgba(0,0,0,0.05)",
  padding: "1px 4px",
  borderRadius: 3,
  fontSize: 11,
};
const emptyState: React.CSSProperties = {
  padding: 12,
  border: "1px dashed var(--ha-divider)",
  borderRadius: 6,
  background: "var(--ha-card-bg)",
};
const nozzleTable: React.CSSProperties = { width: "100%", borderCollapse: "collapse", fontSize: 12 };
const summaryTable: React.CSSProperties = { width: "100%", borderCollapse: "collapse", fontSize: 11 };
const th: React.CSSProperties = {
  textAlign: "left",
  padding: "4px 8px 4px 0",
  borderBottom: "1px solid var(--ha-divider)",
  fontWeight: 600,
  color: "var(--ha-secondary-text)",
  fontSize: 10,
  textTransform: "uppercase",
  letterSpacing: "0.04em",
};
const td: React.CSSProperties = {
  padding: "4px 8px 4px 0",
  borderBottom: "1px solid var(--ha-divider)",
  color: "var(--ha-primary-text)",
};
const linkStyle: React.CSSProperties = { color: "var(--ha-primary-color)" };
const downloadLink: React.CSSProperties = {
  color: "var(--ha-primary-color)",
  textDecoration: "none",
  fontSize: 11,
  fontWeight: 500,
};
const fileList: React.CSSProperties = {
  listStyle: "none",
  padding: 0,
  margin: 0,
  fontSize: 12,
  lineHeight: 1.6,
};
const zipBtn: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 6,
  padding: "6px 12px",
  background: "var(--ha-primary-color)",
  color: "#fff",
  border: "none",
  borderRadius: 4,
  fontSize: 12,
  fontWeight: 600,
  textDecoration: "none",
  cursor: "pointer",
};
const editBtn: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 5,
  marginTop: 8,
  padding: "5px 12px",
  background: "none",
  border: "1px solid var(--ha-divider)",
  borderRadius: 4,
  fontSize: 12,
  fontWeight: 500,
  color: "var(--ha-primary-text)",
  cursor: "pointer",
};
const editInput: React.CSSProperties = {
  padding: "4px 8px",
  border: "1px solid var(--ha-divider)",
  borderRadius: 4,
  fontSize: 12,
  color: "var(--ha-primary-text)",
  background: "#fff",
  width: "100%",
  boxSizing: "border-box",
};
const editActions: React.CSSProperties = {
  display: "flex",
  justifyContent: "flex-end",
  gap: 8,
  marginTop: 8,
};
const editCancelBtn: React.CSSProperties = {
  padding: "5px 14px",
  background: "none",
  border: "1px solid var(--ha-divider)",
  borderRadius: 4,
  fontSize: 12,
  fontWeight: 500,
  color: "var(--ha-primary-text)",
  cursor: "pointer",
};
const editSaveBtn: React.CSSProperties = {
  padding: "5px 14px",
  background: "var(--ha-primary-color)",
  color: "#fff",
  border: "none",
  borderRadius: 4,
  fontSize: 12,
  fontWeight: 600,
  cursor: "pointer",
};
const editError: React.CSSProperties = {
  marginTop: 6,
  padding: "6px 10px",
  background: "var(--ha-error-bg)",
  color: "var(--ha-error)",
  borderRadius: 4,
  fontSize: 11,
};
