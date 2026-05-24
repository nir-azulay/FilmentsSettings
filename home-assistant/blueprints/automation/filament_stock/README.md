# Filament Stock blueprints

Three importable automations that connect the [Filament Stock integration](../../../custom_components/filament_stock/) with your Bambu Lab printer.

| File | What it does |
|---|---|
| [`ams_tray_emptied_decrement.yaml`](ams_tray_emptied_decrement.yaml) | When an AMS tray transitions to "Empty", auto-match the tray's previously loaded `filament_id` + `color` against Filament Stock and call `filament_stock.use_spool`. One automation per tray you want auto-decrementing. |
| [`print_start_out_of_stock.yaml`](print_start_out_of_stock.yaml) | When the printer state transitions to `printing`, scan every loaded AMS tray, auto-match to Filament Stock, and notify if any is out of stock or below threshold. |
| [`weekly_low_stock_digest.yaml`](weekly_low_stock_digest.yaml) | Reads `binary_sensor.filament_low_stock_alert` and sends a weekly summary. |

## Auto-binding by `filament_id` + `color`

The Bambu HACS integration exposes per-tray sensors whose attributes include `filament_id` (e.g. `P6306ce1` for your custom SUNLU PETG-HS) and `color` (`#RRGGBBAA`). The Filament Stock integration mirrors these on its own sensors. The blueprints match on both, so:

- You **don't** maintain a mapping table.
- When you move a spool to a different tray, the binding follows automatically.
- Unknown filaments (no match in Filament Stock) are skipped silently.

## Import

**Settings -> Automations & Scenes -> Blueprints -> Import Blueprint -> paste the raw GitHub URL of any of the YAML files above.**

Then **Create Automation** from the imported blueprint and fill in the input fields.

## Required Bambu integration entities (verified against HACS Bambu Lab v2.2.22 + an H2S)

| Purpose | Example entity (your serial is the prefix) |
|---|---|
| Per-tray content | `sensor.h2s_<serial>_ams_1_tray_4` (state = "SUNLU PETG High Speed", attrs `filament_id`, `color`, `remain_enabled`) |
| Printer current stage | `sensor.h2s_<serial>_current_stage` (state value `printing` when actively printing) |
| External spool | `sensor.h2s_<serial>_externalspool_external_spool` (same attribute schema as AMS tray) |

## Why "state -> Empty" instead of "remain percent below threshold"

The Bambu integration's `remain` attribute is `-1` for any spool whose RFID weight tracking isn't reporting (the common case). We instead trigger on the explicit `Empty` state transition, which fires reliably the moment you remove a finished spool and the tray reports empty.
