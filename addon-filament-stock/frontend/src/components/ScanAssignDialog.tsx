import { useEffect, useState } from "react";
import {
  AmsTray,
  AmsTraysResponse,
  SpoolInstance,
  assignSpoolToTray,
  fetchAmsTrays,
  fetchSpoolByUid,
} from "../api";

interface Props {
  uid: string;
  onClose: () => void;
  onAssigned?: () => void;
}

export default function ScanAssignDialog({ uid, onClose, onAssigned }: Props) {
  const [spool, setSpool] = useState<SpoolInstance | null>(null);
  const [trays, setTrays] = useState<AmsTray[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTray, setSelectedTray] = useState<string | null>(null);
  const [pushToPrinter, setPushToPrinter] = useState(false);
  const [assigning, setAssigning] = useState(false);
  const [result, setResult] = useState<{ ok: boolean; msg: string } | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [sp, amsResp] = await Promise.all([
          fetchSpoolByUid(uid),
          fetchAmsTrays(),
        ]);
        if (cancelled) return;
        setSpool(sp);
        setTrays(amsResp.trays ?? []);
        if (sp.status !== "in_stock") {
          setError(`Spool ${uid} is not available (status: ${sp.status})`);
        }
      } catch (e: any) {
        if (!cancelled) setError(e.message || "Failed to load spool");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [uid]);

  const handleAssign = async () => {
    if (!selectedTray || !spool) return;
    setAssigning(true);
    setResult(null);
    try {
      const tray = trays.find((t) => t.entity_id === selectedTray);
      const resp = await assignSpoolToTray(uid, {
        entity_id: selectedTray,
        push_to_printer: pushToPrinter,
        location_label: tray?.location_label ?? "",
      });
      const pushMsg = resp.push_to_printer.requested
        ? resp.push_to_printer.ok
          ? " Printer updated."
          : ` Printer update failed: ${resp.push_to_printer.error}`
        : "";
      setResult({ ok: true, msg: `Assigned to ${tray?.location_label || selectedTray}.${pushMsg}` });
      onAssigned?.();
    } catch (e: any) {
      setResult({ ok: false, msg: e.message || "Assignment failed" });
    } finally {
      setAssigning(false);
    }
  };

  const colorSwatch = spool?.color_hex ?? "#808080";

  return (
    <div style={overlay} onClick={onClose}>
      <div style={dialog} onClick={(e) => e.stopPropagation()}>
        <h3 style={title}>Scan &amp; Assign Spool</h3>

        {loading && <p style={infoText}>Loading spool {uid}...</p>}

        {error && <p style={errorText}>{error}</p>}

        {spool && !error && (
          <>
            {/* Spool info */}
            <div style={spoolInfo}>
              <div
                style={{
                  width: 36, height: 36, borderRadius: 6,
                  background: colorSwatch, border: "2px solid #ccc",
                  flexShrink: 0,
                }}
              />
              <div>
                <div style={{ fontWeight: 600, fontSize: 15 }}>
                  {spool.brand} {spool.material}
                </div>
                <div style={{ fontSize: 13, color: "var(--ha-secondary-text)" }}>
                  {spool.color_name} &middot; {spool.packaging} &middot;{" "}
                  <span style={{ fontFamily: "monospace", fontSize: 12 }}>{spool.uid}</span>
                </div>
                {spool.nozzle_temp_min && spool.nozzle_temp_max && (
                  <div style={{ fontSize: 12, color: "var(--ha-secondary-text)" }}>
                    Nozzle: {spool.nozzle_temp_min}-{spool.nozzle_temp_max}&deg;C
                    {spool.bed_temp ? ` | Bed: ${spool.bed_temp}°C` : ""}
                  </div>
                )}
              </div>
            </div>

            {/* Tray picker */}
            <div style={{ margin: "12px 0 8px", fontWeight: 500, fontSize: 13 }}>
              Select AMS tray:
            </div>
            {trays.length === 0 ? (
              <p style={infoText}>No AMS trays found</p>
            ) : (
              <div style={trayList}>
                {trays.map((t) => (
                  <label key={t.entity_id} style={trayRow(selectedTray === t.entity_id)}>
                    <input
                      type="radio"
                      name="tray"
                      checked={selectedTray === t.entity_id}
                      onChange={() => setSelectedTray(t.entity_id)}
                    />
                    <span style={{ flex: 1 }}>{t.location_label || t.entity_id}</span>
                    {t.loaded && t.material && (
                      <span style={{ fontSize: 11, color: "var(--ha-secondary-text)" }}>
                        {t.material}
                      </span>
                    )}
                  </label>
                ))}
              </div>
            )}

            {/* Push to printer */}
            <label style={checkboxRow}>
              <input
                type="checkbox"
                checked={pushToPrinter}
                onChange={(e) => setPushToPrinter(e.target.checked)}
              />
              <span style={{ fontSize: 13 }}>Also update the printer&apos;s AMS display</span>
            </label>
            <div style={{ fontSize: 11, color: "var(--ha-secondary-text)", marginLeft: 24, marginBottom: 8 }}>
              Requires LAN mode. Does not work in Cloud-only mode.
            </div>

            {/* Result */}
            {result && (
              <div style={{ ...resultBox, background: result.ok ? "#e8f5e9" : "#ffebee", color: result.ok ? "#2e7d32" : "#c62828" }}>
                {result.msg}
              </div>
            )}
          </>
        )}

        {/* Actions */}
        <div style={footer}>
          <button onClick={onClose} style={cancelBtn}>
            {result?.ok ? "Done" : "Cancel"}
          </button>
          {spool && spool.status === "in_stock" && !result?.ok && (
            <button
              onClick={handleAssign}
              disabled={!selectedTray || assigning}
              style={{
                ...assignBtn,
                opacity: !selectedTray || assigning ? 0.5 : 1,
              }}
            >
              {assigning ? "Assigning..." : "Assign to Tray"}
            </button>
          )}
        </div>
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
  width: "min(420px, 90vw)", maxHeight: "85vh", overflowY: "auto",
  boxShadow: "0 8px 32px rgba(0,0,0,0.2)",
};
const title: React.CSSProperties = {
  margin: "0 0 16px", fontSize: 18, fontWeight: 600,
  color: "var(--ha-primary-text)",
};
const spoolInfo: React.CSSProperties = {
  display: "flex", gap: 12, alignItems: "center",
  padding: 12, borderRadius: 8,
  background: "rgba(0,0,0,0.03)", marginBottom: 12,
};
const trayList: React.CSSProperties = {
  display: "flex", flexDirection: "column", gap: 4,
  maxHeight: 200, overflowY: "auto", marginBottom: 12,
};
const trayRow = (selected: boolean): React.CSSProperties => ({
  display: "flex", alignItems: "center", gap: 8,
  padding: "8px 10px", borderRadius: 6, cursor: "pointer",
  background: selected ? "var(--ha-primary-color-light, #e3f2fd)" : "transparent",
  border: `1px solid ${selected ? "var(--ha-primary-color, #1976d2)" : "var(--ha-divider, #e0e0e0)"}`,
  fontSize: 13,
});
const checkboxRow: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 8,
  cursor: "pointer", marginTop: 8,
};
const resultBox: React.CSSProperties = {
  padding: "8px 12px", borderRadius: 6, fontSize: 13,
  marginTop: 8,
};
const infoText: React.CSSProperties = {
  fontSize: 13, color: "var(--ha-secondary-text)", padding: "8px 0",
};
const errorText: React.CSSProperties = {
  fontSize: 13, color: "var(--ha-error, #c62828)", padding: "8px 0",
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
const assignBtn: React.CSSProperties = {
  padding: "8px 20px", border: "none", borderRadius: 6,
  background: "var(--ha-primary-color, #1976d2)", color: "#fff",
  cursor: "pointer", fontSize: 13, fontWeight: 600,
};
