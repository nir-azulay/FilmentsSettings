# Filament Stock -- custom integration

Surfaces the [Filament Stock add-on](../../../addon-filament-stock/) as Home Assistant devices, sensors, and services so its data can drive automations alongside the [Bambu Lab integration](https://github.com/greghesp/ha-bambulab).

Author: **[Nir Azulay](https://github.com/nir-azulay)** -- MIT licensed, see [LICENSE](../../../LICENSE).

## Requirements

- The companion [Filament Stock add-on](../../../addon-filament-stock/) installed and running.
- Home Assistant **2024.6** or later.
- [HACS](https://hacs.xyz/) for installation.

## Install via HACS

1. **HACS -> Integrations**, top-right **... menu -> Custom repositories**.
2. URL: `https://github.com/nir-azulay/FilmentsSettings`, Category: **Integration**. **Add**.
3. Find **Filament Stock** in the HACS list -> **Download**.
4. Restart Home Assistant.
5. **Settings -> Devices & Services -> Add Integration -> "Filament Stock"**.
6. Accept the default Base URL. The config flow auto-discovers the add-on's hostname on the HA docker network; override only if you run the backend elsewhere.

## What it creates

- One **device** per filament (named e.g. "SUNLU PETG HS"). Rename from **Settings -> Devices & Services -> Filament Stock -> the device -> pencil icon**.
- One `sensor.filament_<brand>_<material>` per filament. State = total available spools (sum of `quantity - quantity_used` over in-stock colors). Attributes:
  - `colors` -- list of `{name, hex, status, quantity, used, available, order_id}`
  - `packaging_type`, `filament_type`, `bed_temp`, `nozzle_temp_min/max`, `density`, `amazon_url`, `low_stock_threshold`, `filament_id`
- `binary_sensor.filament_low_stock_alert` -- `on` whenever `/api/alerts` returns any rows (device class: `problem`).
- `sensor.filament_low_stock_count` -- numeric count of currently-firing alerts.

## Services

| Service | Purpose |
|---|---|
| `filament_stock.use_spool` | Increment `quantity_used` for a color (caps at total quantity). |
| `filament_stock.mark_arrived` | Flip a color to `in_stock`; optionally override quantity. |
| `filament_stock.add_purchase` | Add N spools to a color (creates the color if missing). |
| `filament_stock.set_status` | Force a color to `in_stock` / `ordered` / `out_of_stock`. |

All four take `filament_entity` (a `sensor.filament_*` entity) + `color_name` (case-insensitive match against the color name shown in the dashboard).

## Auto-binding to Bambu AMS trays (no mapping needed)

The Bambu HACS integration exposes each AMS tray as a sensor whose attributes include `filament_id` and `color` (`#RRGGBBAA`). The Filament Stock sensors expose those same fields. The [blueprints](../../blueprints/automation/filament_stock/) match on those two attributes automatically, so when importing a blueprint you only pick the AMS tray sensors -- no manual ID/color mapping table to keep in sync.

If a tray's filament has no matching Filament Stock entry (e.g. you loaded a one-off generic spool), the automation skips it silently. Add the filament in the add-on's UI, and the next auto-match works.

## Author

**Nir Azulay** -- <https://github.com/nir-azulay>
