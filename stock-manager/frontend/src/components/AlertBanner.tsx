import { Alert } from "../api";

interface Props { alerts: Alert[]; }

export default function AlertBanner({ alerts }: Props) {
  return (
    <div style={banner}>
      <div style={iconWrap}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="var(--ha-error)">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
        </svg>
      </div>
      <div style={{ flex: 1 }}>
        <p style={title}>Low Stock Alert</p>
        <p style={body}>
          {alerts.map((a, i) => (
            <span key={`${a.filament_id}-${a.color_stock_id}`}>
              <strong style={{ color: "var(--ha-primary-text)" }}>{a.brand} {a.material} {a.color_name}</strong>
              <span style={{ color: "var(--ha-secondary-text)", marginLeft: 3 }}>({a.current_stock} left)</span>
              {i < alerts.length - 1 && <span style={{ margin: "0 5px", color: "var(--ha-disabled-text)" }}>·</span>}
            </span>
          ))}
        </p>
      </div>
      <span style={badge}>{alerts.length}</span>
    </div>
  );
}

const banner: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 10,
  padding: "10px 14px",
  background: "var(--ha-error-bg)",
  border: "1px solid rgba(244,67,54,0.18)",
  borderLeft: "3px solid var(--ha-error)",
  borderRadius: "var(--ha-card-radius)",
  marginBottom: 12,
};
const iconWrap: React.CSSProperties = {
  width: 30, height: 30,
  display: "flex", alignItems: "center", justifyContent: "center",
  background: "rgba(244,67,54,0.15)",
  borderRadius: "50%", flexShrink: 0,
};
const title: React.CSSProperties = {
  fontSize: 11, fontWeight: 600, color: "var(--ha-error)",
  textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 2,
};
const body: React.CSSProperties = {
  fontSize: 12, color: "var(--ha-secondary-text)", lineHeight: 1.5,
};
const badge: React.CSSProperties = {
  background: "var(--ha-error)", color: "#fff",
  fontSize: 11, fontWeight: 700,
  padding: "2px 7px", borderRadius: 10,
  minWidth: 20, textAlign: "center", flexShrink: 0,
};
