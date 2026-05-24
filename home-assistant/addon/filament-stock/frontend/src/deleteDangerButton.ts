import type { CSSProperties } from "react";

/** Same red “Delete” control as on the filament card footer. */
export const deleteDangerBtn: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  padding: "7px 12px",
  background: "var(--ha-error-bg)",
  color: "var(--ha-error)",
  border: "1px solid rgba(244,67,54,0.25)",
  borderRadius: 4,
  fontSize: 12,
  fontWeight: 500,
  cursor: "pointer",
  whiteSpace: "nowrap",
  flexShrink: 0,
};
