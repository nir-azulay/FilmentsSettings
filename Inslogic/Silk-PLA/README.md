# Inslogic Silk PLA

## Product Info

- **Brand:** Inslogic
- **Material:** Silk PLA (Four-Color Silk PLA)
- **Diameter:** 1.75mm ± 0.02mm
- **Net Weight:** 1 kg
- **Density:** ~1.25 g/cm³
- **Amazon:** https://www.amazon.com/dp/B0FQTHY34Y

## Key Features

- Four-color silk finish for decorative prints
- Smooth, glossy surface with metallic sheen
- Standard PLA printing ease
- Compatible with most FDM printers
- Not high-speed — standard printing speeds recommended for best silk finish

## Material Properties (Typical Silk PLA)

| Property | Value |
|---|---|
| Diameter | 1.75mm ± 0.02mm |
| Density | ~1.25 g/cm³ |
| Glass Transition Temperature (Tg) | ~60°C |
| Heat Deflection Temperature (HDT) | ~50°C |
| Vicat Softening Temperature | ~50°C |
| Nozzle Temperature Range | 205–235°C |
| Bed Temperature Range | 50–60°C |

*No official TDS available. Values based on SUNLU Silk PLA reference profile and typical Silk PLA properties.*

## Recommended Printing Settings

| Parameter | Value |
|---|---|
| Nozzle Temperature | 205–235°C (speed dependent) |
| Bed Temperature | 50–60°C |
| Cooling Fan Speed | 30–70% (controlled for silk finish) |
| Retraction Distance | 0.8–1.2mm |
| Retraction Speed | 30–40mm/s |
| Flow Ratio | 0.98 |
| Drying | 50°C for 12h |
| Print Speed | Moderate (not high-speed) |
| Air Filtration | Not required |
| Heated Chamber | Not required |

### Silk PLA Tips

- Moderate fan speeds (30-70%) preserve the silk sheen — too much cooling dulls the finish
- Slightly higher temps than standard PLA help the silk particles flow and orient properly
- Slower outer wall speeds improve surface finish quality
- Flow ratio of 0.98 prevents over-extrusion artifacts on the glossy surface

## Profile Configuration

**Printer:** Bambu Lab H2S
**Nozzle Types:** Standard + High Flow (0.2, 0.4, 0.6, 0.8mm)
**Filament ID:** Pd0b37275

### Filament Base Profiles (`filament/base/`)

| File | Nozzle | Max Vol Speed (STD/HF) | Nozzle Temp (STD/HF) | Retraction (STD/HF) |
|---|---|---|---|---|
| `my-Inslogic Silk PLA @Bambu Lab H2S 0.2 nozzle.json` | 0.2mm | 8 / 10 mm³/s | 230 / 230°C | 0.8 / 0.8 mm |
| `my-Inslogic Silk PLA @Bambu Lab H2S 0.4 nozzle.json` | 0.4mm | 12 / 16 mm³/s | 230 / 230°C | 1.0 / 1.0 mm |
| `my-Inslogic Silk PLA @Bambu Lab H2S 0.6 nozzle.json` | 0.6mm | 14 / 18 mm³/s | 230 / 230°C | 0.8 / 0.8 mm |
| `my-Inslogic Silk PLA @Bambu Lab H2S 0.8 nozzle.json` | 0.8mm | 16 / 20 mm³/s | 230 / 230°C | 0.9 / 0.9 mm |

**Common filament settings:** Flow ratio 0.98, Fan 30–70%, Bed 60°C (all plates), Pressure advance 0.02, Deretraction speed 35 mm/s, Tg=60°C, HDT=50°C

### Filament User Presets (`filament/`)

- `my-Inslogic Silk PLA @Bambu Lab H2S 0.2/0.4/0.6/0.8 nozzle` — per-nozzle presets
- `my-Inslogic Silk PLA Calibrated` — custom override for personal calibrations

### Process Presets (`process/`)

| File | Nozzle | Layer Height | Inner Wall | Outer Wall | Infill |
|---|---|---|---|---|---|
| `my-Inslogic Silk PLA 0.10mm @H2S 0.2 nozzle.json` | 0.2mm | 0.10mm | 80 | 50 | 80 |
| `my-Inslogic Silk PLA 0.20mm @H2S 0.4 nozzle.json` | 0.4mm | 0.20mm | 120 | 80 | 150 |
| `my-Inslogic Silk PLA 0.30mm @H2S 0.6 nozzle.json` | 0.6mm | 0.30mm | 150 | 80 | 180 |
| `my-Inslogic Silk PLA 0.40mm @H2S 0.8 nozzle.json` | 0.8mm | 0.40mm | 150 | 80 | 180 |

**Common process settings:** Gyroid infill 20%, 4 wall loops, support enabled, support top Z distance 0.28mm, bridge speed 25mm/s

### Key Silk PLA-specific Settings

- **Air filtration:** Disabled (PLA is safe)
- **Chamber temperature:** 0°C (not needed)
- **Fan speed:** 30–70% (controlled for silk finish)
- **First layers fan off:** 1 layer
- **Bed plates:** Cool plate 60°C, Hot plate 60°C, Textured 60°C, Supertack 60°C
- **Tg:** 60°C | **HDT:** 50°C
- **Flow ratio:** 0.98 / 0.98 (STD/HF)
- **Deretraction speed:** 35 mm/s (both extruders)
- **Aux fan gcode:** Included (manages chamber ventilation based on bed temp)

### Recommended Build Plate

| Plate | Recommended? | Glue? | Notes |
|-------|-------------|-------|-------|
| **Cool plate** | **Best choice** | No | Easy release, good adhesion |
| Textured PEI | Great | No | Also works well for silk finish |
| Hot plate (smooth PEI) | OK | No | Works fine |
| Engineering plate | Not recommended | — | PLA bonds too strongly, hard to remove |

## Installation

Files are deployed to:
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament\base\` (base profiles)
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament\` (user presets)
- `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\process\` (process presets)
