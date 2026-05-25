# Filament Stock blueprints

Three importable automations that wire the [Filament Stock integration](../../../custom_components/filament_stock/) to your Bambu Lab printer.

Author: **[Nir Azulay](https://github.com/nir-azulay)** -- MIT licensed, see [LICENSE](../../../../LICENSE).

## What's here

| File | What it does |
|---|---|
| [`ams_tray_emptied_decrement.yaml`](ams_tray_emptied_decrement.yaml) | When an AMS tray transitions to "Empty", auto-match the tray's previously loaded `filament_id` + `color` against Filament Stock and call `filament_stock.use_spool`. Create one automation per tray you want auto-decrementing. |
| [`print_start_out_of_stock.yaml`](print_start_out_of_stock.yaml) | When the printer's `current_stage` becomes `printing`, scan every loaded AMS tray, auto-match to Filament Stock, and notify if any color is out of stock or below threshold. |
| [`weekly_low_stock_digest.yaml`](weekly_low_stock_digest.yaml) | Reads `binary_sensor.filament_low_stock_alert` once a week and sends a summary notification. |

## Auto-binding by `filament_id` + `color`

The Bambu HACS integration exposes per-tray sensors whose attributes include `filament_id` (e.g. `P6306ce1` for a custom SUNLU PETG-HS) and `color` (`#RRGGBBAA`). The Filament Stock integration mirrors those on its own sensors. The blueprints match on both, so:

- You **don't** maintain a mapping table.
- Moving a spool to a different tray re-binds automatically.
- Unknown filaments (no Filament Stock match) are skipped silently.

## Import

For each `.yaml` above:

1. **Settings -> Automations & Scenes -> Blueprints -> Import Blueprint**.
2. Paste the raw GitHub URL of the file.
3. **Create Automation** from the new blueprint and fill in the input fields.

## Bambu integration entities (verified against HACS Bambu Lab v2.2.22 + H2S)

| Purpose | Example entity (your printer's serial is the prefix) |
|---|---|
| Per-tray content | `sensor.h2s_<serial>_ams_1_tray_4` (state = `"SUNLU PETG High Speed"` etc.; attrs `filament_id`, `color`, `remain_enabled`) |
| Printer current stage | `sensor.h2s_<serial>_current_stage` (value `printing` while actively printing) |
| External spool | `sensor.h2s_<serial>_externalspool_external_spool` (same attribute schema as an AMS tray) |

Other Bambu printer models (P1S, X1C, A1, etc.) should work identically as long as the Bambu integration exposes the same `filament_id` + `color` attributes on tray sensors.

## Design note: why "state -> Empty" and not "remain % below threshold"

The Bambu integration's `remain` attribute is `-1` for any spool whose RFID weight tracking isn't reporting -- which is most spools, unless you're using Bambu's first-party AMS-aware filament. Triggering on the explicit `Empty` state transition fires reliably the moment you remove a finished spool and the tray reports empty, regardless of whether the spool had an RFID tag.

## Author

**Nir Azulay** -- <https://github.com/nir-azulay>
