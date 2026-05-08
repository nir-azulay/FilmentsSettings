const COLOR_MAP: Record<string, string> = {
  // Whites
  white: "#ffffff",
  snow: "#fffafa",
  ivory: "#fffff0",
  cream: "#fffdd0",
  pearl: "#f0ead6",
  "antique white": "#faebd7",

  // Blacks
  black: "#000000",
  "jet black": "#0a0a0a",
  charcoal: "#36454f",
  onyx: "#353839",

  // Greys
  grey: "#808080",
  gray: "#808080",
  silver: "#c0c0c0",
  "light grey": "#d3d3d3",
  "light gray": "#d3d3d3",
  "dark grey": "#404040",
  "dark gray": "#404040",
  "space grey": "#4a4a4a",
  "space gray": "#4a4a4a",
  graphite: "#474747",

  // Reds
  red: "#ff0000",
  "dark red": "#8b0000",
  crimson: "#dc143c",
  scarlet: "#ff2400",
  cherry: "#de3163",
  maroon: "#800000",
  wine: "#722f37",
  burgundy: "#800020",
  ruby: "#e0115f",
  "fire red": "#ce2029",
  brick: "#cb4154",
  cardinal: "#c41e3a",

  // Pinks
  pink: "#ffc0cb",
  "hot pink": "#ff69b4",
  magenta: "#ff00ff",
  fuchsia: "#ff00ff",
  rose: "#ff007f",
  salmon: "#fa8072",
  coral: "#ff7f50",
  blush: "#de5d83",
  "neon pink": "#ff6ec7",
  bubblegum: "#ffc1cc",

  // Oranges
  orange: "#ff8c00",
  "dark orange": "#ff8c00",
  tangerine: "#ff9966",
  peach: "#ffcba4",
  apricot: "#fbceb1",
  amber: "#ffbf00",
  rust: "#b7410e",
  copper: "#b87333",
  terracotta: "#e2725b",
  "burnt orange": "#cc5500",

  // Yellows
  yellow: "#ffff00",
  gold: "#ffd700",
  "lemon yellow": "#fff44f",
  mustard: "#ffdb58",
  "neon yellow": "#cfff04",
  blonde: "#faf0be",
  canary: "#ffef00",
  honey: "#eb9605",
  sunflower: "#ffda03",

  // Greens
  green: "#008000",
  "dark green": "#006400",
  "light green": "#90ee90",
  lime: "#00ff00",
  "neon green": "#39ff14",
  mint: "#98ff98",
  olive: "#808000",
  emerald: "#50c878",
  sage: "#9dc183",
  forest: "#228b22",
  "forest green": "#228b22",
  teal: "#008080",
  jade: "#00a86b",
  "army green": "#4b5320",
  "grass green": "#7cfc00",
  "sea green": "#2e8b57",
  pistachio: "#93c572",
  avocado: "#568203",

  // Blues
  blue: "#0000ff",
  "dark blue": "#00008b",
  "light blue": "#add8e6",
  navy: "#000080",
  "sky blue": "#87ceeb",
  "royal blue": "#4169e1",
  "baby blue": "#89cff0",
  cobalt: "#0047ab",
  cyan: "#00ffff",
  turquoise: "#40e0d0",
  aqua: "#00ffff",
  "steel blue": "#4682b4",
  "powder blue": "#b0e0e6",
  "ocean blue": "#0077be",
  "midnight blue": "#191970",
  sapphire: "#0f52ba",
  "ice blue": "#99d9ea",
  azure: "#007fff",
  denim: "#1560bd",
  "electric blue": "#7df9ff",
  "neon blue": "#4d4dff",
  indigo: "#4b0082",
  periwinkle: "#ccccff",

  // Purples
  purple: "#800080",
  violet: "#7f00ff",
  lavender: "#e6e6fa",
  lilac: "#c8a2c8",
  plum: "#dda0dd",
  "dark purple": "#301934",
  mauve: "#e0b0ff",
  "royal purple": "#7851a9",
  eggplant: "#614051",
  amethyst: "#9966cc",

  // Browns
  brown: "#8b4513",
  "dark brown": "#654321",
  "light brown": "#c4a484",
  tan: "#d2b48c",
  beige: "#f5f5dc",
  khaki: "#c3b091",
  chocolate: "#7b3f00",
  coffee: "#6f4e37",
  mocha: "#967969",
  caramel: "#ffd59a",
  walnut: "#773f1a",
  wood: "#a0522d",
  sienna: "#a0522d",
  chestnut: "#954535",
  mahogany: "#c04000",
  hazelnut: "#b5651d",

  // Metallics / Special
  "silk gold": "#d4af37",
  "silk silver": "#aaa9ad",
  "silk copper": "#b87333",
  "silk bronze": "#cd7f32",
  "silk rose gold": "#b76e79",
  bronze: "#cd7f32",
  "rose gold": "#b76e79",
  titanium: "#878681",
  platinum: "#e5e4e2",
  chrome: "#dbe4eb",

  // Transparent / Special
  transparent: "#ffffff",
  clear: "#ffffff",
  natural: "#f5f0e0",
  translucent: "#e8e8e8",

  // Common filament-specific colors
  "galaxy black": "#1c1c2e",
  "midnight": "#2c3e50",
  "arctic white": "#f8f8ff",
  "signal red": "#ff0000",
  "racing red": "#d50000",
  "grass": "#7cfc00",
  "ocean": "#0077be",
  "sunset": "#fad6a5",
  "sunrise": "#ffcf48",
  "lava": "#cf1020",
  "ice": "#d6fffa",
  "smoke": "#738276",
  "ash": "#b2beb5",
  "sand": "#c2b280",
  "clay": "#b66a50",
  "slate": "#708090",
  "cobblestone": "#8b8589",
};

export function lookupColorHex(name: string): string | null {
  const normalized = name.trim().toLowerCase();
  if (!normalized) return null;

  if (COLOR_MAP[normalized]) return COLOR_MAP[normalized];

  for (const [key, hex] of Object.entries(COLOR_MAP)) {
    if (key.includes(normalized) || normalized.includes(key)) {
      return hex;
    }
  }

  return null;
}

export function getColorSuggestions(name: string): Array<{ name: string; hex: string }> {
  const normalized = name.trim().toLowerCase();
  if (!normalized) return [];

  const results: Array<{ name: string; hex: string }> = [];

  for (const [key, hex] of Object.entries(COLOR_MAP)) {
    if (key.includes(normalized) || normalized.includes(key)) {
      results.push({ name: key, hex });
    }
  }

  return results.slice(0, 6);
}
