import { ReactNode } from "react";

interface Props {
  title: string;
  children: ReactNode;
  warning: string;
  onCancel: () => void;
  onConfirm: () => void;
  confirming?: boolean;
}

/** Shared “Are you sure?” dialog — same look for filament and color deletes. */
export default function ConfirmDeleteModal({
  title,
  children,
  warning,
  onCancel,
  onConfirm,
  confirming,
}: Props) {
  return (
    <div style={overlay} role="dialog" aria-modal="true" aria-labelledby="confirm-delete-title">
      <div style={panel} onClick={(e) => e.stopPropagation()}>
        <h2 id="confirm-delete-title" style={dialogTitle}>
          {title}
        </h2>
        <div style={body}>{children}</div>
        <p style={warningText}>{warning}</p>
        <div style={actions}>
          <button type="button" onClick={onCancel} disabled={confirming} style={cancelBtn}>
            Cancel
          </button>
          <button type="button" onClick={onConfirm} disabled={confirming} style={confirmBtn}>
            {confirming ? "Deleting…" : "Yes, delete"}
          </button>
        </div>
      </div>
    </div>
  );
}

const overlay: React.CSSProperties = {
  position: "fixed",
  inset: 0,
  zIndex: 2100,
  background: "var(--ha-overlay-bg)",
  backdropFilter: "blur(3px)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: 20,
};
const panel: React.CSSProperties = {
  width: "100%",
  maxWidth: 400,
  background: "var(--ha-card-bg)",
  borderRadius: "var(--ha-card-radius)",
  padding: "20px 22px",
  boxShadow: "var(--ha-dialog-shadow)",
};
const dialogTitle: React.CSSProperties = {
  margin: 0,
  fontSize: 18,
  fontWeight: 600,
  color: "var(--ha-primary-text)",
};
const body: React.CSSProperties = {
  marginTop: 12,
  fontSize: 14,
  lineHeight: 1.5,
  color: "var(--ha-secondary-text)",
};
const warningText: React.CSSProperties = {
  margin: "10px 0 0",
  fontSize: 13,
  lineHeight: 1.45,
  color: "var(--ha-error)",
};
const actions: React.CSSProperties = {
  display: "flex",
  gap: 10,
  marginTop: 20,
  justifyContent: "flex-end",
};
const cancelBtn: React.CSSProperties = {
  padding: "10px 16px",
  borderRadius: 8,
  border: "1px solid var(--ha-divider)",
  background: "var(--ha-surface-lower)",
  color: "var(--ha-primary-text)",
  fontSize: 14,
  fontWeight: 500,
  cursor: "pointer",
};
const confirmBtn: React.CSSProperties = {
  padding: "10px 16px",
  borderRadius: 8,
  border: "none",
  background: "var(--ha-error)",
  color: "#fff",
  fontSize: 14,
  fontWeight: 600,
  cursor: "pointer",
};
