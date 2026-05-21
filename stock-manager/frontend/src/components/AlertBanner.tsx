import { Alert, StapleAlertIgnore } from "../api";

interface Props {
  alerts: Alert[];
  ignores: StapleAlertIgnore[];
  onIgnore: (filamentType: string, colorName: string) => Promise<void>;
  onUnignore: (ignoreId: number) => Promise<void>;
}

export default function AlertBanner({ alerts, ignores, onIgnore, onUnignore }: Props) {
  return (
    <div style={{ marginBottom: 12 }}>
      {alerts.length > 0 && (
        <div style={banner}>
          <div style={iconWrap}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="var(--ha-error)">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
            </svg>
          </div>
          <div style={{ flex: 1 }}>
            <p style={title}>Low Stock Alert</p>
            <div style={alertList}>
              {alerts.map((a) => (
                <div key={`${a.filament_id}-${a.color_stock_id}`} style={alertRow}>
                  <span>
                    <strong style={{ color: "var(--ha-primary-text)" }}>
                      {a.brand} {a.material} {a.color_name}
                    </strong>
                    <span style={{ color: "var(--ha-secondary-text)", marginLeft: 6 }}>
                      ({a.current_stock} left)
                    </span>
                  </span>
                  <button
                    type="button"
                    style={ignoreBtn}
                    title={`Ignore all ${a.filament_type} ${a.color_name} low-stock alerts`}
                    onClick={() => onIgnore(a.filament_type, a.color_name)}
                  >
                    Ignore {a.filament_type} {a.color_name}
                  </button>
                </div>
              ))}
            </div>
          </div>
          <span style={badge}>{alerts.length}</span>
        </div>
      )}

      {ignores.length > 0 && (
        <div style={ignoredWrap}>
          <p style={ignoredTitle}>Ignored staples (no alerts)</p>
          <div style={ignoredList}>
            {ignores.map((ig) => (
              <span key={ig.id} style={ignoredChip}>
                {ig.filament_type} {ig.color_name}
                <button
                  type="button"
                  style={unignoreBtn}
                  title="Resume low-stock alerts"
                  onClick={() => onUnignore(ig.id)}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

const banner: React.CSSProperties = {
  display: "flex", alignItems: "flex-start", gap: 10,
  padding: "10px 14px",
  background: "var(--ha-error-bg)",
  border: "1px solid rgba(244,67,54,0.18)",
  borderLeft: "3px solid var(--ha-error)",
  borderRadius: "var(--ha-card-radius)",
};
const iconWrap: React.CSSProperties = {
  width: 30, height: 30,
  display: "flex", alignItems: "center", justifyContent: "center",
  background: "rgba(244,67,54,0.15)",
  borderRadius: "50%", flexShrink: 0, marginTop: 2,
};
const title: React.CSSProperties = {
  fontSize: 11, fontWeight: 600, color: "var(--ha-error)",
  textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 6,
};
const alertList: React.CSSProperties = {
  display: "flex", flexDirection: "column", gap: 8,
};
const alertRow: React.CSSProperties = {
  display: "flex", flexWrap: "wrap", alignItems: "center", gap: 8,
  fontSize: 12, lineHeight: 1.4,
};
const ignoreBtn: React.CSSProperties = {
  fontSize: 10, padding: "3px 8px", borderRadius: 10,
  border: "1px solid rgba(244,67,54,0.35)",
  background: "rgba(255,255,255,0.06)",
  color: "var(--ha-error)",
  cursor: "pointer", fontWeight: 500,
};
const badge: React.CSSProperties = {
  background: "var(--ha-error)", color: "#fff",
  fontSize: 11, fontWeight: 700,
  padding: "2px 7px", borderRadius: 10,
  minWidth: 20, textAlign: "center", flexShrink: 0,
};
const ignoredWrap: React.CSSProperties = {
  marginTop: 8, padding: "8px 12px",
  background: "var(--ha-surface-lower)",
  borderRadius: "var(--ha-card-radius)",
  border: "1px solid var(--ha-divider)",
};
const ignoredTitle: React.CSSProperties = {
  fontSize: 10, fontWeight: 600, color: "var(--ha-secondary-text)",
  textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 6,
};
const ignoredList: React.CSSProperties = {
  display: "flex", flexWrap: "wrap", gap: 6,
};
const ignoredChip: React.CSSProperties = {
  display: "inline-flex", alignItems: "center", gap: 4,
  fontSize: 11, padding: "3px 8px", borderRadius: 10,
  background: "var(--ha-card-background)",
  color: "var(--ha-secondary-text)",
};
const unignoreBtn: React.CSSProperties = {
  border: "none", background: "none", cursor: "pointer",
  color: "var(--ha-secondary-text)", fontSize: 14, lineHeight: 1, padding: 0,
};
