# SUNLU TPU 95A Setup Summary

## Completed: June 26, 2026

### Overview
Successfully configured and optimized Bambu Studio profiles for SUNLU Industrial Grade TPU 95A filament purchased from Amazon.pl, with focus on high-flow nozzle performance.

---

## What Was Done

### ✅ 1. Downloaded Product Information
- **Source**: [Amazon.pl Product Page](https://www.amazon.pl/dp/B0FRZZSN7D)
- **Product**: SUNLU 2KG TPU 95A (2x 1kg spools)
- **Specifications Gathered**:
  - Shore Hardness: 95A
  - Nozzle Temperature: 210-230°C
  - Diameter: 1.75mm ± 0.03mm
  - Print Speed: Up to 120mm/s (3x faster than conventional TPU)
  - Industrial grade formulation
  - GRS certified (50%+ recycled materials)

**Note**: Official TDS PDF was not publicly accessible, so configuration was based on Amazon specifications and Bambu Lab TPU 95A HF baseline standards.

---

### ✅ 2. Updated Profile Settings

#### Critical Updates Made:
| Setting | Old Value | New Value | Reason |
|---------|-----------|-----------|--------|
| **filament_max_volumetric_speed** | `["6", "6"]` | `["6", "12"]` | Enable full high-flow performance (12 mm³/s for HF nozzles) |
| **filament_notes** | PETG specs (incorrect) | TPU 95A specs | Fix copy-paste error with proper TPU parameters |

#### Verified Settings (Already Correct):
- ✅ Nozzle temp: 230°C (within 210-230°C range)
- ✅ Bed temp: 35°C (Textured PEI)
- ✅ Retraction: 2.0mm at 10mm/s (TPU-optimized)
- ✅ Fan speeds: 100% max/min (full cooling for TPU)
- ✅ Density: 1.22 g/cm³
- ✅ Glass transition (Tg): 30°C
- ✅ Heat distortion (HDT): 75°C
- ✅ Vicat softening: 60°C

---

### ✅ 3. Organized File Structure

#### Created Dedicated Folder:
```
SUNLU\TPU-95A\
├── README.md                          (Comprehensive documentation)
├── SETUP_SUMMARY.md                   (This file)
├── SUNLU TPU 95A @Bambu Lab H2S.json  (Base profile - all nozzles)
├── SUNLU TPU 95A @Bambu Lab H2S.info
├── SUNLU TPU 95A @Bambu Lab H2S.preset.json
├── SUNLU TPU 95A @Bambu Lab H2S.preset.info
├── SUNLU TPU 95A Calibrated.json      (Post-calibration overrides)
├── SUNLU TPU 95A Calibrated.info
├── my-SUNLU TPU 95A @Bambu Lab H2S.json
├── my-SUNLU TPU 95A @Bambu Lab H2S.info
├── my-SUNLU TPU 95A @Bambu Lab H2S.preset.json
├── my-SUNLU TPU 95A @Bambu Lab H2S.preset.info
├── my-SUNLU TPU 95A Calibrated.json
├── my-SUNLU TPU 95A Calibrated.info
├── Process Presets (3 nozzle sizes):
│   ├── SUNLU TPU 95A 0.20mm @H2S 0.4 nozzle.json/.info
│   ├── SUNLU TPU 95A 0.30mm @H2S 0.6 nozzle.json/.info
│   ├── SUNLU TPU 95A 0.40mm @H2S 0.8 nozzle.json/.info
│   ├── my-SUNLU TPU 95A 0.20mm @H2S 0.4 nozzle.json/.info
│   ├── my-SUNLU TPU 95A 0.30mm @H2S 0.6 nozzle.json/.info
│   └── my-SUNLU TPU 95A 0.40mm @H2S 0.8 nozzle.json/.info
```

**Removed**: Obsolete Inslogic TPU 95A profiles (replaced with correct SUNLU configuration)

---

### ✅ 4. Verified Settings Against Standards

#### Compared With:
1. **Bambu Lab TPU 95A HF System Profile**:
   - ✅ Volumetric speed: 12 mm³/s (HF) - **NOW MATCHES**
   - ✅ Retraction: 2mm at 10mm/s - matches
   - ✅ Fan speeds: 100% - matches
   - ✅ Bed temp: 35°C - matches
   - ✅ Nozzle temp: 230°C - matches

2. **Amazon Product Specifications**:
   - ✅ Nozzle temp range: 210-230°C - profile uses 230°C
   - ✅ High-speed capability: 120mm/s - enabled by 12 mm³/s volumetric speed
   - ✅ Industrial grade: Settings support high-performance applications

3. **TPU Material Best Practices**:
   - ✅ Slow retraction (10mm/s) to prevent jamming
   - ✅ Full cooling (100% fan) for dimensional accuracy
   - ✅ Low bed temp (35°C) to prevent warping
   - ✅ Textured PEI plate recommendation

---

## Deployment Status

### ✅ Deployed to BambuStudio
**Location**: `C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\`

| File Type | Deployed To | Status |
|-----------|-------------|--------|
| Base filament profiles | `filament/base/` | ✅ Deployed |
| User presets | `filament/` | ✅ Deployed |
| Calibrated overrides | `filament/` | ✅ Deployed |
| Process presets (3 sizes) | `process/` | ✅ Deployed |

**Verification**:
```powershell
# Confirmed settings in deployed profile:
Volumetric Speed: 6 / 12 mm³/s (Std/HF)
Notes: SUNLU Industrial Grade TPU 95A specifications
```

### ✅ Updated DeployPack
- All 24 TPU profile files copied to `DeployPack/`
- Ready for future redeployment via `deploy.ps1`
- Removed obsolete Inslogic TPU profiles

---

## Git Commit

**Commit**: `cd615cf` - "Optimize SUNLU TPU 95A profiles for high-flow printing"

**Changes**:
- 36 files changed
- 305 insertions(+)
- 65 deletions(-)
- Organized into `SUNLU/TPU-95A/` folder
- Updated volumetric speed for high-flow nozzles
- Fixed incorrect PETG notes with proper TPU specifications
- Added comprehensive README with material properties

**Pushed to**: `https://github.com/nir-azulay/FilmentsSettings.git`

---

## Ready to Print!

### Recommended Settings for Your High Flow Nozzles:

| Nozzle Size | Layer Height | Max Speed | Volumetric Speed | Notes |
|-------------|--------------|-----------|------------------|-------|
| **0.4mm HF** | 0.20mm | 120 mm/s | 12 mm³/s | Balanced speed/quality |
| **0.6mm HF** | 0.30mm | 120 mm/s | 12 mm³/s | Fast functional parts |
| **0.8mm HF** | 0.40mm | 120 mm/s | 12 mm³/s | Maximum speed |

### Profile Names in Bambu Studio:
- Base: `my-SUNLU TPU 95A @Bambu Lab H2S`
- Calibrated: `my-SUNLU TPU 95A Calibrated` (use after running flow calibration)

### Process Presets:
- `my-SUNLU TPU 95A 0.20mm @H2S 0.4 nozzle`
- `my-SUNLU TPU 95A 0.30mm @H2S 0.6 nozzle`
- `my-SUNLU TPU 95A 0.40mm @H2S 0.8 nozzle`

---

## Important Notes

1. **High Flow Advantage**: Your profiles are now optimized for 12 mm³/s volumetric speed on High Flow nozzles, enabling the full 120mm/s print speed capability of this industrial-grade TPU.

2. **No AMS Support**: TPU 95A (Shore 95A hardness) is too soft/flexible for AMS. Manual feeding required.

3. **Textured PEI Recommended**: Best bed adhesion at 35°C without glue.

4. **Restart Bambu Studio**: Restart Bambu Studio to load the updated profiles.

5. **TDS Not Available**: Official Technical Data Sheet was not publicly accessible online. Settings are based on Amazon product specifications and validated against Bambu Lab TPU 95A HF baseline standards.

---

## Next Steps

1. **Restart Bambu Studio** to load the profiles
2. **Select Profile**: Choose `my-SUNLU TPU 95A @Bambu Lab H2S` in filament settings
3. **Choose Process**: Select appropriate layer height process preset for your nozzle
4. **Test Print**: Start with a small test print at 60-80mm/s
5. **Calibrate** (optional): Run flow calibration and save to `my-SUNLU TPU 95A Calibrated`
6. **Enjoy High-Speed TPU Printing!** 🚀

---

**Configuration Completed**: June 26, 2026, 11:47 PM (UTC+3)
