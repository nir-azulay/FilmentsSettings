# Filament Stock for Home Assistant

Native Home Assistant deployment of the Filament Stock Manager. Three pieces:

| Component | Path | What it is |
|---|---|---|
| **Add-on** | [`../addon-filament-stock/`](../addon-filament-stock/) | Docker container with the FastAPI backend + React UI, served inside HA via Ingress. Stores data in `/data/filaments.db` (included in HA snapshots). Installed via the HA add-on store. |
| **Custom integration** | [`custom_components/filament_stock/`](custom_components/filament_stock/) | Polls the add-on and exposes one `sensor.filament_*` per filament plus services for use/restock/etc. Installed via HACS. |
| **Blueprints** | [`blueprints/automation/filament_stock/`](blueprints/automation/filament_stock/) | Importable automations: AMS tray emptied -> decrement, print-start out-of-stock alert, weekly digest. |

The HA Supervisor add-on protocol requires `repository.json` and the add-on folder to live at the **repo root**, so `addon-filament-stock/` sits there. Everything else (integration, blueprints) lives under `home-assistant/`.

## Install

### 1. Add-on

1. Home Assistant -> **Settings -> Add-ons -> Add-on Store**, then the **... menu (top-right) -> Repositories**.
2. Paste this repo URL: `https://github.com/nir-azulay/FilmentsSettings`. Click **Add**, then **Close**.
3. Scroll the store list. A new section **"Filament Stock for Home Assistant"** appears with one add-on: **Filament Stock**. Click it -> **Install** (HA OS will build the image, takes 5-10 min the first time).
4. After install: enable **Show in sidebar**, **Start on boot**, **Watchdog**. Click **Start**.
5. The **Filaments** panel appears in the HA sidebar. Open it to confirm the UI loads (empty DB on a fresh install).

### 2. Custom integration (via HACS)

1. **HACS -> Integrations -> ... menu -> Custom repositories**.
2. URL: `https://github.com/nir-azulay/FilmentsSettings`, Category: **Integration**.
3. **Add** -> click **Filament Stock** in the list -> **Download** -> restart HA.
4. **Settings -> Devices & Services -> Add Integration -> "Filament Stock"**. Accept the default base URL (`http://addon_filament_stock:8099`) unless you changed the slug.

### 3. Blueprints

Import each `.yaml` from [`blueprints/automation/filament_stock/`](blueprints/automation/filament_stock/) via **Settings -> Automations & Scenes -> Blueprints -> Import Blueprint** (paste the raw GitHub URL of the file).

## Data location

The add-on stores SQLite at `/data/filaments.db` inside the container. On HA OS this maps to `/addon_configs/filament_stock/data/filaments.db` and is included in HA snapshots automatically.

## Migrating from a standalone QNAP install

Drop the existing `filaments.db` into `\\homeassistant\addon_configs\filament_stock\data\` (Samba share) before the first add-on start. The DB migrations in [`../addon-filament-stock/app/db_schema.py`](../addon-filament-stock/app/db_schema.py) bring any old schema forward on startup.
