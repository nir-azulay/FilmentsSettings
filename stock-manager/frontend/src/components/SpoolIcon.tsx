import { darkenHex, isLightColor, normalizeHex } from "../colorVisual";

type Props = {
  colorHex: string;
  size?: number;
  /** Show ×N badge when > 1 */
  count?: number;
  muted?: boolean;
};

/** Side-view filament spool SVG */
export function SpoolIcon({ colorHex, size = 36, count, muted = false }: Props) {
  const fill = normalizeHex(colorHex);
  const rim = darkenHex(fill, 0.32);
  const hole = muted ? "rgba(0,0,0,0.12)" : "rgba(0,0,0,0.22)";
  const opacity = muted ? 0.55 : 1;

  return (
    <div
      style={{
        position: "relative",
        width: size,
        height: size,
        flexShrink: 0,
        opacity,
        filter: muted ? "grayscale(0.25)" : undefined,
      }}
      title={count && count > 1 ? `${count} spools` : undefined}
    >
      <svg viewBox="0 0 32 40" width={size} height={size} aria-hidden>
        <ellipse cx="16" cy="5" rx="13" ry="4" fill={rim} />
        <path
          d="M4 5 h24 a2 2 0 0 1 2 2 v26 a2 2 0 0 1-2 2 H4 a2 2 0 0 1-2-2 V7 a2 2 0 0 1 2-2z"
          fill={fill}
          stroke={rim}
          strokeWidth="1.2"
        />
        <ellipse cx="16" cy="35" rx="13" ry="4" fill={rim} />
        <ellipse cx="16" cy="20" rx="5" ry="11" fill={hole} />
        <path
          d="M16 9 v22"
          stroke={isLightColor(fill) ? "rgba(0,0,0,0.08)" : "rgba(255,255,255,0.12)"}
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>
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
          }}
        >
          ×{count}
        </span>
      )}
    </div>
  );
}

/** Stacked spools for quantity at a glance (max 4 visible) */
export function SpoolStack({ colorHex, count, size = 28 }: { colorHex: string; count: number; size?: number }) {
  const n = Math.min(Math.max(count, 1), 4);
  const offsets = [
    { left: 0, z: 4 },
    { left: 6, z: 3 },
    { left: 12, z: 2 },
    { left: 18, z: 1 },
  ].slice(0, n);

  return (
    <div style={{ position: "relative", width: size + (n - 1) * 6, height: size, flexShrink: 0 }}>
      {offsets.map((o, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: o.left,
            top: 0,
            zIndex: o.z,
          }}
        >
          <SpoolIcon colorHex={colorHex} size={size - 4} />
        </div>
      ))}
      {count > 4 && (
        <span
          style={{
            position: "absolute",
            right: -6,
            bottom: 0,
            fontSize: 11,
            fontWeight: 700,
            color: "var(--ha-primary-text)",
          }}
        >
          +{count - 4}
        </span>
      )}
    </div>
  );
}
