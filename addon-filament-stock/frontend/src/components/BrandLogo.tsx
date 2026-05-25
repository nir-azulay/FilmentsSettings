import { useState } from "react";

const BRAND_BG: Record<string, string> = {
  SUNLU: "#00a8a8",
  Inslogic: "#ffffff",
  Isanmate: "#ffffff",
  Jayo: "#ffffff",
  "Bambu Lab": "#ffffff",
  Bambu: "#ffffff",
  GolGeo: "#f5e400",
  CC3D: "#2a2a2c",
};

/** Convert a site-absolute logo path (e.g. "/logos/logo-sunlu.png") into a
 * relative path so it resolves correctly behind HA Ingress, where the app is
 * mounted under /api/hassio_ingress/<TOKEN>/. */
export function resolveLogoUrl(url: string | undefined): string | undefined {
  if (!url) return url;
  if (/^[a-z]+:\/\//i.test(url) || url.startsWith("//") || url.startsWith("data:")) return url;
  return url.replace(/^\/+/, "");
}

type Props = {
  brand: string;
  url?: string;
  size?: number;
};

export default function BrandLogo({ brand, url, size = 28 }: Props) {
  const [failed, setFailed] = useState(false);
  const bg = BRAND_BG[brand] ?? "#2a2a2c";
  const resolved = resolveLogoUrl(url);
  const showImg = resolved && !failed;

  return (
    <div
      title={brand}
      style={{
        width: size,
        height: size,
        borderRadius: 6,
        flexShrink: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
        background: bg,
        border: "1px solid var(--ha-divider)",
        boxShadow: "0 1px 2px rgba(0,0,0,0.08)",
      }}
    >
      {showImg ? (
        <img
          src={resolved}
          alt=""
          style={{ width: "100%", height: "100%", objectFit: "contain", padding: 3 }}
          onError={() => setFailed(true)}
        />
      ) : (
        <span style={{ fontSize: size * 0.32, fontWeight: 700, color: bg === "#ffffff" || bg === "#f5e400" ? "#333" : "#fff" }}>
          {brand.slice(0, 2).toUpperCase()}
        </span>
      )}
    </div>
  );
}

export function uniqueBrandsFromFilaments(
  filaments: { brand: string; brand_logo_url: string }[],
): { brand: string; logoUrl: string }[] {
  const map = new Map<string, string>();
  for (const f of filaments) {
    if (!map.has(f.brand)) {
      map.set(f.brand, f.brand_logo_url || "");
    }
  }
  return [...map.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([brand, logoUrl]) => ({ brand, logoUrl }));
}
