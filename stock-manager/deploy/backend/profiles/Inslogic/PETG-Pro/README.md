# Inslogic PETG Pro

High-Speed Matte PETG filament with enhanced toughness and bed adhesion.

## Product Info

| Property | Value |
|----------|-------|
| Brand | Inslogic |
| Material | PETG Pro (Matte) |
| Diameter | 1.75 ± 0.02 mm |
| Net Weight | 1 kg |
| Color | Black |
| Max Print Speed | 600 mm/s |

## Links

- **Amazon**: https://www.amazon.com/dp/B0DZG2TKZ4
- **Official**: https://www.inslogic3d.com
- **TDS PDF**: https://cdn.shopify.com/s/files/1/0822/8611/7163/files/Inslogic_PETG_Pro_Filament_Technical_Data_Sheet_TDS.pdf?v=1739875791

## TDS Material Properties

### Physical Properties

| Property | Method | Value |
|----------|--------|-------|
| Density | ISO 1183 | 1.26 g/cm³ |
| Melting Temperature | ISO 11357-3 | 128°C |
| Glass Transition Temperature (Tg) | ISO 11357-3 | 65.5°C |
| Heat Deflection Temperature (0.45 MPa) | ISO 75 | 72°C |

### Mechanical Properties

| Property | Method | Value |
|----------|--------|-------|
| Tensile Strength | ISO 527/2 | 50.00 MPa |
| Elongation at Break | ISO 527/2 | 34.53% |
| Flexural Strength | ISO 178 | 81.90 MPa |
| Flexural Modulus | ISO 178 | 2750 MPa |
| Izod Impact, Notched (X-Y, 23°C) | ISO 180 | 4.8 KJ/m² |

## Manufacturer Recommended Print Settings

| Parameter | Value |
|-----------|-------|
| Nozzle Size | 0.2, 0.4, 0.6 mm |
| Nozzle Temp (50-100 mm/s) | 230-240°C |
| Nozzle Temp (100-300 mm/s) | 240-255°C |
| Nozzle Temp (300-600 mm/s) | 255-270°C |
| Bed Temperature | 60-70°C |
| Cooling Fan | 100% (TDS) |
| Bed Type | Smooth PEI, High Temp Plate |
| Drying | 50°C, 4 hours |

## Profile Settings

Using Bambu PETG Basic as baseline for fan/retraction (60%/20% fan to prevent stringing).

| Setting | 0.2 nozzle | 0.4 nozzle | 0.6 nozzle | 0.8 nozzle |
|---------|-----------|-----------|-----------|-----------|
| Nozzle Temp (STD/HF) | 250/250°C | 245/250°C | 250/255°C | 255/260°C |
| Initial Layer Temp (STD/HF) | 250/250°C | 250/255°C | 255/260°C | 260/265°C |
| Bed Temp | 70°C | 70°C | 70°C | 70°C |
| Fan Max/Min | 60%/20% | 60%/20% | 60%/20% | 60%/20% |
| Overhang Fan | 50% | 50% | 50% | 50% |
| Retraction | 0.8mm | 0.8mm | 0.8mm | 0.8mm |
| Retraction Speed (STD/HF) | 35/40 mm/s | 35/40 mm/s | 35/40 mm/s | 35/40 mm/s |
| Max Volumetric (STD/HF) | 1/1 | 18/21 | 21/28 | 21/28 |

## Process Preset Speeds

| Setting | 0.2 nozzle | 0.4 nozzle | 0.6 nozzle | 0.8 nozzle |
|---------|-----------|-----------|-----------|-----------|
| Layer Height | 0.10mm | 0.20mm | 0.30mm | 0.40mm |
| Inner Wall (STD/HF) | 120/120 | 220/220 | 250/300 | 250/300 |
| Outer Wall (STD/HF) | 80/80 | 150/150 | 120/150 | 120/150 |
| Infill (STD/HF) | 100/100 | 300/300 | 300/350 | 300/350 |
| Initial Layer | 30/30 | 40/40 | 40/45 | 40/45 |
| Infill Density | 20% | 20% | 20% | 20% |
| Wall Loops | 4 | 4 | 4 | 4 |

## Files

| File | Description |
|------|-------------|
| `my-Inslogic PETG Pro @Bambu Lab H2S 0.{2,4,6,8} nozzle.json` | Base filament profiles |
| `my-Inslogic PETG Pro @Bambu Lab H2S 0.{2,4,6,8} nozzle.preset.json` | User presets |
| `my-Inslogic PETG Pro Calibrated.json` | Calibrated override |
| `my-Inslogic PETG Pro 0.{10,20,30,40}mm @H2S 0.{2,4,6,8} nozzle.json` | Process presets |
| `Inslogic_PETG_Pro_TDS.pdf` | Technical Data Sheet |

## Notes

- Recommended plate: **Textured PEI** (good adhesion + easy release, never smooth PEI for PETG)
- Fan speeds use Bambu PETG baseline (60/20%) NOT TDS 100% — over-cooling PETG causes stringing
- High-speed capable (600mm/s) so process speeds are set aggressively like SUNLU PETG HS
- Matte finish variant with enhanced toughness vs standard PETG
