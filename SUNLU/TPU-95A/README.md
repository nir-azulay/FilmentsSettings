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
- **TDS**: Not publicly available online (settings derived from manufacturer specifications and Bambu Lab TPU 95A baseline)

## Material Properties

### Mechanical Properties
| Property | Value | Notes |
|----------|-------|-------|
| Shore Hardness | 95A | Good balance of flexibility and rigidity |
| Tensile Strength | N/A | Not specified by manufacturer |
| Elongation at Break | High | Elastic and impact-resistant |
| Impact Resistance | Excellent | Industrial-grade formulation |
| Wear Resistance | Excellent | Suitable for functional parts |

### Thermal Properties
| Property | Value | Unit |
|----------|-------|------|
| Glass Transition Temp (Tg) | 30 | °C |
| Heat Distortion Temp (HDT) | 75 | °C |
| Vicat Softening Point | 60 | °C |
| Drying Temperature | 65 | °C |
| Drying Time | 12 | hours |

### Physical Properties
| Property | Value | Unit |
|----------|-------|------|
| Density | 1.22 | g/cm³ |
| Diameter Tolerance | ±0.03 | mm |
| Shrinkage | Minimal | - |

## Manufacturer Recommended Print Settings

Based on Amazon product specifications and Bambu Lab TPU 95A HF baseline:

| Setting | Value | Notes |
|---------|-------|-------|
| **Nozzle Temperature** | 210-230°C | Use 230°C for optimal flow |
| **Bed Temperature** | 35°C | Textured PEI plate recommended |
| **Print Speed** | Up to 120 mm/s | 3x faster than conventional TPU |
| **Max Volumetric Speed** | 12 mm³/s | High Flow nozzles only |
| **Retraction Distance** | 2.0 mm | TPU-optimized |
| **Retraction Speed** | 10 mm/s | Slow for flexible filament |
| **Part Cooling Fan** | 100% | Full cooling throughout print |
| **Chamber Temperature** | Not required | - |

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
| **Bed Temp** | 35°C | 35°C | 35°C |
| **Max Vol Speed (Std)** | 6 mm³/s | 6 mm³/s | 6 mm³/s |
| **Max Vol Speed (HF)** | 12 mm³/s | 12 mm³/s | 12 mm³/s |
| **Retraction Length** | 2.0mm | 2.0mm | 2.0mm |
| **Retraction Speed** | 10mm/s | 10mm/s | 10mm/s |
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
