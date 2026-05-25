# FilmentsSettings

3D-printing toolkit for [Bambu Lab](https://bambulab.com/) printers built and maintained by **[Nir Azulay](https://github.com/nir-azulay)**. Two independent pieces share this repo:

| What | Where |
|---|---|
| **Filament Stock for Home Assistant** -- native HA add-on + integration + blueprints for tracking spools and wiring them to AMS automations | [`addon-filament-stock/`](addon-filament-stock/) + [`home-assistant/`](home-assistant/) |
| **Bambu Lab filament profiles** -- tested filament + process JSON profiles for the H2S, with the generators that produced them | [`SUNLU/`](SUNLU/), [`Inslogic/`](Inslogic/), [`DeployPack/`](DeployPack/) |

## Filament Stock for Home Assistant

Inventory dashboard, low-stock alerts, and full Home Assistant integration so your AMS trays auto-decrement spools, your push notifications fire when a print starts on a depleted color, and your weekly digest shows what to restock.

**[Setup guide -> home-assistant/README.md](home-assistant/README.md)**

Components:
- [`addon-filament-stock/`](addon-filament-stock/) -- HA Supervisor add-on (FastAPI + React + SQLite, served via HA Ingress).
- [`home-assistant/custom_components/filament_stock/`](home-assistant/custom_components/filament_stock/) -- HACS integration that exposes one `sensor.filament_*` per filament plus 4 services for use/restock automations.
- [`home-assistant/blueprints/automation/filament_stock/`](home-assistant/blueprints/automation/filament_stock/) -- three importable automations bridging Bambu Lab and Filament Stock.

## Bambu filament profiles

Per-filament folders contain Bambu Studio user profile JSONs, process presets, and the manufacturer TDS PDF. A Python generator script drives them so changes propagate consistently across all four nozzle sizes (0.2 / 0.4 / 0.6 / 0.8mm).

The full workflow for adding a new filament is documented in [`.cursor/rules/add-filament.mdc`](.cursor/rules/add-filament.mdc).

## Author

**Nir Azulay** -- <https://github.com/nir-azulay>

## License

MIT -- see [LICENSE](LICENSE).
