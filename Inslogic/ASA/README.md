# Inslogic ASA

## Product Info

- **Brand:** Inslogic
- **Material:** ASA (Acrylonitrile Styrene Acrylate)
- **Diameter:** 1.75mm ± 0.02mm
- **Net Weight:** 1 kg
- **Filament Length:** 370 m
- **Density:** 1.05 g/cm³
- **Amazon:** https://www.amazon.com/dp/B0FQTRVM8Y
- **Official Product Page:** https://www.inslogic3d.com/products/asa-filament
- **TDS PDF:** [Inslogic ASA Technical Data Sheet](https://cdn.shopify.com/s/files/1/0822/8611/7163/files/Inslogic_ASA_Filament_Technical_Data_Sheet_TDS.pdf?v=1737037060) ([local copy](Inslogic_ASA_TDS.pdf))

## Key Features

- UV & weather resistant
- Low warping
- Better layer adhesion
- Improved mechanical properties & strength
- High precision with fine detail
- Heat resistance
- Pre-dried for immediate use
- Compatible with Bambu Lab AMS and A1 mini

## Material Properties

| Property | Value |
|---|---|
| Chemical Name | Acrylonitrile Styrene Acrylate |
| Diameter | 1.75mm ± 0.02mm |
| Density | 1.05 g/cm³ |
| Melting Temperature | 120°C |
| Glass Transition Temperature (Tg) | 108°C |
| Heat Deflection Temperature (HDT @ 0.45 MPa) | 98°C |
| Tensile Strength | 52.4 MPa |
| Elongation at Break | 21.4% |
| Flexural Strength | 75.2 MPa |
| Flexural Modulus | 2162 MPa |
| Izod Impact, Notched | 18.33 KJ/m² |
| Shrinkage at 23°C | 0.4 - 0.9% |

Full data in the [TDS PDF](https://cdn.shopify.com/s/files/1/0822/8611/7163/files/Inslogic_ASA_Filament_Technical_Data_Sheet_TDS.pdf?v=1737037060). SDS also available on the [official product page](https://www.inslogic3d.com/products/asa-filament).

## Manufacturer Recommended Printing Settings

| Parameter | Value |
|---|---|
| Nozzle Temperature (slow 50-100mm/s) | 250 - 260°C |
| Nozzle Temperature (fast 100-200mm/s) | 260 - 280°C |
| Bed Temperature | 80 - 100°C |
| Cooling Fan Speed | 100% |
| Bed Type | Smooth PEI Sheet, High Temperature Plate |
| Glue | Recommended |
| Heated Chamber | Recommended |
| Drying Settings | 80°C, 4h |
| Supported Nozzle Sizes | 0.2, 0.4, 0.6 mm |
| Air Filtration | Required (styrene fumes) |

### Community Tips (from Amazon reviews)

- Nozzle 260°C, bed 90-100°C works well on Bambu printers
- Heated chamber (50-55°C) helps prevent warping
- Better bed adhesion than ABS, slight warping on large parts
- Excellent UV resistance for outdoor prints

## Profile Configuration

**Printer:** Bambu Lab H2S
**Nozzle Types:** Standard + High Flow (0.2, 0.4, 0.6, 0.8mm)

### Filament Base Profiles (`filament/base/`)

| File | Nozzle | Max Vol Speed (STD/HF) | Nozzle Temp (STD/HF) | Flow Ratio (STD/HF) |
|---|---|---|---|---|
| `my-Inslogic ASA basic @Bambu Lab H2S 0.2 nozzle.json` | 0.2mm | 6 / 8 mm³/s | 270 / 270°C | 0.95 / 0.98 |
| `my-Inslogic ASA basic @Bambu Lab H2S 0.4 nozzle.json` | 0.4mm | 18 / 18 mm³/s | 270 / 270°C | 0.98 / 0.98 |
| `my-Inslogic ASA basic @Bambu Lab H2S 0.6 nozzle.json` | 0.6mm | 16 / 30 mm³/s | 270 / 270°C | 0.97 / 0.97 |
| `my-Inslogic ASA basic @Bambu Lab H2S 0.8 nozzle.json` | 0.8mm | 22 / 38 mm³/s | 270 / 270°C | 0.97 / 0.97 |

### Filament User Presets (`filament/`)

- `my-Inslogic ASA basic @Bambu Lab H2S 0.2/0.4/0.6/0.8 nozzle` - per-nozzle presets
- `my-Inslogic ASA Calibrated` - custom override for personal calibrations

### Process Presets (`process/`)

| File | Nozzle | Layer Height | Inner Wall | Outer Wall | Infill |
|---|---|---|---|---|---|
| `my-Inslogic ASA 0.10mm @H2S 0.2 nozzle.json` | 0.2mm | 0.10mm | 100 | 60 | 100 |
| `my-Inslogic ASA 0.20mm @H2S 0.4 nozzle.json` | 0.4mm | 0.20mm | STD/160 HF | STD/100 HF | STD/200 HF |
| `my-Inslogic ASA 0.30mm @H2S 0.6 nozzle.json` | 0.6mm | 0.30mm | 200 | 100 | 250 |
| `my-Inslogic ASA 0.40mm @H2S 0.8 nozzle.json` | 0.8mm | 0.40mm | 200 | 100 | 250 |

**Common process settings:** Gyroid infill 20%, 4 wall loops, support enabled, support top Z distance 0.3mm

### Key ASA-specific Settings

- **Air filtration:** Enabled
- **Chamber temperature:** 60°C
- **Pressure advance:** Enabled (0.02)
- **Fan speed:** Max 35%, Min 10% (matching Bambu ASA system profile)
- **First layers fan off:** 3 layers
- **Retraction:** 0.5-0.9mm @ 30-35mm/s (varies by nozzle size)
- **Deretraction speed:** 30-35mm/s (matches retraction speed)
- **Bed plates:** Engineering 100°C, Hot plate 100°C, Textured 100°C (all plates)
- **Tg:** 108°C | **HDT:** 98°C

## Installation

Files are deployed to:
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament\base\` (base profiles)
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament\` (user presets)
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\process\` (process presets)
