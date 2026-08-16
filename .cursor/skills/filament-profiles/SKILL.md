---
name: filament-profiles
description: Configure Bambu Studio filament profiles from TDS specifications. Use when adding new filaments, tuning print settings, fixing profile issues, or when the user mentions TDS, filament, nozzle temperature, retraction, volumetric speed, or print quality problems.
---

# Filament Profile Configuration

Configure Bambu Studio Beta filament profiles based on manufacturer TDS (Technical Data Sheet) specifications for the Bambu Lab H2C printer.

## Workflow Overview

1. **Get TDS** - User provides TDS PDF link or product page
2. **Extract parameters** - Read TDS and extract all printing specifications
3. **User creates filament** - Via Bambu Studio Beta wizard (creates filament_id)
4. **Configure profile** - Apply TDS-based settings to all nozzle variants
5. **Deploy** - Copy to DeployPack for version control

## File Locations

| Type | Path |
|------|------|
| Base profiles | `C:\Users\Nir\AppData\Roaming\BambuStudioBeta\user\2189385007\filament\base\` |
| User presets | `C:\Users\Nir\AppData\Roaming\BambuStudioBeta\user\2189385007\filament\` |
| System reference | `C:\Users\Nir\AppData\Roaming\BambuStudioBeta\system\BBL\filament\` |
| DeployPack | `c:\GitHub\filments settings\DeployPack\` |

## TDS Parameters to Extract

### Material Properties
| TDS Field | Profile Setting |
|-----------|-----------------|
| Density (g/cm³) | `filament_density` |
| Glass Transition Tg (°C) | `temperature_vitrification` |
| HDT Heat Distortion (°C) | `filament_dev_ams_drying_heat_distortion_temperature` |
| Vicat Softening (°C) | `filament_dev_drying_softening_temperature` |
| Drying Temperature (°C) | `filament_dev_ams_drying_temperature` |

### Print Settings
| TDS Field | Profile Setting |
|-----------|-----------------|
| Nozzle Temp range | `nozzle_temperature`, `nozzle_temperature_initial_layer` |
| Bed Temp range | `hot_plate_temp`, `textured_plate_temp` |
| Retraction Distance | `filament_retraction_length` |
| Retraction Speed | `filament_retraction_speed`, `filament_deretraction_speed` |
| Max Print Speed | Calculate `filament_max_volumetric_speed` |

## Mandatory Settings (Wizard Gets Wrong)

These MUST be fixed after wizard creates the profile:

| Setting | Required Value | Reason |
|---------|---------------|--------|
| `enable_pressure_advance` | `"1"` | Must be enabled for quality |
| `filament_retraction_speed` | Explicit value (e.g., `"35"`) | `"nil"` causes extrusion issues |
| `filament_deretraction_speed` | Match retraction speed | `"nil"` causes issues |
| `filament_start_gcode` | Aux fan control (see below) | Chamber ventilation |

## Fan Speeds by Material

| Material | fan_max_speed | fan_min_speed | overhang_fan_speed |
|----------|---------------|---------------|-------------------|
| PLA | 100% | 100% | 90% |
| PETG | 60% | 20% | 50% |
| ASA | 35% | 10% | 80-100% |
| PA/Nylon | 30% | 10% | 50% |
| TPU | 100% | 100% | 100% |

## Filament Start Gcode (PLA/PETG)

```
; filament start gcode\n{if (bed_temperature[current_extruder] >80)||(bed_temperature_initial_layer[current_extruder] >80)}M106 P3 S255\n{elsif (bed_temperature[current_extruder] >60)||(bed_temperature_initial_layer[current_extruder] >60)}M106 P3 S180\n{endif}\n\n{if activate_air_filtration[current_extruder] && support_air_filtration}\nM106 P3 S{during_print_exhaust_fan_speed_num[current_extruder]} \n{endif}
```

## ASA Start Gcode (Keep Chamber Sealed)

```
; filament start gcode\n; ASA: Keep chamber sealed, no aux fan\nM106 P3 S0
```

## Nozzle Temperature Strategy

TDS usually provides a range (e.g., 205-245°C). Configure based on extruder type:

| Extruder | Temperature | Reason |
|----------|-------------|--------|
| Standard | Mid-low of TDS range | Lower speeds, quality focus |
| High Flow | Mid-high of TDS range (+10-15°C) | Higher speeds need more heat |
| E3D High Flow | Same as High Flow | Same capability |

## Volumetric Speed Calculation

MVS (mm³/s) = layer_height × line_width × speed

Typical ranges by nozzle:
| Nozzle | Standard | High Flow |
|--------|----------|-----------|
| 0.2mm | 10-15 | 12-18 |
| 0.4mm | 20-28 | 35-54 |
| 0.6mm | 25-32 | 40-54 |
| 0.8mm | 28-35 | 42-55 |

## Extruder Array Structure

Profiles use arrays for extruder-specific values:
- **0.2mm nozzle**: 2 values `[Standard, HF]`
- **0.4/0.6mm nozzle**: 3 values `[Standard, HF, E3D HF]`
- **0.8mm nozzle**: 2 values `[Standard, HF]`

Example:
```json
"nozzle_temperature": ["220", "235", "235"],
"filament_max_volumetric_speed": ["25", "42", "42"]
```

## Common Mistakes & Fixes

### PETG Stringing
- **Cause**: Fan too high (80-90%), freezes outer shell while core stays molten
- **Fix**: Match Bambu PETG fan speeds (max 60%, min 20%, overhang 50%)

### ASA Not Extruding / Calibration Failure
- **Cause**: Fan at 100% (should be 35%), temps too low, pressure advance disabled
- **Fix**: Match Bambu ASA profile exactly - fan 35%, temp 270°C, enable PA

### ASA Support Disconnecting
- **Cause**: Z-hop missing, travel moves hit warped parts
- **Fix**: Add explicit Z-hop (0.4-0.6mm), increase textured plate temp to 105-110°C

### 0.2mm Nozzle Broken MVS
- **Cause**: Wizard often sets MVS to 1-2 mm³/s
- **Fix**: Set appropriate values (12-18 mm³/s)

### Nil Retraction Values
- **Cause**: Wizard sets `"nil"` for retraction/deretraction speed
- **Fix**: Always set explicit values (35mm/s is safe default)

## Build Plate Recommendations

| Material | Best Plate | Glue? |
|----------|-----------|-------|
| PLA | Any (avoid Engineering) | No |
| PETG | Textured PEI | No (never smooth PEI!) |
| ASA | Engineering plate | Yes |
| PA/Nylon | Textured PEI | Yes (required) |
| TPU | Textured PEI | No |

## Profile Identity Fields (DO NOT MODIFY)

These are created by the wizard and must not be changed:
- `filament_id`
- `filament_settings_id`
- `name`
- `inherits`
- `.info` file contents

## Deploy to BambuStudioBeta

After configuring, copy to DeployPack:
```powershell
Copy-Item "C:\Users\Nir\AppData\Roaming\BambuStudioBeta\user\2189385007\filament\base\<Filament Name> @Bambu Lab H2C*" -Destination "c:\GitHub\filments settings\DeployPack\" -Force
```

## JSON Formatting

- Version: `"2.8.0.4"`
- Use Python `json.dump(indent=4, sort_keys=True)` for consistency
- Never use PowerShell `ConvertTo-Json` (wrong indentation)
- `.info` files: ASCII, no BOM, Unix line endings
