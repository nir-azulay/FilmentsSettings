# GolGeo Silk PLA

## Product Info

- **Brand:** GolGeo
- **Material:** Silk PLA (Shiny Gold)
- **Diameter:** 1.75mm ± 0.02mm
- **Net Weight:** 1 kg / 2.2 lbs
- **Color:** Gold (Silky)
- **Density:** ~1.24 g/cm³

## Key Features

- Shiny silk gold finish
- Glossy and smooth surface
- Dimensional accuracy ± 0.02mm
- Compatible with most FDM printers

## Material Properties (Generic Silk PLA)

| Property | Value |
|---|---|
| Diameter | 1.75mm ± 0.02mm |
| Density | ~1.24 g/cm³ |
| Glass Transition Temperature (Tg) | ~45°C |
| Heat Deflection Temperature (HDT) | ~45°C |
| Vicat Softening Temperature | ~50°C |
| Nozzle Temperature Range | 190–240°C |
| Bed Temperature Range | 35–55°C |

*Based on Generic PLA Silk @BBL H2S system profile.*

## Recommended Printing Settings

| Parameter | Value |
|---|---|
| Nozzle Temperature (0.4-0.8mm) | 220°C |
| Nozzle Temperature (0.2mm) | 240°C |
| Bed Temperature | 35–55°C (plate dependent) |
| Cooling Fan Speed | 100% |
| Retraction Distance | 0.4mm |
| Retraction Speed | 35mm/s |
| Flow Ratio | 0.98 |
| Drying | 45°C for 12h |
| Print Speed | Standard (not high-speed) |
| Outer Wall Speed | 50–60mm/s (for best gloss) |

### Silk PLA Tips

- Full cooling (100%) as per Bambu Generic Silk PLA profile
- Higher nozzle temp (240°C) required for 0.2mm nozzle due to restricted flow
- Slower outer wall speeds (50-60mm/s) improve silk surface finish
- Flow ratio 0.98 prevents over-extrusion artifacts on glossy surface
- Wipe enabled (1mm distance) for cleaner retractions

## Profile Configuration

**Printer:** Bambu Lab H2S
**Nozzle Types:** Standard + High Flow (0.2, 0.4, 0.6, 0.8mm)
**Filament ID:** Pf2a8e6c3

### Filament Base Profiles (`filament/base/`)

| File | Nozzle | Max Vol Speed (STD/HF) | Nozzle Temp (STD/HF) | Retraction |
|---|---|---|---|---|
| `my-GolGeo Silk PLA @Bambu Lab H2S 0.2 nozzle.json` | 0.2mm | 1 / 1 mm³/s | 240 / 240°C | 0.4mm |
| `my-GolGeo Silk PLA @Bambu Lab H2S 0.4 nozzle.json` | 0.4mm | 7.5 / 7.5 mm³/s | 220 / 220°C | 0.4mm |
| `my-GolGeo Silk PLA @Bambu Lab H2S 0.6 nozzle.json` | 0.6mm | 7.5 / 7.5 mm³/s | 220 / 220°C | 0.4mm |
| `my-GolGeo Silk PLA @Bambu Lab H2S 0.8 nozzle.json` | 0.8mm | 7.5 / 7.5 mm³/s | 220 / 220°C | 0.4mm |

**Common settings:** Flow ratio 0.98, Fan 100%, Bed 55°C (hot/textured/eng), Cool plate 35°C, Pressure advance 0.02, Wipe 1mm, Spiral lift Z-hop

### Filament User Presets (`filament/`)

- `my-GolGeo Silk PLA Calibrated` — custom override for personal calibrations

### Process Presets (`process/`)

| File | Nozzle | Layer Height | Inner Wall | Outer Wall | Infill |
|---|---|---|---|---|---|
| `my-GolGeo Silk PLA 0.10mm @H2S 0.2 nozzle.json` | 0.2mm | 0.10mm | 80 | 50 | 80 |
| `my-GolGeo Silk PLA 0.20mm @H2S 0.4 nozzle.json` | 0.4mm | 0.20mm | 120 | 60 | 150 |
| `my-GolGeo Silk PLA 0.30mm @H2S 0.6 nozzle.json` | 0.6mm | 0.30mm | 150 | 60 | 180 |
| `my-GolGeo Silk PLA 0.40mm @H2S 0.8 nozzle.json` | 0.8mm | 0.40mm | 150 | 60 | 180 |

**Common process settings:** Gyroid infill 20%, 4 wall loops, support enabled, bridge speed 25mm/s

### Recommended Build Plate

| Plate | Recommended? | Glue? | Notes |
|-------|-------------|-------|-------|
| **Cool plate** | Good | No | 35°C, easy release |
| **Textured PEI** | Great | No | 55°C, good silk finish |
| Hot plate (smooth PEI) | Good | No | 55°C |
| Engineering plate | OK | No | 55°C |

## Installation

Files are deployed via `DeployPack\deploy.ps1` to:
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament\base\` (base profiles)
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament\` (calibrated preset)
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\process\` (process presets)
