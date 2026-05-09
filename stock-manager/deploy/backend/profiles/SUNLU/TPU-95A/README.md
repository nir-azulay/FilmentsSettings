# SUNLU TPU 95A

## Product Info

| Property | Value |
|----------|-------|
| Brand | SUNLU |
| Material | TPU 95A |
| Diameter | 1.75mm |
| Shore Hardness | 95A |
| Tolerance | ±0.03mm |
| Weight | 1kg per spool |
| Density | 1.22 g/cm³ |

## Links

- **Amazon:** https://www.amazon.pl/dp/B0FRZZSN7D
- **Manufacturer:** https://www.sunlu.com

## Manufacturer Recommended Print Settings

| Parameter | Value |
|-----------|-------|
| Nozzle Temperature | 210–230°C |
| Bed Temperature | 30–35°C |
| Print Speed | 20–40 mm/s (up to 120 mm/s claimed) |
| Retraction | Minimal (flexible material) |
| Compatible with AMS | No (too soft) |

## Material Properties

| Property | Value |
|----------|-------|
| Shore Hardness | 95A |
| Density | 1.22 g/cm³ |
| Heat Distortion Temp | ~45°C |
| Vitrification (Tg) | ~30°C |
| Elongation at Break | High (flexible) |
| Impact Resistance | Excellent |
| Wear Resistance | Excellent |
| Elasticity | High |

## Notes

- TPU 95A is **NOT compatible with AMS** — must feed from external spool holder
- Only supports **0.4, 0.6, 0.8mm nozzles** on H2S (no 0.2mm support)
- Requires **Direct Drive** extruder (not Bowden)
- Very low retraction (2mm at 10mm/s) to prevent jamming
- Maximum cooling fan (100%) for best surface quality
- Print slowly for best results — TPU is flexible and can buckle in feed path
- Compatible with Bambu Lab H2S (confirmed by SUNLU and Bambu system profiles)

## Profile Files

| File | Nozzle | Layer Height | Key Settings |
|------|--------|-------------|--------------|
| my-SUNLU TPU 95A @Bambu Lab H2S 0.4 nozzle.json | 0.4mm | — | 230°C, 35°C bed, 2mm retract @10mm/s |
| my-SUNLU TPU 95A @Bambu Lab H2S 0.6 nozzle.json | 0.6mm | — | 230°C, 35°C bed, 2mm retract @10mm/s |
| my-SUNLU TPU 95A @Bambu Lab H2S 0.8 nozzle.json | 0.8mm | — | 230°C, 35°C bed, 2mm retract @10mm/s |
| my-SUNLU TPU 95A 0.20mm @H2S 0.4 nozzle.json | 0.4mm | 0.20mm | 30-50mm/s walls, gyroid infill |
| my-SUNLU TPU 95A 0.30mm @H2S 0.6 nozzle.json | 0.6mm | 0.30mm | 30-50mm/s walls, gyroid infill |
| my-SUNLU TPU 95A 0.40mm @H2S 0.8 nozzle.json | 0.8mm | 0.40mm | 30-50mm/s walls, gyroid infill |
| my-SUNLU TPU 95A Calibrated.json | 0.4mm | — | Flow ratio 0.98, PA 0.04 |

## Recommended Build Plate

| Plate | Glue? | Notes |
|-------|-------|-------|
| Textured PEI | No | Good adhesion + easy release |
| Cool Plate | No | Also works well |
| Engineering Plate | No | OK but may stick too hard |
