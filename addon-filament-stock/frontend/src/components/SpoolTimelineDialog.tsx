import { useEffect, useState } from "react";
import { SpoolEvent, fetchSpoolEvents } from "../api";

interface Props {
  uid: string;
  onClose: () => void;
}

const EVENT_META: Record<string, { label: string; icon: string; color: string }> = {
  created: { label: "Created", icon: "+", color: "#2e7d32" },
  assigned: { label: "Assigned to tray", icon: "→", color: "#1565c0" },
  unassigned: { label: "Returned to stock", icon: "↩", color: "#f57c00" },
  emptied: { label: "Marked empty", icon: "✕", color: "#999" },
  deleted: { label: "Deleted", icon: "🗑", color: "#c62828" },
};

function formatTs(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, {
    month: "short", day: "numeric", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

export default function SpoolTimelineDialog({ uid, onClose }: Props) {
  const [events, setEvents] = useState<SpoolEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchSpoolEvents(uid)
      .then((e) => { if (!cancelled) setEvents(e); })
      .catch((err) => { if (!cancelled) setError(err.message); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [uid]);

  return (
    <div style={overlay} onClick={onClose}>
      <div style={dialog} onClick={(e) => e.stopPropagation()}>
        <div style={header}>
          <div>
            <h3 style={title}>Spool Timeline</h3>
            <span style={subtitle}>{uid}</span>
          </div>
          <button onClick={onClose} style={closeBtn} aria-label="Close">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <div style={body}>
          {loading && <p style={infoText}>Loading...</p>}
          {error && <p style={errorText}>{error}</p>}
          {!loading && events.length === 0 && <p style={infoText}>No events recorded yet.</p>}

          {events.map((ev, i) => {
            const meta = EVENT_META[ev.event_type] ?? { label: ev.event_type, icon: "•", color: "#666" };
            const isLast = i === events.length - 1;
            const detailStr = ev.details?.tray
              ? ev.details.tray
              : ev.details?.packaging
              ? ev.details.packaging
              : null;

            return (
              <div key={ev.id} style={eventRow}>
                <div style={timelineCol}>
                  <div style={{ ...dot, background: meta.color }}>{meta.icon}</div>
                  {!isLast && <div style={line} />}
                </div>
                <div style={eventContent}>
                  <span style={{ fontWeight: 600, fontSize: 13, color: meta.color }}>
                    {meta.label}
                  </span>
                  {detailStr && (
                    <span style={detailPill}>{detailStr}</span>
                  )}
                  <span style={tsText}>{formatTs(ev.timestamp)}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

const overlay: React.CSSProperties = {
  position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)",
  display: "flex", alignItems: "center", justifyContent: "center",
  zIndex: 1100,
};
const dialog: React.CSSProperties = {
  background: "var(--ha-card-bg, #fff)", borderRadius: 12, padding: 0,
  width: "min(380px, 90vw)", maxHeight: "80vh", overflowY: "auto",
  boxShadow: "0 8px 32px rgba(0,0,0,0.25)",
};
const header: React.CSSProperties = {
  display: "flex", justifyContent: "space-between", alignItems: "center",
  padding: "14px 16px", borderBottom: "1px solid var(--ha-divider, #e0e0e0)",
};
const title: React.CSSProperties = {
  margin: 0, fontSize: 16, fontWeight: 600, color: "var(--ha-primary-text)",
};
const subtitle: React.CSSProperties = {
  fontSize: 12, fontFamily: "monospace", color: "var(--ha-secondary-text)",
};
const closeBtn: React.CSSProperties = {
  background: "none", border: "none", color: "var(--ha-secondary-text)",
  width: 32, height: 32, display: "flex", alignItems: "center",
  justifyContent: "center", borderRadius: "50%", cursor: "pointer",
};
const body: React.CSSProperties = {
  padding: "16px 20px 20px",
};
const infoText: React.CSSProperties = {
  fontSize: 13, color: "var(--ha-secondary-text)", textAlign: "center",
};
const errorText: React.CSSProperties = {
  fontSize: 13, color: "var(--ha-error, #c62828)", textAlign: "center",
};
const eventRow: React.CSSProperties = {
  display: "flex", gap: 12, minHeight: 48,
};
const timelineCol: React.CSSProperties = {
  display: "flex", flexDirection: "column", alignItems: "center",
  width: 28, flexShrink: 0,
};
const dot: React.CSSProperties = {
  width: 24, height: 24, borderRadius: "50%",
  display: "flex", alignItems: "center", justifyContent: "center",
  fontSize: 12, color: "#fff", fontWeight: 700, flexShrink: 0,
};
const line: React.CSSProperties = {
  width: 2, flex: 1, background: "var(--ha-divider, #e0e0e0)",
  margin: "4px 0",
};
const eventContent: React.CSSProperties = {
  display: "flex", flexDirection: "column", gap: 2,
  paddingBottom: 12,
};
const detailPill: React.CSSProperties = {
  fontSize: 11, color: "var(--ha-secondary-text)",
  background: "rgba(0,0,0,0.05)", padding: "1px 8px",
  borderRadius: 4, alignSelf: "flex-start",
};
const tsText: React.CSSProperties = {
  fontSize: 11, color: "var(--ha-secondary-text)",
};
