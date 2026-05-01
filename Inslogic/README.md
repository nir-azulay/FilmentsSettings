# Inslogic ASA

## Product Info

- **Brand:** Inslogic
- **Material:** ASA (UV & Weather Resistant)
- **Diameter:** 1.75mm
- **Features:** High-strength, heat-resistant, low warping, ideal for outdoor use
- **Amazon:** https://www.amazon.com/dp/B0FQTRVM8Y

## Manufacturer Recommended Settings

| Parameter | Value |
|---|---|
| Nozzle Temperature | 250 - 280°C |
| Bed Temperature | 90 - 100°C (PEI/Engineering plate) |
| Chamber Temperature | 50 - 60°C |
| Air Filtration | Required (styrene fumes) |
| Enclosure | Recommended |

### Community Tips (from Amazon reviews)

- Nozzle 260°C, bed 90-100°C works well on Bambu printers
- Turn off part cooling fan for best results
- Heated chamber (50-55°C) helps prevent warping
- Better bed adhesion than ABS, slight warping on large parts
- Excellent UV resistance for outdoor prints

## Profile Configuration

**Printer:** Bambu Lab H2S
**Nozzle Types:** Standard + High Flow (0.2, 0.4, 0.6, 0.8mm)

### Filament Base Profiles (`filament/base/`)

| File | Nozzle | Max Vol Speed (STD/HF) | Nozzle Temp (STD/HF) | Flow Ratio (STD/HF) |
|---|---|---|---|---|
| `azul-Inslogic ASA basic @Bambu Lab H2S 0.2 nozzle.json` | 0.2mm | 6 / 8 mm³/s | 255 / 255°C | 0.95 / 0.98 |
| `azul-Inslogic ASA basic @Bambu Lab H2S 0.4 nozzle.json` | 0.4mm | 18 / 18 mm³/s | 260 / 260°C | 0.95 / 0.98 |
| `azul-Inslogic ASA basic @Bambu Lab H2S 0.6 nozzle.json` | 0.6mm | 16 / 30 mm³/s | 255 / 260°C | 0.97 / 0.97 |
| `azul-Inslogic ASA basic @Bambu Lab H2S 0.8 nozzle.json` | 0.8mm | 22 / 38 mm³/s | 260 / 265°C | 0.97 / 0.97 |

### Filament User Presets (`filament/`)

- `azul-Inslogic ASA basic @Bambu Lab H2S 0.2/0.4/0.6/0.8 nozzle` - per-nozzle presets
- `azul-Inslogic ASA Calibrated` - custom override for personal calibrations

### Process Presets (`process/`)

| File | Nozzle | Layer Height | Inner Wall | Outer Wall | Infill |
|---|---|---|---|---|---|
| `azul-0.10mm Inslogic ASA @H2S 0.2 nozzle.json` | 0.2mm | 0.10mm | 100 | 60 | 100 |
| `azul-0.20mm Inslogic ASA @H2S 0.4 nozzle.json` | 0.4mm | 0.20mm | STD/160 HF | STD/100 HF | STD/200 HF |
| `azul-0.30mm Inslogic ASA @H2S 0.6 nozzle.json` | 0.6mm | 0.30mm | 200 | 100 | 250 |
| `azul-0.40mm Inslogic ASA @H2S 0.8 nozzle.json` | 0.8mm | 0.40mm | 200 | 100 | 250 |

**Common process settings:** Gyroid infill 20%, 4 wall loops, support enabled, support top Z distance 0.3mm

### Key ASA-specific Settings

- **Air filtration:** Enabled
- **Chamber temperature:** 60°C
- **Fan speed:** Minimal (0-10%)
- **First layers fan off:** 3 layers
- **Bed plates:** Engineering 90°C, Hot plate 90-100°C, Textured 95-105°C

## Installation

Files are deployed to:
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament\base\` (base profiles)
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament\` (user presets)
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\process\` (process presets)
