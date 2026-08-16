# Filament Profile Examples

## SUNLU PLA+ (TDS: SL-TE-WI-080)

### TDS Extracted Values
| Property | TDS Value |
|----------|-----------|
| Density | 1.21 g/cm³ |
| Tg | 61°C |
| HDT | 56°C |
| Vicat | 54°C |
| Nozzle Temp | 205-215°C @ 50-100mm/s, 215-245°C @ 100-200mm/s |
| Bed Temp | 50-60°C |
| Retraction | 0.8-1.2mm @ 30-40mm/s |
| Drying | 50°C |

### Applied Configuration
```json
"filament_density": ["1.21"],
"temperature_vitrification": ["61"],
"filament_dev_ams_drying_heat_distortion_temperature": ["56"],
"filament_dev_drying_softening_temperature": ["54"],
"filament_dev_ams_drying_temperature": ["50", "50", "50", "50"],
"enable_pressure_advance": ["1"],
"filament_retraction_length": ["1.0", "1.0", "1.0"],
"filament_retraction_speed": ["35", "35", "35"],
"filament_deretraction_speed": ["35", "35", "35"],
"fan_max_speed": ["100"],
"fan_min_speed": ["100"],
"nozzle_temperature": ["220", "235", "235"],
"nozzle_temperature_initial_layer": ["220", "235", "235"],
"hot_plate_temp": ["55"],
"textured_plate_temp": ["55"]
```

### Volumetric Speeds Applied
| Nozzle | Standard | HF |
|--------|----------|-----|
| 0.2mm | 12 | 15 |
| 0.4mm | 25 | 42 |
| 0.6mm | 30 | 45 |
| 0.8mm | 32 | 48 |

---

## SUNLU PETG High Speed (TDS: SL-TE-WI-062)

### TDS Extracted Values
| Property | TDS Value |
|----------|-----------|
| Density | 1.28 g/cm³ |
| Tg | 65.5°C |
| HDT | 70°C |
| Nozzle Temp | 240-260°C |
| Bed Temp | 60-70°C |
| Retraction | 0.8-1.2mm @ 30-40mm/s |

### Applied Configuration
```json
"filament_density": ["1.28"],
"temperature_vitrification": ["66"],
"filament_dev_ams_drying_heat_distortion_temperature": ["70"],
"enable_pressure_advance": ["1"],
"filament_retraction_length": ["1.0"],
"filament_retraction_speed": ["35", "40"],
"filament_deretraction_speed": ["35", "40"],
"fan_max_speed": ["60"],
"fan_min_speed": ["20"],
"overhang_fan_speed": ["50"],
"nozzle_temperature": ["245", "255"],
"hot_plate_temp": ["70"],
"textured_plate_temp": ["70"]
```

---

## Inslogic PETG Pro (High Speed 600mm/s)

### Applied Configuration for High Speed
```json
"filament_max_volumetric_speed": ["18", "54", "54"],  // 0.4mm nozzle
"nozzle_temperature": ["245", "265", "265"],
"fan_max_speed": ["100"],
"fan_min_speed": ["50"]
```

---

## Inslogic ASA Basic

### Key Settings for Adhesion
```json
"filament_start_gcode": ["; filament start gcode\\n; ASA: Keep chamber sealed, no aux fan\\nM106 P3 S0"],
"filament_z_hop": ["0.4", "0.4"],  // 0.2mm nozzle
"filament_z_hop": ["0.5", "0.5", "0.5"],  // 0.4/0.6mm nozzle
"filament_z_hop": ["0.6", "0.6"],  // 0.8mm nozzle
"textured_plate_temp": ["105"],
"textured_plate_temp_initial_layer": ["110"]
```

---

## Lessons Learned Summary

### 1. Never Trust Wizard Defaults
The Bambu Studio wizard creates profiles with many broken settings:
- `enable_pressure_advance: "0"` → Always set to `"1"`
- `filament_retraction_speed: "nil"` → Always explicit values
- `filament_max_volumetric_speed` for 0.2mm → Often 1-2, should be 10-18

### 2. Fan Speed Is Material-Specific
Never blindly copy fan speeds between materials:
- PLA needs maximum cooling (100%)
- PETG needs moderate cooling (60% max)
- ASA needs minimal cooling (35% max)

### 3. HF Nozzles Need Higher Temps
High Flow nozzles push more plastic faster, requiring +10-20°C:
- Standard: Use TDS mid-range
- HF: Use TDS high-range or +15°C above standard

### 4. Retraction Prevents Stringing
TDS retraction values are reliable:
- Typical range: 0.8-1.2mm
- Speed: 30-40mm/s
- Always set both retraction AND deretraction speed

### 5. ASA Needs Chamber Control
ASA warps with temperature changes:
- Disable aux fan (M106 P3 S0)
- Use higher bed temps on textured PEI (105-110°C)
- Add Z-hop to prevent nozzle collisions with warped parts

### 6. Build Plate Selection Matters
- Never use smooth PEI for PETG (bonds permanently)
- Engineering plate is best for ASA
- Textured PEI works for most materials with proper temps
