interface Props {
  onClick: () => void;
  title?: string;
  disabled?: boolean;
}

export default function TrashIconButton({ onClick, title = "Delete", disabled }: Props) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      style={btn}
      title={title}
      aria-label={title}
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="3 6 5 6 21 6" />
        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
      </svg>
    </button>
  );
}

const btn: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  width: 28,
  height: 28,
  padding: 0,
  flexShrink: 0,
  background: "rgba(0,0,0,0.05)",
  border: "1px solid var(--ha-divider)",
  borderRadius: 6,
  color: "var(--ha-secondary-text)",
  cursor: "pointer",
};
