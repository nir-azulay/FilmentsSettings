import { useRef, useState } from "react";
import jsQR from "jsqr";

interface Props {
  onScanned: (uid: string) => void;
  onClose: () => void;
}

const SP_RE = /SP-[A-F0-9]{8}/i;

/** Load an image file onto a canvas and return the context + dimensions. */
function loadImageToCanvas(
  file: File,
  maxDim = 1400,
): Promise<{ ctx: CanvasRenderingContext2D; w: number; h: number }> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const scale = Math.min(1, maxDim / Math.max(img.width, img.height));
      const w = Math.round(img.width * scale);
      const h = Math.round(img.height * scale);
      const canvas = document.createElement("canvas");
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext("2d")!;
      ctx.drawImage(img, 0, 0, w, h);
      URL.revokeObjectURL(img.src);
      resolve({ ctx, w, h });
    };
    img.onerror = () => {
      URL.revokeObjectURL(img.src);
      reject(new Error("Failed to load image"));
    };
    img.src = URL.createObjectURL(file);
  });
}

/**
 * Decode a QR code from an image file.
 * Strategy: load to canvas, try jsQR on full image and progressively
 * tighter center crops until the QR code is found.
 */
async function decodeQR(file: File): Promise<string> {
  const { ctx, w, h } = await loadImageToCanvas(file);

  for (const cropFactor of [1, 0.75, 0.5]) {
    const cw = Math.round(w * cropFactor);
    const ch = Math.round(h * cropFactor);
    const cx = Math.round((w - cw) / 2);
    const cy = Math.round((h - ch) / 2);
    const imgData = ctx.getImageData(cx, cy, cw, ch);
    const result = jsQR(imgData.data, cw, ch);
    if (result?.data) return result.data;
  }

  throw new Error("no_qr");
}

export default function QrScannerDialog({ onScanned, onClose }: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [decoding, setDecoding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [manualUid, setManualUid] = useState("");

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setDecoding(true);
    setError(null);
    try {
      const decoded = await decodeQR(file);
      const match = decoded.match(SP_RE);
      if (match) {
        onScanned(match[0].toUpperCase());
      } else {
        setError(`QR decoded but no spool UID found: "${decoded}"`);
      }
    } catch {
      setError(
        "Could not read a QR code from the photo. " +
          "Make sure the QR code fills most of the frame and is in focus.",
      );
    } finally {
      setDecoding(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const handleManualSubmit = () => {
    const trimmed = manualUid.trim().toUpperCase();
    const match = trimmed.match(SP_RE);
    if (match) {
      onScanned(match[0]);
    } else {
      setError("Invalid spool UID. Expected format: SP-XXXXXXXX");
    }
  };

  return (
    <div style={overlay} onClick={onClose}>
      <div style={dialog} onClick={(e) => e.stopPropagation()}>
        <div style={header}>
          <h3 style={titleStyle}>Scan Spool QR Code</h3>
          <button onClick={onClose} style={closeBtn} aria-label="Close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <div style={body}>
          <p style={instruction}>
            Take a photo of the QR code on the spool label:
          </p>

          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            capture="environment"
            onChange={handleFile}
            style={{ display: "none" }}
            id="qr-file-input"
          />

          <button
            onClick={() => fileRef.current?.click()}
            disabled={decoding}
            style={cameraBtn}
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
              <circle cx="12" cy="13" r="4" />
            </svg>
            {decoding ? "Decoding..." : "Take Photo"}
          </button>

          {error && <p style={errorText}>{error}</p>}

          <div style={dividerStyle}>
            <div style={dividerLine} />
            <span style={dividerText}>or enter UID manually</span>
            <div style={dividerLine} />
          </div>

          <div style={manualRow}>
            <input
              type="text"
              value={manualUid}
              onChange={(e) => setManualUid(e.target.value)}
              placeholder="SP-XXXXXXXX"
              style={manualInput}
              onKeyDown={(e) => e.key === "Enter" && handleManualSubmit()}
            />
            <button onClick={handleManualSubmit} style={manualBtn}>
              Assign
            </button>
          </div>
        </div>
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
  width: "min(400px, 92vw)", maxHeight: "90vh", overflowY: "auto",
  boxShadow: "0 8px 32px rgba(0,0,0,0.25)",
};
const header: React.CSSProperties = {
  display: "flex", justifyContent: "space-between", alignItems: "center",
  padding: "14px 16px", borderBottom: "1px solid var(--ha-divider, #e0e0e0)",
};
const titleStyle: React.CSSProperties = {
  margin: 0, fontSize: 16, fontWeight: 600, color: "var(--ha-primary-text)",
};
const closeBtn: React.CSSProperties = {
  background: "none", border: "none", color: "var(--ha-secondary-text)",
  width: 32, height: 32, display: "flex", alignItems: "center",
  justifyContent: "center", borderRadius: "50%", cursor: "pointer",
};
const body: React.CSSProperties = {
  padding: "16px 20px 20px",
};
const instruction: React.CSSProperties = {
  fontSize: 14, color: "var(--ha-primary-text)", textAlign: "center",
  margin: "0 0 14px", lineHeight: 1.5,
};
const cameraBtn: React.CSSProperties = {
  display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
  width: "100%", padding: "14px 20px",
  background: "var(--ha-primary-color, #1976d2)", color: "#fff",
  border: "none", borderRadius: 8,
  fontSize: 16, fontWeight: 600, cursor: "pointer",
};
const errorText: React.CSSProperties = {
  fontSize: 13, color: "var(--ha-error, #c62828)", textAlign: "center",
  padding: "10px 0 0", margin: 0,
};
const dividerStyle: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 12,
  margin: "18px 0 14px",
};
const dividerLine: React.CSSProperties = {
  flex: 1, height: 1, background: "var(--ha-divider, #e0e0e0)",
};
const dividerText: React.CSSProperties = {
  fontSize: 12, color: "var(--ha-secondary-text)",
  whiteSpace: "nowrap", flex: "0 0 auto",
};
const manualRow: React.CSSProperties = {
  display: "flex", gap: 8,
};
const manualInput: React.CSSProperties = {
  flex: 1, padding: "8px 12px",
  border: "1px solid var(--ha-divider, #e0e0e0)", borderRadius: 6,
  fontSize: 14, fontFamily: "ui-monospace, monospace",
  color: "var(--ha-primary-text)", background: "#fff",
};
const manualBtn: React.CSSProperties = {
  padding: "8px 16px",
  background: "var(--ha-primary-color, #1976d2)", color: "#fff",
  border: "none", borderRadius: 6,
  fontSize: 13, fontWeight: 600, cursor: "pointer",
};
