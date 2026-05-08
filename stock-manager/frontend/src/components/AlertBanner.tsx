import { Alert } from "../api";

interface Props {
  alerts: Alert[];
}

export default function AlertBanner({ alerts }: Props) {
  return (
    <div style={bannerStyle}>
      <div style={iconWrap}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
          <line x1="12" y1="9" x2="12" y2="13" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
      </div>
      <div style={{ flex: 1 }}>
        <p style={alertTitle}>Low Stock Alert</p>
        <p style={alertBody}>
          {alerts.map((a, i) => (
            <span key={a.filament_id}>
              <strong>{a.brand} {a.material}</strong>
              <span style={{ opacity: 0.7 }}> ({a.current_stock} left)</span>
              {i < alerts.length - 1 && <span style={{ margin: "0 0.4rem", opacity: 0.3 }}>&bull;</span>}
            </span>
          ))}
        </p>
      </div>
      <span style={countBadge}>{alerts.length}</span>
    </div>
  );
}

const bannerStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: "0.8rem",
  padding: "0.9rem 1.2rem",
  background: "var(--danger-subtle)",
  border: "1px solid rgba(239, 68, 68, 0.2)",
  borderRadius: "var(--radius-lg)",
  marginBottom: "1.5rem",
};

const iconWrap: React.CSSProperties = {
  width: "36px",
  height: "36px",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  background: "rgba(239, 68, 68, 0.15)",
  borderRadius: "var(--radius-sm)",
  color: "var(--danger)",
  flexShrink: 0,
};

const alertTitle: React.CSSProperties = {
  fontSize: "0.82rem",
  fontWeight: 600,
  color: "var(--danger)",
  marginBottom: "2px",
};

const alertBody: React.CSSProperties = {
  fontSize: "0.8rem",
  color: "var(--text-secondary)",
  lineHeight: 1.5,
};

const countBadge: React.CSSProperties = {
  background: "var(--danger)",
  color: "#fff",
  fontSize: "0.72rem",
  fontWeight: 700,
  padding: "0.2rem 0.5rem",
  borderRadius: "10px",
  minWidth: "22px",
  textAlign: "center",
};
