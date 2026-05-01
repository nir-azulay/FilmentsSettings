# SUNLU High Speed Matte PETG

## Product Info

- **Brand:** SUNLU
- **Material:** PETG (High Speed Matte)
- **Diameter:** 1.75mm ± 0.02mm
- **Max Print Speed:** 470 mm/s (per TDS)
- **Density:** 1.28 g/cm³
- **Amazon:** https://www.amazon.com/SUNLU-High-Speed-Filament-1-75mm/dp/B0D9NFF2T8
- **Official Page:** https://www.sunlu.com/products/high-speed-petg-filament
- **Technical Data Sheet (TDS):** [SL-TE-WI-062 PDF](https://www.sunlu.com/public/upload/file/20260330/ccf53a55-5b58-49fa-b1d9-08f94c0a4b28.pdf) · [Local copy](SUNLU_PETG_HS_TDS.pdf)

## Manufacturer Recommended Settings (from TDS)

| Parameter | Value |
|---|---|
| Nozzle Temp | 240–260°C (at speeds ≤400 mm/s) |
| Bed/Plate Temp | 60–70°C |
| Plate Material | Textured PEI Build Plate |
| Plate Treatment | No processing required |
| Cooling Fan | Open/Close |
| Raft Distance | 0.2–0.4mm |
| Retraction Distance | 0.8–1.2mm |
| Retraction Speed | 30–40mm/s |
| Supported Material | PVA |
| Drying Temp | 60–65°C |

## Material Properties (from TDS SL-TE-WI-062)

### Mechanical Properties

| Property | Test Method | Condition | Value |
|---|---|---|---|
| Tensile Strength (X-Y) | ISO 527/2 | 50 mm/min | 46±5 MPa |
| Elongation at Break (X-Y) | ISO 527/2 | 50 mm/min | 14±5% |
| Flexural Strength (X-Y) | ISO 178 | 2 mm/min | 75±6 MPa |
| Flexural Modulus (X-Y) | ISO 178 | 2 mm/min | 2650±200 MPa |
| Izod Impact, Notched (X-Y) | ISO 180 | 23°C | 3±1.5 KJ/m² |
| Izod Impact, Unnotched (Z-X) | ISO 180 | 23°C | 4.5±2 KJ/m² |
| Shore Hardness | ISO 868 | 23°C | 79 HA/HD |

### Thermal Properties

| Property | Test Method | Condition | Value |
|---|---|---|---|
| HDT (Heat Distortion) | ISO 75 | 0.45 MPa | 70±2°C |
| Glass Transition (Tg) | ISO 11357-2 | 10°C/min | 65.5°C |
| Melting Temperature | ISO 11357-3 | 10°C/min | 128°C |
| Decomposition Temp (@5%) | ISO 11358 | 20°C/min | ≥423°C |

### Other Properties

| Property | Test Method | Condition | Value |
|---|---|---|---|
| Melt Mass-flow Rate | ISO 1133 | 210°C/2.16 kg | 4.4±2 g/10min |
| Density | ISO 1183 | 23°C | 1.28 g/cm³ |
| Flammability | UL 94 | 1.5mm | Class HB |

## Profile Configuration

**Printer:** Bambu Lab H2S
**Nozzle Types:** Standard + High Flow (0.2, 0.4, 0.6, 0.8mm)

### Filament Base Profiles (`filament/base/`)

| File | Nozzle | Max Vol Speed (STD/HF) | Nozzle Temp (STD/HF) |
|---|---|---|---|
| `my-SUNLU PETG HS @Bambu Lab H2S 0.2 nozzle.json` | 0.2mm | 6 / 10 mm³/s | 240 / 250°C |
| `my-SUNLU PETG HS @Bambu Lab H2S 0.4 nozzle.json` | 0.4mm | 12 / 21 mm³/s | 245 / 255°C |
| `my-SUNLU PETG HS @Bambu Lab H2S 0.6 nozzle.json` | 0.6mm | 18 / 28 mm³/s | 250 / 260°C |
| `my-SUNLU PETG HS @Bambu Lab H2S 0.8 nozzle.json` | 0.8mm | 22 / 36 mm³/s | 255 / 260°C |

### Filament User Presets (`filament/`)

- `my-SUNLU PETG HS @Bambu Lab H2S 0.2/0.4/0.6/0.8 nozzle` - per-nozzle presets
- `my-SUNLU PETG HS Calibrated` - custom override for personal calibrations

### Process Presets (`process/`)

| File | Nozzle | Layer Height | Inner Wall | Outer Wall | Infill |
|---|---|---|---|---|---|
| `my-SUNLU PETG HS 0.10mm @H2S 0.2 nozzle.json` | 0.2mm | 0.10mm | 120 | 80 | 100 |
| `my-SUNLU PETG HS 0.20mm @H2S 0.4 nozzle.json` | 0.4mm | 0.20mm | STD/220 HF | STD/150 HF | STD/300 HF |
| `my-SUNLU PETG HS 0.30mm @H2S 0.6 nozzle.json` | 0.6mm | 0.30mm | 250/300 HF | 120/150 HF | 300/350 HF |
| `my-SUNLU PETG HS 0.40mm @H2S 0.8 nozzle.json` | 0.8mm | 0.40mm | 250/300 HF | 120/150 HF | 300/350 HF |

**Common process settings:** Gyroid infill 20%, 4 wall loops, support enabled, support top Z distance 0.32mm

## Installation

Files are deployed to:
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament\base\` (base profiles)
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament\` (user presets)
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\process\` (process presets)
