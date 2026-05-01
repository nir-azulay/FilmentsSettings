# SUNLU Easy PA (Nylon 6+66)

## Product Info

- **Brand:** SUNLU
- **Material:** PA (Polyamide / Nylon 6+66)
- **Diameter:** 1.75mm
- **Weight:** 1KG
- **Density:** 1.10 g/cm³
- **Features:** Low warping/cracking, high toughness, excellent impact resistance
- **Amazon:** https://www.amazon.com/dp/B0FB2JQN1X
- **Official Page:** https://www.sunlu.com/products/easy-pa-nylon-filament
- **TDS PDF:** https://www.sunlu.com/public/upload/file/20260330/a5909dda-0573-4f11-a34a-00d495b1ea09.pdf

## Official TDS Recommended Printing Parameters

| Parameter | Value |
|---|---|
| Nozzle Temperature | 250-270°C @ 50-100mm/s, 270-280°C @ 100-150mm/s |
| Plate Temperature | 30-50°C |
| Plate Material | Textured PEI Build Plate |
| Plate Treatment | GLUE |
| Cooling Fan | Open/Close |
| Raft Distance | 0.2-0.4mm |
| Retraction Distance | 0.8-1.2mm |
| Retraction Speed | 30-40mm/s |
| Drying Temperature | 80-110°C |

## TDS Material Properties

| Property | Test Method | Value |
|---|---|---|
| Tensile Strength (X-Y) | ISO 527/2 | 61±6 MPa |
| Elongation at Break (X-Y) | ISO 527/2 | 15±3% |
| Flexural Strength (X-Y) | ISO 178 | 91±5 MPa |
| Flexural Modulus (X-Y) | ISO 178 | 2314±250 MPa |
| Izod Impact (Notched, X-Y) | ISO 180 | 11±3 KJ/m² |
| Izod Impact (Unnotched, Z-X) | ISO 180 | 5.1±1.5 KJ/m² |
| Shore Hardness | ISO 868 | 78.5 HA/HD |
| HDT (0.45 MPa) | ISO 75 | 119±3°C |
| Glass Transition (Tg) | ISO 11357-2 | 65°C |
| Melting Temperature | ISO 11357-3 | 198°C |
| Vicat Softening | ISO 306 | 135°C |
| Density | ISO 1183 | 1.10 g/cm³ |
| Moulding Shrinkage | ISO 294 | 1.3-1.6% |
| Flammability | UL 94 | HB |

## Profile Configuration

**Printer:** Bambu Lab H2S
**Nozzle Types:** Standard + High Flow (0.2, 0.4, 0.6, 0.8mm)

### Filament Base Profiles (`filament/base/`)

| File | Nozzle | Max Vol Speed (STD/HF) | Nozzle Temp (STD/HF) | Retraction (STD/HF) | Flow Ratio |
|---|---|---|---|---|---|
| `my-SUNLU PA E-PA @Bambu Lab H2S 0.2 nozzle.json` | 0.2mm | 5 / 7 mm³/s | 260 / 260°C | 0.8 / 0.8 mm @ 35 mm/s | 1.00 / 1.02 |
| `my-SUNLU PA E-PA @Bambu Lab H2S 0.4 nozzle.json` | 0.4mm | 9 / 12 mm³/s | 265 / 265°C | 1.0 / 1.0 mm @ 35 mm/s | 1.02 / 1.02 |
| `my-SUNLU PA E-PA @Bambu Lab H2S 0.6 nozzle.json` | 0.6mm | 12 / 18 mm³/s | 268 / 270°C | 0.8 / 0.8 mm @ 30/35 mm/s | 1.02 / 1.02 |
| `my-SUNLU PA E-PA @Bambu Lab H2S 0.8 nozzle.json` | 0.8mm | 15 / 22 mm³/s | 270 / 275°C | 0.9 / 0.9 mm @ 30/35 mm/s | 1.02 / 1.02 |

### Filament User Presets (`filament/`)

- `my-SUNLU PA E-PA @Bambu Lab H2S 0.2/0.4/0.6/0.8 nozzle` - per-nozzle presets
- `my-SUNLU PA E-PA Calibrated` - custom override for personal calibrations

### Process Presets (`process/`)

| File | Nozzle | Layer Height | Inner Wall | Outer Wall | Infill |
|---|---|---|---|---|---|
| `my-SUNLU PA E-PA 0.10mm @H2S 0.2 nozzle.json` | 0.2mm | 0.10mm | 80 | 50 | 80 |
| `my-SUNLU PA E-PA 0.20mm @H2S 0.4 nozzle.json` | 0.4mm | 0.20mm | STD/130 HF | STD/80 HF | STD/160 HF |
| `my-SUNLU PA E-PA 0.30mm @H2S 0.6 nozzle.json` | 0.6mm | 0.30mm | 160 | 80 | 200 |
| `my-SUNLU PA E-PA 0.40mm @H2S 0.8 nozzle.json` | 0.8mm | 0.40mm | 160 | 80 | 200 |

**Common process settings:** Gyroid infill 20%, 4 wall loops, support enabled, support top Z distance 0.3mm

### Key PA-specific Settings

- **Air filtration:** Enabled
- **Pressure advance:** 0.025
- **Fan speed:** Low (10-45% max depending on nozzle)
- **First layers fan off:** 3 layers
- **Bed plates:** Engineering 45°C, Hot plate 50°C, Textured PEI 50°C (all with glue)
- **Nozzle HRC:** 3 (hardened nozzle recommended)
- **Drying:** 80-110°C (TDS), 90°C AMS drying, 100°C chamber drying
- **HDT:** 119°C | **Vicat Softening:** 135°C | **Tg:** 65°C

## Installation

Files are deployed to:
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament\base\` (base profiles)
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament\` (user presets)
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\process\` (process presets)
