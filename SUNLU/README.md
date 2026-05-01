# SUNLU High Speed PETG

## Product Info

- **Brand:** SUNLU
- **Material:** PETG (High Speed / High Flow)
- **Diameter:** 1.75mm ± 0.02mm
- **Print Speed Range:** 30 - 600mm/s
- **Amazon:** https://www.amazon.com/SUNLU-High-Speed-Filament-1-75mm/dp/B0D9NFF2T8

## Manufacturer Recommended Settings

| Speed Range | Nozzle Temp | Bed Temp |
|---|---|---|
| 50 - 100 mm/s | 230 - 240°C | 70 - 80°C |
| 100 - 300 mm/s | 240 - 255°C | 70 - 80°C |
| 300 - 600 mm/s | 255 - 270°C | 70 - 80°C |

## Profile Configuration

**Printer:** Bambu Lab H2S
**Nozzle Types:** Standard + High Flow (0.2, 0.4, 0.6, 0.8mm)

### Filament Base Profiles (`filament/base/`)

| File | Nozzle | Max Vol Speed (STD/HF) | Nozzle Temp (STD/HF) |
|---|---|---|---|
| `azul-SUNLU PETG HS @Bambu Lab H2S 0.2 nozzle.json` | 0.2mm | 6 / 8 mm³/s | 255 / 255°C |
| `azul-SUNLU PETG HS @Bambu Lab H2S 0.4 nozzle.json` | 0.4mm | 12 / 21 mm³/s | 245 / 255°C |
| `azul-SUNLU PETG HS @Bambu Lab H2S 0.6 nozzle.json` | 0.6mm | 18 / 28 mm³/s | 250 / 260°C |
| `azul-SUNLU PETG HS @Bambu Lab H2S 0.8 nozzle.json` | 0.8mm | 22 / 32 mm³/s | 255 / 265°C |

### Filament User Presets (`filament/`)

- `azul-SUNLU PETG HS @Bambu Lab H2S 0.2/0.4/0.6/0.8 nozzle` - per-nozzle presets
- `azul-SUNLU PETG HS Calibrated` - custom override for personal calibrations

### Process Presets (`process/`)

| File | Nozzle | Layer Height | Inner Wall | Outer Wall | Infill |
|---|---|---|---|---|---|
| `azul-0.10mm SUNLU PETG HS @H2S 0.2 nozzle.json` | 0.2mm | 0.10mm | 120 | 80 | 100 |
| `azul-0.20mm SUNLU PETG HS @H2S 0.4 nozzle.json` | 0.4mm | 0.20mm | STD/220 HF | STD/150 HF | STD/300 HF |
| `azul-0.30mm SUNLU PETG HS @H2S 0.6 nozzle.json` | 0.6mm | 0.30mm | 250/300 HF | 120/150 HF | 300/350 HF |
| `azul-0.40mm SUNLU PETG HS @H2S 0.8 nozzle.json` | 0.8mm | 0.40mm | 250/300 HF | 120/150 HF | 300/350 HF |

**Common process settings:** Gyroid infill 20%, 4 wall loops, support enabled, support top Z distance 0.32mm

## Installation

Files are deployed to:
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament\base\` (base profiles)
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament\` (user presets)
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\process\` (process presets)
