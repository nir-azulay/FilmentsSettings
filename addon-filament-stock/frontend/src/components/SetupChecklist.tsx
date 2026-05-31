import { useEffect, useState } from "react";
import { HealthCheck, HealthReport, fetchHealth } from "../api";

/** Setup-checklist card shown above the dashboard when /api/health reports
 *  any failing checks. The component is its own data owner: it fetches the
 *  report on mount and re-fetches on demand (via the "Re-check" button).
 *
 *  Display rules:
 *   - All checks ok -> renders nothing (zero footprint for happy installs).
 *   - Any check failing -> sticky card at the top of the page.
 *   - Auto-collapsed if the worst severity is "warn"; auto-expanded if
 *     any check is "error" (because the user actually needs to act).
 */
export default function SetupChecklist() {
  const [report, setReport] = useState<HealthReport | null>(null);
  const [loading, setLoading] = useState(false);
  // null while we wait for the report -- we don't know yet whether to
  // start expanded or collapsed. Set on first report arrival and then
  // controlled by the user.
  const [expanded, setExpanded] = useState<boolean | null>(null);

  const refresh = async () => {
    setLoading(true);
    try {
      const r = await fetchHealth();
      setReport(r);
      if (expanded === null) {
        setExpanded(r.severity === "error");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void refresh();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Nothing to show until we have a report, or if everything passes.
  if (!report || report.ok) return null;

  const failingChecks = report.checks.filter((c) => !c.ok);
  const hasErrors = failingChecks.some((c) => c.severity === "error");
  const headerColor = hasErrors
    ? "var(--ha-error, #db4437)"
    : "var(--ha-warning, #ffa726)";
  const headerBg = hasErrors
    ? "var(--ha-error-bg, rgba(219, 68, 55, 0.08))"
    : "var(--ha-warning-bg, rgba(255, 167, 38, 0.08))";

  return (
    <section
      className="ha-card"
      style={{
        ...wrap,
        borderLeft: `4px solid ${headerColor}`,
      }}
    >
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        style={{ ...headerBtn, background: headerBg }}
        aria-expanded={expanded ?? false}
      >
        <span style={{ ...iconBadge, background: headerColor }}>
          {hasErrors ? "!" : "?"}
        </span>
        <span style={{ display: "flex", flexDirection: "column", alignItems: "flex-start", gap: 2, flex: 1 }}>
          <span style={{ fontWeight: 600, fontSize: 14 }}>
            Setup checklist
          </span>
          <span style={{ fontSize: 12, color: "var(--ha-secondary-text)" }}>
            {report.summary}
          </span>
        </span>
        <span style={{ fontSize: 12, color: "var(--ha-secondary-text)", marginRight: 4 }}>
          {failingChecks.length} of {report.checks.length} failing
        </span>
        <span style={chevron(expanded ?? false)}>▾</span>
      </button>

      {expanded && (
        <div style={body}>
          <ul style={list}>
            {report.checks.map((c) => (
              <CheckRow key={c.id} check={c} />
            ))}
          </ul>
          <div style={footer}>
            <button
              type="button"
              onClick={() => void refresh()}
              disabled={loading}
              style={recheckBtn}
            >
              {loading ? "Re-checking…" : "Re-check now"}
            </button>
            <a
              href="https://github.com/greghesp/ha-bambulab"
              target="_blank"
              rel="noopener noreferrer"
              style={docLink}
            >
              ha-bambulab on GitHub ↗
            </a>
          </div>
        </div>
      )}
    </section>
  );
}

function CheckRow({ check }: { check: HealthCheck }) {
  const isOk = check.ok;
  const isError = check.severity === "error";
  const dotColor = isOk
    ? "var(--ha-success, #43a047)"
    : isError
    ? "var(--ha-error, #db4437)"
    : "var(--ha-warning, #ffa726)";
  const label = isOk ? "OK" : isError ? "ERROR" : "WARN";

  return (
    <li style={row}>
      <span style={{ ...statusDot, background: dotColor }} aria-label={label} title={label} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={rowTitle}>{check.name}</div>
        <div style={rowMsg}>{check.message}</div>
        {!isOk && check.hint && (
          <div style={rowHint}>
            <strong style={{ color: "var(--ha-primary-text)" }}>What to do:</strong>{" "}
            {check.hint}
          </div>
        )}
      </div>
    </li>
  );
}

// ── styles ─────────────────────────────────────────────────────────────────

const wrap: React.CSSProperties = {
  marginBottom: 16,
  padding: 0,
  overflow: "hidden",
};

const headerBtn: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 12,
  width: "100%",
  padding: "12px 16px",
  border: "none",
  cursor: "pointer",
  textAlign: "left",
  color: "var(--ha-primary-text)",
};

const iconBadge: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  width: 28,
  height: 28,
  borderRadius: "50%",
  color: "#fff",
  fontWeight: 700,
  fontSize: 16,
  flexShrink: 0,
};

const chevron = (expanded: boolean): React.CSSProperties => ({
  display: "inline-block",
  transition: "transform 0.15s ease",
  transform: expanded ? "rotate(0deg)" : "rotate(-90deg)",
  fontSize: 14,
  color: "var(--ha-secondary-text)",
});

const body: React.CSSProperties = {
  padding: "12px 16px 16px",
  borderTop: "1px solid var(--ha-divider, rgba(0, 0, 0, 0.08))",
};

const list: React.CSSProperties = {
  listStyle: "none",
  padding: 0,
  margin: 0,
  display: "flex",
  flexDirection: "column",
  gap: 10,
};

const row: React.CSSProperties = {
  display: "flex",
  gap: 10,
  alignItems: "flex-start",
  padding: "8px 10px",
  borderRadius: 6,
  background: "var(--ha-card-bg-subtle, rgba(0, 0, 0, 0.02))",
};

const statusDot: React.CSSProperties = {
  width: 10,
  height: 10,
  borderRadius: "50%",
  marginTop: 6,
  flexShrink: 0,
};

const rowTitle: React.CSSProperties = {
  fontSize: 13,
  fontWeight: 600,
  color: "var(--ha-primary-text)",
};

const rowMsg: React.CSSProperties = {
  fontSize: 12,
  color: "var(--ha-secondary-text)",
  marginTop: 2,
};

const rowHint: React.CSSProperties = {
  fontSize: 12,
  color: "var(--ha-secondary-text)",
  marginTop: 6,
  padding: "6px 8px",
  background: "var(--ha-info-bg, rgba(3, 169, 244, 0.08))",
  borderRadius: 4,
  lineHeight: 1.4,
};

const footer: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  marginTop: 12,
  paddingTop: 10,
  borderTop: "1px dashed var(--ha-divider, rgba(0, 0, 0, 0.08))",
};

const recheckBtn: React.CSSProperties = {
  padding: "6px 12px",
  background: "var(--ha-primary-color)",
  color: "#fff",
  border: "none",
  borderRadius: "var(--ha-btn-radius, 4px)",
  fontSize: 12,
  fontWeight: 500,
  cursor: "pointer",
};

const docLink: React.CSSProperties = {
  fontSize: 12,
  color: "var(--ha-primary-color)",
  textDecoration: "none",
};
