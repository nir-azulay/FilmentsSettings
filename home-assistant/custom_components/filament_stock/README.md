# Filament Stock custom integration

Exposes the Filament Stock add-on to Home Assistant as devices, sensors, and services so its data can be used in automations alongside the Bambu Lab integration.

## What it creates

- One **device** per filament (named e.g. "SUNLU PETG HS"). Edit its friendly name from **Settings -> Devices & Services -> Filament Stock -> the device -> pencil icon**.
- One `sensor.filament_<brand>_<material>` per filament. State = available spools. Attributes:
  - `colors` -- list of `{name, hex, status, quantity, used, available, order_id}`
  - `packaging_type`, `filament_type`, `bed_temp`, `nozzle_temp_min/max`, `density`, `amazon_url`, `low_stock_threshold`
- `binary_sensor.filament_low_stock_alert` -- `on` whenever the add-on's `/api/alerts` returns any rows.
- `sensor.filament_low_stock_count` -- numeric count of currently-firing alerts.

## Services

| Service | Purpose |
|---|---|
| `filament_stock.use_spool` | Increment `quantity_used` for a color (caps at total quantity). |
| `filament_stock.mark_arrived` | Flip a color to `in_stock`; optionally override quantity. |
| `filament_stock.add_purchase` | Add N spools to a color (creates the color if missing). |
| `filament_stock.set_status` | Force a color to `in_stock` / `ordered` / `out_of_stock`. |

All four take `filament_entity` + `color_name`.

## Auto-binding to Bambu AMS trays (no mapping needed)

The Bambu HACS integration exposes each AMS tray as a sensor whose attributes include `filament_id` and `color` (`#RRGGBBAA` hex). The Filament Stock sensors expose those same fields. The blueprints in [`../../blueprints/automation/filament_stock/`](../../blueprints/automation/filament_stock/) match on those two attributes automatically, so you only have to **pick the AMS tray sensors** when importing the blueprints -- no manual ID/color mapping table to keep in sync.

If a tray's filament has no matching Filament Stock entry (e.g. you loaded a one-off generic spool), the automation skips it silently. If you want it tracked, add the filament in the add-on first, then the next auto-match works.
