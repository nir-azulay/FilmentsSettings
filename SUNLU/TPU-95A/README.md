# SUNLU TPU 95A - Industrial Grade Flexible Filament

## Product Information

- **Brand**: SUNLU
- **Material**: TPU 95A (Shore 95A hardness)
- **Diameter**: 1.75mm ± 0.03mm
- **Grade**: Industrial grade
- **Weight**: 2kg (2x 1kg spools in the 2-pack)

## Links

- **Amazon Product Page**: [SUNLU TPU 95A on Amazon.pl](https://www.amazon.pl/dp/B0FRZZSN7D)
- **Official SUNLU Website**: [SUNLU TPU Collection](https://www.sunlu.com/collections/tpu-filament)
- **TDS Document**: SL-TE-WI-088 - [Download PDF](https://media.sunlu.com/prod/20260330/e8b9c06a-4b93-46cb-9532-d9deb185a7c8.pdf)

## Material Properties

### Mechanical Properties (from TDS SL-TE-WI-088)
| Property | Value | Test Method | Notes |
|----------|-------|-------------|-------|
| Shore Hardness | 95 HA | ISO 868 | Good balance of flexibility and rigidity |
| Tensile Strength | 31±3 MPa | ISO 527/2 | X-Y direction, 50mm/min |
| Elongation at Break | >900% | ISO 527/2 | Extremely elastic! |
| Izod Impact Strength (Notched) | 47±5 KJ/m² | ISO 180 | X-Y direction, 23°C |
| Izod Impact Strength (Unnotched) | 38±5 KJ/m² | ISO 180 | Z-X direction, 23°C |

### Thermal Properties (from TDS SL-TE-WI-088)
| Property | Value | Test Method | Notes |
|----------|-------|-------------|-------|
| Decomposition Temp (@5%) | ≥300°C | ISO 11358 | High thermal stability |
| Melt Mass-Flow Rate | 28±3 g/10min | ISO 1133 | 190°C/2.16kg |
| Drying Temperature | 50-60°C | TDS spec | Use 55°C optimal |
| Drying Time | 12 hours | TDS spec | Before printing |

### Physical Properties (from TDS SL-TE-WI-088)
| Property | Value | Test Method | Notes |
|----------|-------|-------------|-------|
| Density | 1.21 g/cm³ | ISO 1183 | @ 23°C |
| Diameter Tolerance | ±0.03 mm | Product spec | High precision |
| Volume Resistivity | 1.05×10¹² ohm-cm | IEC 60093 | Electrical properties |
| Permittivity | 3.4 | IEC 60250 | @ 1 kHz |
| Flammability | HB Class | UL 94 | @ 1.5mm |

## Manufacturer Recommended Print Settings (TDS SL-TE-WI-088)

| Setting | TDS Specification | Profile Value | Notes |
|---------|------------------|---------------|-------|
| **Nozzle Temperature** | 190-210°C @ 50-80mm/s<br>210-230°C @ 80-120mm/s | 230°C | Use 230°C for high-speed printing |
| **Bed Temperature** | 50-60°C | 55°C | Textured PEI plate, no processing required |
| **Print Speed** | 50-120 mm/s | Up to 120 mm/s | Temperature-dependent speed range |
| **Max Volumetric Speed** | - | 6 mm³/s (Std)<br>12 mm³/s (HF) | High Flow nozzles enable full speed |
| **Retraction Distance** | 0.8-1.2 mm | 1.0 mm | TDS-compliant (with TPU feeder assistant) |
| **Retraction Speed** | 30-40 mm/s | 35 mm/s | TDS mid-range for reduced stringing |
| **Part Cooling Fan** | Open/Close | 100% | Full cooling throughout print |
| **Raft Distance** | 0.2-0.4 mm | - | TDS specification |
| **Drying Temperature** | 50-60°C | 55°C | 12 hours before printing |
| **Support Material** | PVA | - | TDS recommendation |

## Print Quality Tips

1. **Nozzle Selection**: This TPU works with 0.4mm, 0.6mm, and 0.8mm nozzles (no 0.2mm due to flexibility)
2. **High Flow Advantage**: With High Flow nozzles, you can achieve 12 mm³/s volumetric speed and 120mm/s linear speed
3. **Bed Adhesion**: Use Textured PEI plate at 35°C - excellent adhesion without glue
4. **No AMS Support**: TPU 95A is too soft/flexible for AMS compatibility - manual feeding required
5. **Retraction**: Keep retraction minimal (2mm) and slow (10mm/s) to avoid jamming
6. **First Layer**: Print first layer at 30-35mm/s for best adhesion
7. **Drying**: If filament absorbs moisture, dry at 65°C for 12 hours before printing

## Created Profile Files

### Filament Base Profiles (3 nozzle sizes)
| File Name | Nozzle | Nozzle Temp | Volumetric Speed (Std/HF) | Notes |
|-----------|--------|-------------|---------------------------|-------|
| `SUNLU TPU 95A @Bambu Lab H2S.json` | 0.4, 0.6, 0.8mm | 230/230°C | 6/12 mm³/s | Base profile for all nozzles |

### User Presets
| File Name | Purpose |
|-----------|---------|
| `SUNLU TPU 95A @Bambu Lab H2S.preset.json` | User preset (inherits from base) |
| `SUNLU TPU 95A Calibrated.json` | Post-calibration overrides |

### Process Presets (3 nozzle sizes)
| File Name | Nozzle | Layer Height | Inherits From | Notes |
|-----------|--------|--------------|---------------|-------|
| `SUNLU TPU 95A 0.20mm @H2S 0.4 nozzle.json` | 0.4mm | 0.20mm | `0.20mm Standard @BBL H2S` | Standard layer height |
| `SUNLU TPU 95A 0.30mm @H2S 0.6 nozzle.json` | 0.6mm | 0.30mm | `0.30mm Standard @BBL H2S 0.6 nozzle` | Larger nozzle |
| `SUNLU TPU 95A 0.40mm @H2S 0.8 nozzle.json` | 0.8mm | 0.40mm | `0.40mm Standard @BBL H2S 0.8 nozzle` | Fast printing |

**Note**: TPU does not support 0.2mm nozzles due to filament flexibility and feed path constraints.

## Key Settings Summary (Per Nozzle)

All nozzles use the same thermal settings but differ in process parameters:

| Setting | 0.4mm | 0.6mm | 0.8mm |
|---------|-------|-------|-------|
| **Layer Height** | 0.20mm | 0.30mm | 0.40mm |
| **Nozzle Temp (Std)** | 230°C | 230°C | 230°C |
| **Nozzle Temp (HF)** | 230°C | 230°C | 230°C |
| **Bed Temp** | 55°C | 55°C | 55°C |
| **Max Vol Speed (Std)** | 6 mm³/s | 6 mm³/s | 6 mm³/s |
| **Max Vol Speed (HF)** | 12 mm³/s | 12 mm³/s | 12 mm³/s |
| **Retraction Length** | 1.0mm | 1.0mm | 1.0mm |
| **Retraction Speed** | 35mm/s | 35mm/s | 35mm/s |
| **Fan Speed** | 100% | 100% | 100% |

## Recommended Build Plate

| Plate Type | Adhesion | Glue Required | Notes |
|------------|----------|---------------|-------|
| **Textured PEI** | Excellent | No | **Recommended** - Best for TPU |
| Engineering Plate | Good | No | Alternative option |
| Cool Plate | Poor | Yes | Not recommended |
| Smooth PEI | Good | No | Acceptable but harder to remove |

## Use Cases

Perfect for applications requiring:
- **Flexible seals and gaskets**
- **Shock absorbers and dampeners**
- **Protective cases and bumpers**
- **Wearable accessories (watch bands, phone cases)**
- **Functional mechanical parts with flexibility**
- **Grip surfaces and ergonomic handles**
- **Robotic soft components**
- **Sports equipment (insoles, padding)**

## Certifications

- **Global Recycled Standard (GRS)** certified
- Contains at least 50% recycled materials
- Intertek certified (TE-00320188)
- Climate Pledge Friendly
- Worker well-being protections

## Troubleshooting

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| Stringing | Retraction too fast | Use 2mm at 10mm/s (already set) |
| Under-extrusion | Speed too high for Standard nozzle | Reduce speed or use High Flow nozzle |
| Poor bed adhesion | Bed temp too low | Ensure 35°C, clean bed surface |
| Jamming | Retraction too long | Keep at 2mm maximum |
| Warping | Unlikely with TPU | Check bed level and adhesion |

## Notes

- This TPU formulation is optimized for high-speed printing (up to 120mm/s with High Flow nozzles)
- Industrial grade quality provides better layer adhesion and mechanical properties than standard TPU
- Not compatible with AMS due to Shore 95A hardness - requires manual feeding
- High Flow nozzles recommended to leverage the filament's fast-printing capabilities
- Settings verified against Bambu Lab TPU 95A HF baseline and manufacturer specifications
