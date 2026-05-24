# Filament Stock for Home Assistant

Native Home Assistant deployment of the Filament Stock Manager. Two pieces:

| Component | Path | What it is |
|---|---|---|
| **Add-on** | [`addon/filament-stock/`](addon/filament-stock/) | Docker container with the FastAPI backend + React UI, served inside HA via Ingress. Stores data in `/data/filaments.db` (included in HA snapshots). |
| **Custom integration** | [`custom_components/filament_stock/`](custom_components/filament_stock/) | Polls the add-on and exposes one `sensor.filament_*` per filament plus services for use/restock/etc. Enables Bambu Lab cross-automations. |
| **Blueprints** | [`blueprints/automation/filament_stock/`](blueprints/automation/filament_stock/) | Importable automations: AMS depleted -> decrement, print-start out-of-stock alert, weekly digest. |

## Install

### Add-on

1. Home Assistant -> **Settings -> Add-ons -> Add-on Store -> ... -> Repositories**.
2. Paste this repo URL: `https://github.com/nir-azulay/FilmentsSettings`.
3. Scroll to the **Filament Stock for Home Assistant** section -> click **Filament Stock** -> **Install**.
4. Toggle **Show in sidebar**, **Start on boot**, **Watchdog** on.
5. Click **Start**. The **Filaments** panel appears in the HA sidebar.

### Custom integration (via HACS)

1. **HACS -> Integrations -> ... -> Custom repositories**.
2. URL: `https://github.com/nir-azulay/FilmentsSettings`, Category: **Integration**.
3. Click **Add** -> find **Filament Stock** in the list -> **Download** -> restart HA.
4. **Settings -> Devices & Services -> Add Integration -> "Filament Stock"**.

### Blueprints

Import each `.yaml` from [`blueprints/automation/filament_stock/`](blueprints/automation/filament_stock/) via **Settings -> Automations & Scenes -> Blueprints -> Import Blueprint**.

## Data location

The add-on stores SQLite at `/data/filaments.db` inside the container. On HA OS this maps to `/addon_configs/filament_stock/data/filaments.db` and is included in HA snapshots automatically.

## Migrating from a standalone QNAP install

Drop the existing `filaments.db` into `\\homeassistant\addon_configs\filament_stock\data\` (Samba share) before the first add-on start. The DB migrations in [`app/db_schema.py`](addon/filament-stock/app/db_schema.py) bring any old schema forward on startup.
