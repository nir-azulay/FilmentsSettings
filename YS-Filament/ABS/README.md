# YS Filament ABS

## Product Info

| Field | Value |
|---|---|
| Brand | YS Filament (Guangzhou Yousu 3D Technology Co., Ltd) |
| Material | ABS |
| Diameter | 1.75mm |
| Product Code | YS-ABS111 |
| Amazon | https://a.co/d/02OrrAfC |
| TDS PDF | https://ysfilament.com/u_file/2211/09/file/ABSTDS-af53.pdf |

## TDS Material Properties

### Mechanical Properties

| Property | Test Method | Value | Conditions |
|---|---|---|---|
| Tensile Strength (yield) | ISO 527 | 47 MPa | 50mm/min |
| Tensile Strength (break) | ISO 527 | 34 MPa | 50mm/min |
| Tensile Elongation (break) | ISO 527 | 30% | 50mm/min |
| Flexural Strength | ISO 178 | 76 MPa | 2mm/min |
| Flexural Modulus | ISO 178 | 2.2 GPa | |
| Impact Strength (Izod notched, 23C) | ISO 180/1A | 19 KJ/m² | |
| Impact Strength (Izod notched, -30C) | ISO 180/1A | 9 KJ/m² | |

### Thermal Properties

| Property | Test Method | Value | Conditions |
|---|---|---|---|
| Vicat Softening Temperature | ISO 306 | 104°C / 100°C | 1Kg / 5Kg, 50°C/hr |
| Heat Deflection Temperature | ISO 75/A | 83°C / 98°C | 1.8 MPa, Unannealed / Annealed |
| Flammability | UL-94 | HB | 1.5mm |

### Physical Properties

| Property | Test Method | Value | Conditions |
|---|---|---|---|
| Density | ISO 1183 | 1.05 g/cm³ | 23°C |
| Melt Flow Rate | ISO 1133 | 18.9 g/10min | 220°C, 10Kg |
| Mold Shrinkage | ISO 294-4 | 0.4-0.7% | |
| Linear Expansion Coefficient | ISO 11359 | 8.6×10⁻⁵ | |

## Manufacturer Recommended Print Settings

| Setting | TDS Value | Profile Value (Bambu H2S) |
|---|---|---|
| Nozzle Temperature | 220-250°C | 270°C (matches Bambu system ABS) |
| Bed Temperature | 80-120°C | 90°C (matches Bambu system ABS) |
| Retraction | N/A | 0.4mm @ 35mm/s (H2S direct drive) |
| Fan Max | N/A | 80% (60% for 0.2mm nozzle) |
| Fan Min | N/A | 10% (40% for 0.2mm nozzle) |
| Overhang Fan | N/A | 80% |

## Profile Files

| File | Nozzle | Key Settings |
|---|---|---|
| `my-YS Filament ABS @Bambu Lab H2S 0.2 nozzle.json` | 0.2mm | 270°C, Bed 90°C, MVS 2, Fan 60/40% |
| `my-YS Filament ABS @Bambu Lab H2S 0.4 nozzle.json` | 0.4mm | 270°C, Bed 90°C, MVS 15, Fan 80/10% |
| `my-YS Filament ABS @Bambu Lab H2S 0.6 nozzle.json` | 0.6mm | 270°C, Bed 90°C, MVS 15, Fan 80/10% |
| `my-YS Filament ABS @Bambu Lab H2S 0.8 nozzle.json` | 0.8mm | 270°C, Bed 90°C, MVS 15, Fan 80/10% |
| `my-YS Filament ABS Calibrated.json` | 0.4mm | Calibration override |
| `my-YS Filament ABS 0.10mm @H2S 0.2 nozzle.json` | 0.2mm | Process: 0.10mm layer, gyroid 20%, 4 walls |
| `my-YS Filament ABS 0.20mm @H2S 0.4 nozzle.json` | 0.4mm | Process: 0.20mm layer, gyroid 20%, 4 walls |
| `my-YS Filament ABS 0.30mm @H2S 0.6 nozzle.json` | 0.6mm | Process: 0.30mm layer, gyroid 20%, 4 walls |
| `my-YS Filament ABS 0.40mm @H2S 0.8 nozzle.json` | 0.8mm | Process: 0.40mm layer, gyroid 20%, 4 walls |

## Notes

- ABS requires an enclosure for best results (chamber temp 60°C recommended)
- Use engineering plate with glue for best adhesion
- Enable air filtration -- ABS produces fumes
- Brim (outer + inner, 5mm) enabled in process presets for bed adhesion
- First layer speed set to 30mm/s for better adhesion
- Nozzle temp set to 270°C per Bambu system ABS profile (significantly higher than TDS 220-250°C range -- this is normal for H2S direct drive)
