import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Prediction,
  PredictionsData,
  UsageData,
  fetchPredictions,
  fetchUsageData,
} from "../api";

const COLLAPSE_KEY = "filament_stock_analytics_collapsed";

export default function AnalyticsPanel() {
  const [collapsed, setCollapsed] = useState(
    () => localStorage.getItem(COLLAPSE_KEY) === "1",
  );
  const [period, setPeriod] = useState<"7d" | "30d" | "90d" | "all">("30d");
  const [groupBy, setGroupBy] = useState<"brand" | "material" | "color">("material");
  const [usage, setUsage] = useState<UsageData | null>(null);
  const [predictions, setPredictions] = useState<PredictionsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<"usage" | "predictions">("usage");

  const reload = useCallback(async () => {
    const [u, p] = await Promise.all([
      fetchUsageData(period, groupBy).catch(() => null),
      fetchPredictions().catch(() => null),
    ]);
    setUsage(u);
    setPredictions(p);
  }, [period, groupBy]);

  useEffect(() => {
    if (collapsed) return;
    setLoading(true);
    reload().finally(() => setLoading(false));
  }, [reload, collapsed]);

  const toggleCollapse = () => {
    setCollapsed((prev) => {
      localStorage.setItem(COLLAPSE_KEY, prev ? "0" : "1");
      return !prev;
    });
  };

  const maxGrams = useMemo(() => {
    if (!usage?.groups.length) return 1;
    return Math.max(...usage.groups.map((g) => g.total_grams));
  }, [usage]);

  return (
    <section className="ha-card" style={card}>
      <div style={headerRow} onClick={toggleCollapse} role="button">
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <svg
            width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="var(--ha-primary-text)" strokeWidth="2"
            strokeLinecap="round" strokeLinejoin="round"
            style={{ transform: collapsed ? "rotate(-90deg)" : "rotate(0)", transition: "transform 0.2s" }}
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--ha-primary-color)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 20V10M6 20V14M18 20V4" />
          </svg>
          <h3 style={sectionTitle}>Usage Analytics</h3>
        </div>
      </div>

      {!collapsed && (
        <div style={bodyWrap}>
          {loading && <p style={infoText}>Loading analytics...</p>}

          {!loading && (
            <>
              <div style={tabRow}>
                <button onClick={() => setTab("usage")} style={tab === "usage" ? tabBtnActive : tabBtn}>
                  Consumption
                </button>
                <button onClick={() => setTab("predictions")} style={tab === "predictions" ? tabBtnActive : tabBtn}>
                  Predictions
                </button>
              </div>

              {tab === "usage" && (
                <>
                  <div style={controlsRow}>
                    <div style={filterRow}>
                      {(["7d", "30d", "90d", "all"] as const).map((p) => (
                        <button key={p} onClick={() => setPeriod(p)} style={period === p ? filterBtnActive : filterBtn}>
                          {p === "all" ? "All" : p}
                        </button>
                      ))}
                    </div>
                    <div style={filterRow}>
                      {(["material", "brand", "color"] as const).map((g) => (
                        <button key={g} onClick={() => setGroupBy(g)} style={groupBy === g ? filterBtnActive : filterBtn}>
                          {g.charAt(0).toUpperCase() + g.slice(1)}
                        </button>
                      ))}
                    </div>
                  </div>

                  {!usage || usage.groups.length === 0 ? (
                    <p style={infoText}>No usage data recorded yet. Log usage from the spool overview panel.</p>
                  ) : (
                    <>
                      <div style={totalRow}>
                        <span style={{ fontSize: 24, fontWeight: 700, color: "var(--ha-primary-color)" }}>
                          {Math.round(usage.total_grams)}g
                        </span>
                        <span style={{ fontSize: 12, color: "var(--ha-secondary-text)" }}>
                          total consumed ({period === "all" ? "all time" : `last ${period}`})
                        </span>
                      </div>
                      <div style={chartWrap}>
                        {usage.groups.slice(0, 10).map((g) => (
                          <div key={g.label} style={barRow}>
                            <span style={barLabel}>{g.label}</span>
                            <div style={barTrack}>
                              <div style={{ ...barFill, width: `${Math.max(2, (g.total_grams / maxGrams) * 100)}%` }} />
                            </div>
                            <span style={barValue}>{Math.round(g.total_grams)}g</span>
                          </div>
                        ))}
                      </div>
                    </>
                  )}

                  {usage && usage.timeline.length > 0 && (
                    <div style={{ marginTop: 16 }}>
                      <h4 style={subTitle}>Weekly Trend</h4>
                      <div style={timelineWrap}>
                        {usage.timeline.map((t) => {
                          const maxTl = Math.max(...usage.timeline.map((x) => x.grams));
                          const pct = maxTl > 0 ? (t.grams / maxTl) * 100 : 0;
                          return (
                            <div key={t.week} style={tlBar} title={`${t.week}: ${Math.round(t.grams)}g`}>
                              <div style={{ ...tlBarFill, height: `${Math.max(2, pct)}%` }} />
                              <span style={tlLabel}>{t.week.slice(-3)}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </>
              )}

              {tab === "predictions" && (
                <>
                  {!predictions || predictions.predictions.length === 0 ? (
                    <p style={infoText}>No predictions available. Log some usage data first.</p>
                  ) : (
                    <div style={predictionsList}>
                      {predictions.predictions.map((p) => (
                        <PredictionCard key={p.color_stock_id} prediction={p} />
                      ))}
                    </div>
                  )}
                </>
              )}
            </>
          )}
        </div>
      )}
    </section>
  );
}

function PredictionCard({ prediction: p }: { prediction: Prediction }) {
  const urgent = p.days_remaining < 14;
  const warning = p.days_remaining < 30;
  return (
    <div style={{
      ...predCard,
      borderLeft: `3px solid ${urgent ? "var(--ha-error)" : warning ? "var(--ha-warning)" : "var(--ha-success)"}`,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <div style={{ width: 14, height: 14, borderRadius: 3, background: p.color_hex, flexShrink: 0 }} />
        <span style={{ fontWeight: 600, fontSize: 13 }}>{p.brand} {p.material} - {p.color_name}</span>
      </div>
      <div style={{ display: "flex", gap: 16, marginTop: 6, flexWrap: "wrap" }}>
        <span style={predStat}>
          <strong>{p.days_remaining}</strong> days left
        </span>
        <span style={predStat}>
          {p.daily_rate_grams}g/day
        </span>
        <span style={predStat}>
          {p.available_units} unit{p.available_units !== 1 ? "s" : ""} in stock
        </span>
      </div>
    </div>
  );
}

const card: React.CSSProperties = { marginBottom: 16 };
const headerRow: React.CSSProperties = {
  display: "flex", alignItems: "center", justifyContent: "space-between",
  padding: "14px 20px", cursor: "pointer", userSelect: "none",
};
const sectionTitle: React.CSSProperties = {
  margin: 0, fontSize: 16, fontWeight: 600, color: "var(--ha-primary-text)",
};
const bodyWrap: React.CSSProperties = { padding: "0 20px 16px" };
const infoText: React.CSSProperties = {
  fontSize: 13, color: "var(--ha-secondary-text)", textAlign: "center", padding: "16px 0",
};
const tabRow: React.CSSProperties = {
  display: "flex", gap: 2, marginBottom: 12, padding: 2,
  background: "var(--ha-subtle-bg)", borderRadius: 8, width: "fit-content",
};
const tabBtn: React.CSSProperties = {
  padding: "6px 16px", fontSize: 12, fontWeight: 500,
  background: "transparent", color: "var(--ha-primary-text)",
  border: "none", borderRadius: 6, cursor: "pointer",
};
const tabBtnActive: React.CSSProperties = {
  ...tabBtn, background: "var(--ha-card-bg)", boxShadow: "0 1px 3px rgba(0,0,0,0.12)", fontWeight: 600,
};
const controlsRow: React.CSSProperties = {
  display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 12,
};
const filterRow: React.CSSProperties = {
  display: "flex", gap: 2, padding: 2,
  background: "var(--ha-subtle-bg)", borderRadius: 8,
};
const filterBtn: React.CSSProperties = {
  padding: "4px 10px", fontSize: 11, fontWeight: 500,
  background: "transparent", color: "var(--ha-primary-text)",
  border: "none", borderRadius: 6, cursor: "pointer",
};
const filterBtnActive: React.CSSProperties = {
  ...filterBtn, background: "var(--ha-card-bg)", boxShadow: "0 1px 3px rgba(0,0,0,0.12)", fontWeight: 600,
};
const totalRow: React.CSSProperties = {
  display: "flex", alignItems: "baseline", gap: 8, marginBottom: 12,
};
const chartWrap: React.CSSProperties = {
  display: "flex", flexDirection: "column", gap: 6,
};
const barRow: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 8,
};
const barLabel: React.CSSProperties = {
  fontSize: 12, fontWeight: 500, minWidth: 80, color: "var(--ha-primary-text)",
  overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
};
const barTrack: React.CSSProperties = {
  flex: 1, height: 16, borderRadius: 4, background: "var(--ha-subtle-bg)", overflow: "hidden",
};
const barFill: React.CSSProperties = {
  height: "100%", borderRadius: 4, background: "var(--ha-primary-color)",
  transition: "width 0.3s ease-out",
};
const barValue: React.CSSProperties = {
  fontSize: 11, fontWeight: 600, minWidth: 40, textAlign: "right", color: "var(--ha-secondary-text)",
};
const subTitle: React.CSSProperties = {
  fontSize: 13, fontWeight: 600, color: "var(--ha-primary-text)", marginBottom: 8,
};
const timelineWrap: React.CSSProperties = {
  display: "flex", alignItems: "flex-end", gap: 3, height: 80,
  padding: "0 4px", borderBottom: "1px solid var(--ha-divider)",
};
const tlBar: React.CSSProperties = {
  flex: 1, display: "flex", flexDirection: "column", alignItems: "center",
  justifyContent: "flex-end", height: "100%",
};
const tlBarFill: React.CSSProperties = {
  width: "100%", borderRadius: "3px 3px 0 0", background: "var(--ha-primary-color-light)",
  transition: "height 0.3s ease-out", minHeight: 2,
};
const tlLabel: React.CSSProperties = {
  fontSize: 8, color: "var(--ha-secondary-text)", marginTop: 2,
};
const predictionsList: React.CSSProperties = {
  display: "flex", flexDirection: "column", gap: 6,
};
const predCard: React.CSSProperties = {
  padding: "10px 14px", borderRadius: 8,
  background: "var(--ha-subtle-bg)",
};
const predStat: React.CSSProperties = {
  fontSize: 11, color: "var(--ha-secondary-text)",
};
