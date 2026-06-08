import { useEffect, useRef, useState } from "react";
import { Html5Qrcode } from "html5-qrcode";

interface Props {
  onScanned: (uid: string) => void;
  onClose: () => void;
}

const SP_RE = /SP-[A-F0-9]{8}/i;

export default function QrScannerDialog({ onScanned, onClose }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const scannerRef = useRef<Html5Qrcode | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(true);
  const handledRef = useRef(false);

  useEffect(() => {
    if (!containerRef.current) return;

    const scanner = new Html5Qrcode("qr-reader");
    scannerRef.current = scanner;

    scanner
      .start(
        { facingMode: "environment" },
        { fps: 10, qrbox: { width: 250, height: 250 } },
        (decoded) => {
          if (handledRef.current) return;
          const match = decoded.match(SP_RE);
          if (match) {
            handledRef.current = true;
            scanner.stop().catch(() => {});
            onScanned(match[0].toUpperCase());
          }
        },
        () => {},
      )
      .then(() => setStarting(false))
      .catch((err) => {
        setStarting(false);
        setError(
          typeof err === "string"
            ? err
            : err?.message || "Camera access denied or unavailable",
        );
      });

    return () => {
      scanner.stop().catch(() => {});
    };
  }, [onScanned]);

  return (
    <div style={overlay} onClick={onClose}>
      <div style={dialog} onClick={(e) => e.stopPropagation()}>
        <div style={header}>
          <h3 style={title}>Scan Spool QR Code</h3>
          <button onClick={onClose} style={closeBtn} aria-label="Close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <div style={scannerWrap}>
          <div id="qr-reader" ref={containerRef} style={{ width: "100%" }} />
        </div>

        {starting && <p style={infoText}>Starting camera...</p>}
        {error && <p style={errorText}>{error}</p>}

        <p style={hint}>
          Point your camera at the QR code on a spool label.
          The spool UID (SP-XXXXXXXX) will be detected automatically.
        </p>
      </div>
    </div>
  );
}

const overlay: React.CSSProperties = {
  position: "fixed", inset: 0, background: "rgba(0,0,0,0.6)",
  display: "flex", alignItems: "center", justifyContent: "center",
  zIndex: 1000,
};
const dialog: React.CSSProperties = {
  background: "var(--ha-card-bg, #fff)", borderRadius: 12, padding: 0,
  width: "min(420px, 92vw)", maxHeight: "90vh", overflowY: "auto",
  boxShadow: "0 8px 32px rgba(0,0,0,0.25)",
};
const header: React.CSSProperties = {
  display: "flex", justifyContent: "space-between", alignItems: "center",
  padding: "14px 16px", borderBottom: "1px solid var(--ha-divider, #e0e0e0)",
};
const title: React.CSSProperties = {
  margin: 0, fontSize: 16, fontWeight: 600, color: "var(--ha-primary-text)",
};
const closeBtn: React.CSSProperties = {
  background: "none", border: "none", color: "var(--ha-secondary-text)",
  width: 32, height: 32, display: "flex", alignItems: "center",
  justifyContent: "center", borderRadius: "50%", cursor: "pointer",
};
const scannerWrap: React.CSSProperties = {
  padding: "12px 16px 0",
};
const infoText: React.CSSProperties = {
  fontSize: 13, color: "var(--ha-secondary-text)", textAlign: "center",
  padding: "8px 16px",
};
const errorText: React.CSSProperties = {
  fontSize: 13, color: "var(--ha-error, #c62828)", textAlign: "center",
  padding: "8px 16px",
};
const hint: React.CSSProperties = {
  fontSize: 12, color: "var(--ha-secondary-text)", textAlign: "center",
  padding: "8px 16px 16px", margin: 0, lineHeight: 1.5,
};
