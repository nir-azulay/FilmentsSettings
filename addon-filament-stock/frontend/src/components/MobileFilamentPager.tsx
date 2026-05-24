import { useCallback, useRef, useState } from "react";
import { Filament } from "../api";
import FilamentCard from "./FilamentCard";

interface Props {
  filaments: Filament[];
  staplePools: Map<string, number>;
  ignoredStaples: Set<string>;
  onManageStock: (f: Filament) => void;
  onUpdate: () => Promise<void>;
  onRequestDeleteFilament: (f: Filament) => void;
}

export default function MobileFilamentPager({
  filaments,
  staplePools,
  ignoredStaples,
  onManageStock,
  onUpdate,
  onRequestDeleteFilament,
}: Props) {
  const trackRef = useRef<HTMLDivElement>(null);
  const [index, setIndex] = useState(0);

  const syncIndexFromScroll = useCallback(() => {
    const el = trackRef.current;
    if (!el || filaments.length === 0) return;
    const w = el.clientWidth;
    if (w <= 0) return;
    const i = Math.round(el.scrollLeft / w);
    setIndex(Math.max(0, Math.min(i, filaments.length - 1)));
  }, [filaments.length]);

  const goTo = (i: number) => {
    const el = trackRef.current;
    if (!el) return;
    const next = Math.max(0, Math.min(i, filaments.length - 1));
    el.scrollTo({ left: next * el.clientWidth, behavior: "smooth" });
    setIndex(next);
  };

  if (filaments.length === 0) {
    return (
      <p style={{ textAlign: "center", color: "var(--ha-secondary-text)", padding: 48 }}>
        No filaments in this filter.
      </p>
    );
  }

  const current = filaments[index];

  return (
    <div className="filament-mobile-pager">
      <div className="filament-mobile-pager__meta">
        <span style={counter}>
          {index + 1} / {filaments.length}
        </span>
        <span style={hint}>Swipe ← →</span>
      </div>

      <div
        ref={trackRef}
        className="filament-mobile-carousel"
        onScroll={syncIndexFromScroll}
      >
        {filaments.map((f) => (
          <div key={f.id} className="filament-mobile-slide">
            <FilamentCard
              filament={f}
              staplePools={staplePools}
              ignoredStaples={ignoredStaples}
              onManageStock={() => onManageStock(f)}
              onUpdate={onUpdate}
              onRequestDeleteFilament={() => onRequestDeleteFilament(f)}
            />
          </div>
        ))}
      </div>

      <div className="filament-mobile-pager__nav">
        <button type="button" style={navBtn} disabled={index <= 0} onClick={() => goTo(index - 1)}>
          ← Prev
        </button>
        {filaments.length <= 12 ? (
          <div style={dotsWrap}>
            {filaments.map((f, i) => (
              <button
                key={f.id}
                type="button"
                aria-label={`Go to ${f.brand} ${f.material}`}
                style={{ ...dot, ...(i === index ? dotActive : {}) }}
                onClick={() => goTo(i)}
              />
            ))}
          </div>
        ) : (
          <span style={{ flex: 1, textAlign: "center", fontSize: 12, color: "var(--ha-secondary-text)" }}>
            {current?.brand} {current?.material}
          </span>
        )}
        <button
          type="button"
          style={navBtn}
          disabled={index >= filaments.length - 1}
          onClick={() => goTo(index + 1)}
        >
          Next →
        </button>
      </div>

      {current && filaments.length <= 12 && (
        <p style={caption}>
          {current.brand} · {current.material}
        </p>
      )}
    </div>
  );
}

const counter: React.CSSProperties = {
  fontSize: 13,
  fontWeight: 600,
  color: "var(--ha-primary-text)",
};
const hint: React.CSSProperties = {
  fontSize: 11,
  color: "var(--ha-disabled-text)",
};
const navBtn: React.CSSProperties = {
  padding: "8px 14px",
  borderRadius: 8,
  border: "1px solid var(--ha-divider)",
  background: "var(--ha-card-bg)",
  color: "var(--ha-primary-text)",
  fontSize: 13,
  fontWeight: 500,
  cursor: "pointer",
};
const dotsWrap: React.CSSProperties = {
  display: "flex",
  gap: 6,
  flexWrap: "wrap",
  justifyContent: "center",
  flex: 1,
  maxWidth: "50%",
};
const dot: React.CSSProperties = {
  width: 7,
  height: 7,
  borderRadius: "50%",
  border: "none",
  padding: 0,
  background: "var(--ha-surface-lower)",
  cursor: "pointer",
};
const dotActive: React.CSSProperties = {
  background: "var(--ha-primary-color)",
  transform: "scale(1.2)",
};
const caption: React.CSSProperties = {
  textAlign: "center",
  fontSize: 12,
  color: "var(--ha-secondary-text)",
  marginTop: 8,
};
