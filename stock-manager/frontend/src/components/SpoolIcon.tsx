import { darkenHex, normalizeHex } from "../colorVisual";

/** User-provided spool silhouette (public/spool-silhouette.png), tinted per filament color */
const SPOOL_MASK = "/spool-silhouette.png";

type Props = {
  colorHex: string;
  size?: number;
  /** Show ×N badge when > 1 */
  count?: number;
  muted?: boolean;
};

function spoolMaskStyle(fill: string, size: number): React.CSSProperties {
  return {
    width: size,
    height: size,
    backgroundColor: fill,
    WebkitMaskImage: `url(${SPOOL_MASK})`,
    maskImage: `url(${SPOOL_MASK})`,
    WebkitMaskSize: "contain",
    maskSize: "contain",
    WebkitMaskRepeat: "no-repeat",
    maskRepeat: "no-repeat",
    WebkitMaskPosition: "center",
    maskPosition: "center",
  };
}

export function SpoolIcon({ colorHex, size = 36, count, muted = false }: Props) {
  const fill = normalizeHex(colorHex);
  const rim = darkenHex(fill, 0.28);
  const opacity = muted ? 0.5 : 1;

  return (
    <div
      style={{
        position: "relative",
        width: size,
        height: size,
        flexShrink: 0,
        opacity,
        filter: muted ? "grayscale(0.35)" : undefined,
      }}
      title={count && count > 1 ? `${count} spools` : undefined}
      aria-hidden
    >
      {/* subtle darker “rim” behind */}
      <div
        style={{
          ...spoolMaskStyle(rim, size),
          position: "absolute",
          left: 0,
          top: 1,
          transform: "scale(1.06)",
          opacity: 0.85,
        }}
      />
      <div
        style={{
          ...spoolMaskStyle(fill, size),
          position: "relative",
          filter: "drop-shadow(0 1px 2px rgba(0,0,0,0.2))",
        }}
      />
      {count !== undefined && count > 1 && (
        <span
          style={{
            position: "absolute",
            right: -4,
            bottom: -2,
            fontSize: 10,
            fontWeight: 700,
            lineHeight: 1,
            padding: "2px 5px",
            borderRadius: 8,
            background: "var(--ha-primary-text)",
            color: "#fff",
            boxShadow: "0 1px 3px rgba(0,0,0,0.25)",
            zIndex: 2,
          }}
        >
          ×{count}
        </span>
      )}
    </div>
  );
}

/** One spool + ×N badge (same as summary totals) */
export function SpoolStack({ colorHex, count, size = 32 }: { colorHex: string; count: number; size?: number }) {
  const n = Math.max(count, 1);
  return <SpoolIcon colorHex={colorHex} size={size} count={n > 1 ? n : undefined} />;
}
