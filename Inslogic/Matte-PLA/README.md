# Inslogic Matte PLA

## Product Info

- **Brand:** Inslogic
- **Material:** PLA (Matte Finish)
- **Diameter:** 1.75mm ± 0.02mm
- **Net Weight:** 1 kg
- **Density:** 1.30 g/cm³
- **Amazon:** https://www.amazon.com/dp/B0FQTSLGM4
- **Official Product Page:** https://www.inslogic3d.com/products/matte-pla-filament
- **TDS PDF:** [Inslogic Matte PLA Technical Data Sheet](https://cdn.shopify.com/s/files/1/0822/8611/7163/files/Inslogic_Matte_PLA_Filament_Technical_Data_Sheet_TDS.pdf) ([local copy](Inslogic_Matte_PLA_TDS.pdf))

## Key Features

- Smooth matte surface finish
- Low warping and consistent quality
- High speed printing up to 230 mm/s
- Easy to print, minimal stringing
- Compatible with Bambu Lab AMS

## Material Properties

| Property | Value |
|---|---|
| Chemical Name | Polylactic Acid (PLA) |
| Diameter | 1.75mm ± 0.02mm |
| Density | 1.30 g/cm³ |
| Melting Temperature | 162.6°C |
| Glass Transition Temperature (Tg) | 58.8°C |
| Heat Deflection Temperature (HDT @ 0.45 MPa) | 55°C |
| Tensile Strength | 52.02 MPa |
| Elongation at Break | 9.87% |
| Young's Modulus | 4875 MPa |
| Flexural Strength | 64.00 MPa |
| Flexural Modulus | 2278 MPa |
| Izod Impact, Notched | 5.01 KJ/m² |
| Shrinkage at 23°C | 0.1 - 0.3% |

Full data in the [TDS PDF](https://cdn.shopify.com/s/files/1/0822/8611/7163/files/Inslogic_Matte_PLA_Filament_Technical_Data_Sheet_TDS.pdf). SDS also available on the [official product page](https://www.inslogic3d.com/products/matte-pla-filament).

## Manufacturer Recommended Printing Settings

| Parameter | Value |
|---|---|
| Nozzle Temperature (slow 50-100mm/s) | 205 - 215°C |
| Nozzle Temperature (fast 100-230mm/s) | 215 - 245°C |
| Bed Temperature | 50 - 60°C |
| Cooling Fan Speed | 100% |
| Bed Type | Textured PEI Sheet, Cool Plate |
| Max Speed | 230 mm/s |
| Drying Settings | 50°C, 4h |
| Supported Nozzle Sizes | 0.2, 0.4, 0.6 mm |

## Profile Configuration

**Printer:** Bambu Lab H2S
**Nozzle Types:** Standard + High Flow (0.2, 0.4, 0.6, 0.8mm)

### Filament Base Profiles (`filament/base/`)

| File | Nozzle | Max Vol Speed (STD/HF) | Nozzle Temp (STD/HF) | Retraction (STD/HF) | Flow Ratio (STD/HF) |
|---|---|---|---|---|---|
| `my-Inslogic Matte PLA @Bambu Lab H2S 0.2 nozzle.json` | 0.2mm | 8 / 10 mm³/s | 220 / 210°C | 0.8 / 0.8 mm @ 35 mm/s | 0.98 / 0.98 |
| `my-Inslogic Matte PLA @Bambu Lab H2S 0.4 nozzle.json` | 0.4mm | 12 / 16 mm³/s | 220 / 220°C | 1.0 / 1.0 mm @ 35 mm/s | 0.98 / 0.98 |
| `my-Inslogic Matte PLA @Bambu Lab H2S 0.6 nozzle.json` | 0.6mm | 15 / 20 mm³/s | 220 / 230°C | 0.8 / 0.8 mm @ 35 mm/s | 0.98 / 0.98 |
| `my-Inslogic Matte PLA @Bambu Lab H2S 0.8 nozzle.json` | 0.8mm | 18 / 24 mm³/s | 225 / 235°C | 0.9 / 0.9 mm @ 35 mm/s | 0.98 / 0.98 |

### Filament User Presets (`filament/`)

- `my-Inslogic Matte PLA @Bambu Lab H2S 0.2/0.4/0.6/0.8 nozzle` - per-nozzle presets
- `my-Inslogic Matte PLA Calibrated` - custom override for personal calibrations

### Process Presets (`process/`)

| File | Nozzle | Layer Height | Inner Wall | Outer Wall | Infill |
|---|---|---|---|---|---|
| `my-Inslogic Matte PLA 0.10mm @H2S 0.2 nozzle.json` | 0.2mm | 0.10mm | 100 | 60 | 100 |
| `my-Inslogic Matte PLA 0.20mm @H2S 0.4 nozzle.json` | 0.4mm | 0.20mm | STD/160 HF | STD/100 HF | STD/200 HF |
| `my-Inslogic Matte PLA 0.30mm @H2S 0.6 nozzle.json` | 0.6mm | 0.30mm | 200 | 100 | 230 |
| `my-Inslogic Matte PLA 0.40mm @H2S 0.8 nozzle.json` | 0.8mm | 0.40mm | 200 | 100 | 230 |

**Common process settings:** Gyroid infill 20%, 4 wall loops, support enabled, support top Z distance 0.28mm

### Key PLA-specific Settings

- **Air filtration:** Disabled (PLA is non-toxic)
- **Chamber temperature:** 0°C (no heated chamber for PLA)
- **Fan speed:** 100% (per manufacturer recommendation)
- **First layers fan off:** 1 layer
- **Bed plates:** Cool plate 55°C, Hot plate 55°C, Textured 55°C, Supertack 50°C
- **Engineering plate:** Disabled (0°C - PLA bonds too strongly)
- **Tg:** 59°C | **HDT:** 55°C
- **Pressure advance:** Enabled
- **Deretraction speed:** 35 mm/s (both extruders)
- **Aux fan gcode:** Included (manages chamber ventilation based on bed temp)

## Installation

Files are deployed to:
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament\base\` (base profiles)
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament\` (user presets)
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\process\` (process presets)
