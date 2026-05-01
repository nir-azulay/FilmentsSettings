# Inslogic PLA Pro

## Product Info

- **Brand:** Inslogic
- **Material:** PLA Pro (Polylactic Acid, enhanced)
- **Diameter:** 1.75mm ± 0.02mm
- **Net Weight:** 1 kg
- **Density:** 1.20 g/cm³
- **Amazon:** https://www.amazon.com/dp/B0FQTTXGWP
- **Official Product Page:** https://www.inslogic3d.com/products/pla-pro-filament
- **TDS PDF:** [Inslogic PLA Pro Technical Data Sheet](https://cdn.shopify.com/s/files/1/0822/8611/7163/files/Inslogic_PLA_Pro_Filament_Technical_Data_Sheet_TDS.pdf) ([local copy](Inslogic_PLA_Pro_TDS.pdf))

## Material Properties

| Property | Value |
|---|---|
| Density | 1.20 g/cm³ |
| Melting Temperature | 166°C |
| Glass Transition Temperature (Tg) | 65.3°C |
| Heat Deflection Temperature (HDT @ 0.45 MPa) | 55°C |
| Shore D Hardness | 83D |
| Tensile Strength | 56 MPa |
| Elongation at Break | 20.3% |
| Flexural Strength | 85.8 MPa |
| Flexural Modulus | 2795 MPa |
| Izod Impact, Notched | 20.1 KJ/m² |

Full data in the [TDS PDF](https://cdn.shopify.com/s/files/1/0822/8611/7163/files/Inslogic_PLA_Pro_Filament_Technical_Data_Sheet_TDS.pdf). SDS also available on the [official product page](https://www.inslogic3d.com/products/pla-pro-filament).

## Manufacturer Recommended Printing Settings

| Parameter | Value |
|---|---|
| Nozzle Temperature (slow 50-100mm/s) | 195 - 205°C |
| Nozzle Temperature (fast 100-300mm/s) | 205 - 220°C |
| Bed Temperature | 50 - 60°C |
| Cooling Fan Speed | 100% |
| Bed Type | Textured PEI Sheet, Cool Plate |
| Max Print Speed | 300 mm/s |
| Drying Settings | 50°C, 4h |
| Supported Nozzle Sizes | 0.2, 0.4, 0.6 mm |

## Profile Configuration

**Printer:** Bambu Lab H2S
**Nozzle Types:** Standard + High Flow (0.2, 0.4, 0.6, 0.8mm)

### Filament Base Profiles (`filament/base/`)

| File | Nozzle | Max Vol Speed (STD/HF) | Nozzle Temp (STD/HF) | Retraction (STD/HF) | Flow Ratio (STD/HF) |
|---|---|---|---|---|---|
| `my-Inslogic PLA Pro @Bambu Lab H2S 0.2 nozzle.json` | 0.2mm | 8 / 10 mm³/s | 205 / 205°C | 0.8 / 0.8 mm @ 35 mm/s | 0.98 / 0.98 |
| `my-Inslogic PLA Pro @Bambu Lab H2S 0.4 nozzle.json` | 0.4mm | 12 / 16 mm³/s | 210 / 215°C | 1.0 / 1.0 mm @ 35 mm/s | 0.98 / 0.98 |
| `my-Inslogic PLA Pro @Bambu Lab H2S 0.6 nozzle.json` | 0.6mm | 15 / 20 mm³/s | 215 / 220°C | 0.8 / 0.8 mm @ 35 mm/s | 0.98 / 0.98 |
| `my-Inslogic PLA Pro @Bambu Lab H2S 0.8 nozzle.json` | 0.8mm | 18 / 24 mm³/s | 215 / 220°C | 0.9 / 0.9 mm @ 35 mm/s | 0.98 / 0.98 |

### Filament User Presets (`filament/`)

- `my-Inslogic PLA Pro @Bambu Lab H2S 0.2/0.4/0.6/0.8 nozzle` - per-nozzle presets
- `my-Inslogic PLA Pro Calibrated` - custom override for personal calibrations

### Process Presets (`process/`)

| File | Nozzle | Layer Height | Inner Wall (STD/HF) | Outer Wall (STD/HF) | Infill (STD/HF) |
|---|---|---|---|---|---|
| `my-Inslogic PLA Pro 0.10mm @H2S 0.2 nozzle.json` | 0.2mm | 0.10mm | 100 / 100 | 60 / 60 | 100 / 100 |
| `my-Inslogic PLA Pro 0.20mm @H2S 0.4 nozzle.json` | 0.4mm | 0.20mm | nil / 200 | nil / 120 | nil / 250 |
| `my-Inslogic PLA Pro 0.30mm @H2S 0.6 nozzle.json` | 0.6mm | 0.30mm | 250 / 250 | 120 / 120 | 300 / 300 |
| `my-Inslogic PLA Pro 0.40mm @H2S 0.8 nozzle.json` | 0.8mm | 0.40mm | 250 / 250 | 120 / 120 | 300 / 300 |

**Common process settings:** Gyroid infill 20%, 4 wall loops, support enabled, support top Z distance 0.28mm

### Key PLA Pro-specific Settings

- **Air filtration:** Disabled (PLA is safe)
- **Chamber temperature:** 0°C (no heated chamber needed)
- **Fan speed:** 100% min/max (per manufacturer recommendation)
- **First layers fan off:** 1 layer
- **Bed plates:** Cool plate 55°C, Hot plate 55°C, Textured 55°C, Engineering 0°C (not recommended)
- **Pressure advance:** Enabled (0.02)
- **Tg:** 65°C | **HDT:** 55°C | **Density:** 1.20 g/cm³

## Installation

Files are deployed to:
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament\base\` (base profiles)
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament\` (user presets)
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\process\` (process presets)
