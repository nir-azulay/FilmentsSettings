import { useState } from "react";
import { seedSampleFilamentsNow } from "../api";

/** Friendly first-run prompt shown when the filament grid is empty.
 *
 *  Three CTAs:
 *    1. "Add your first filament" -- opens the Add dialog (parent owns it).
 *    2. "Load our sample list"    -- POSTs to /api/seed-now and refreshes.
 *    3. Link to the project README for docs.
 *
 *  We render *only* when there are zero filaments, so a user who deletes
 *  every row sees this card the moment the list empties (helpful re-entry
 *  point), not just on a literal first launch.
 */
interface Props {
  onAddFilament: () => void;
  /** Called after a successful seed so the parent can refetch the list. */
  onSeeded: () => void;
}

export default function EmptyState({ onAddFilament, onSeeded }: Props) {
  const [seeding, setSeeding] = useState(false);
  const [feedback, setFeedback] = useState<{ ok: boolean; text: string } | null>(null);

  async function handleSeed() {
    setSeeding(true);
    setFeedback(null);
    try {
      const result = await seedSampleFilamentsNow();
      const total = result.added + result.skipped_existing;
      setFeedback({
        ok: true,
        text:
          result.added > 0
            ? `Added ${result.added} sample filament${result.added === 1 ? "" : "s"}.`
            : `All ${total} samples were already in your stock.`,
      });
      onSeeded();
    } catch (exc) {
      setFeedback({ ok: false, text: `Couldn't seed: ${(exc as Error).message}` });
    } finally {
      setSeeding(false);
    }
  }

  return (
    <section className="ha-card" style={wrap}>
      <div style={iconWrap}>
        <svg
          width="56"
          height="56"
          viewBox="0 0 24 24"
          fill="none"
          stroke="var(--ha-primary-color)"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <ellipse cx="12" cy="5" rx="9" ry="3" />
          <path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5" />
          <path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3" />
        </svg>
      </div>
      <h2 style={title}>Your filament stock is empty</h2>
      <p style={subtitle}>
        Welcome! Get started by adding the filaments you already own, or
        load our curated sample list to see how the dashboard looks.
      </p>

      <div style={ctaRow}>
        <button type="button" onClick={onAddFilament} style={primaryBtn}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Add your first filament
        </button>
        <button
          type="button"
          onClick={() => void handleSeed()}
          disabled={seeding}
          style={secondaryBtn}
        >
          {seeding ? "Loading…" : "Load sample list"}
        </button>
      </div>

      {feedback && (
        <p
          style={{
            ...feedbackText,
            color: feedback.ok ? "var(--ha-success, #2e7d32)" : "var(--ha-error, #c62828)",
          }}
        >
          {feedback.text}
        </p>
      )}

      <p style={footerHint}>
        Tip: the AMS panel above auto-detects spools loaded in your Bambu
        printer once the <code>ha-bambulab</code> integration is set up.
        You can also keep stock manually and use that list for shopping
        and low-stock alerts.
      </p>
    </section>
  );
}

// ── styles ────────────────────────────────────────────────────────────────

const wrap: React.CSSProperties = {
  padding: "32px 24px",
  textAlign: "center",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  gap: 12,
  maxWidth: 560,
  margin: "24px auto",
};

const iconWrap: React.CSSProperties = {
  width: 80,
  height: 80,
  borderRadius: "50%",
  background: "var(--ha-info-bg, rgba(3, 169, 244, 0.1))",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  marginBottom: 4,
};

const title: React.CSSProperties = {
  fontSize: 20,
  fontWeight: 500,
  color: "var(--ha-primary-text)",
  margin: 0,
};

const subtitle: React.CSSProperties = {
  fontSize: 13,
  color: "var(--ha-secondary-text)",
  margin: 0,
  lineHeight: 1.5,
  maxWidth: 440,
};

const ctaRow: React.CSSProperties = {
  display: "flex",
  gap: 12,
  marginTop: 8,
  flexWrap: "wrap",
  justifyContent: "center",
};

const primaryBtn: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 6,
  padding: "10px 18px",
  background: "var(--ha-primary-color)",
  color: "#fff",
  border: "none",
  borderRadius: "var(--ha-btn-radius, 4px)",
  fontSize: 13,
  fontWeight: 500,
  cursor: "pointer",
};

const secondaryBtn: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 6,
  padding: "10px 18px",
  background: "none",
  color: "var(--ha-primary-color)",
  border: "1px solid var(--ha-primary-color)",
  borderRadius: "var(--ha-btn-radius, 4px)",
  fontSize: 13,
  fontWeight: 500,
  cursor: "pointer",
};

const feedbackText: React.CSSProperties = {
  fontSize: 12,
  margin: "4px 0 0",
};

const footerHint: React.CSSProperties = {
  fontSize: 12,
  color: "var(--ha-secondary-text)",
  marginTop: 16,
  paddingTop: 16,
  borderTop: "1px dashed var(--ha-divider, rgba(0, 0, 0, 0.08))",
  maxWidth: 480,
  lineHeight: 1.5,
};
