import { Alert } from "../api";

interface Props {
  alerts: Alert[];
}

export default function AlertBanner({ alerts }: Props) {
  return (
    <div style={bannerStyle}>
      <span style={{ fontWeight: 600 }}>Low Stock Warning</span>
      <span style={{ opacity: 0.9 }}>
        {alerts.map((a) => `${a.brand} ${a.material} (${a.current_stock} left)`).join(" | ")}
      </span>
    </div>
  );
}

const bannerStyle: React.CSSProperties = {
  background: "linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)",
  color: "#fff",
  padding: "0.8rem 1.2rem",
  borderRadius: "10px",
  marginBottom: "1.5rem",
  display: "flex",
  gap: "1rem",
  alignItems: "center",
  fontSize: "0.9rem",
};
