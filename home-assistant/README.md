# Filament Stock for Home Assistant

Track your 3D-printer filament inventory inside Home Assistant, and let your AMS-equipped printer keep that inventory accurate automatically.

Built and maintained by **[Nir Azulay](https://github.com/nir-azulay)**. MIT licensed -- see [LICENSE](../LICENSE).

## What you get

| Component | Path | What it does |
|---|---|---|
| **Add-on** | [`../addon-filament-stock/`](../addon-filament-stock/) | Docker container with a FastAPI backend + React UI, served inside HA via Ingress. Stores `filaments.db` at `/config/data/filaments.db` (visible to Samba, included in HA snapshots). Tracks spools and refills independently per color. Adds a **Filaments** panel to your HA sidebar. |
| **Custom integration** | [`custom_components/filament_stock/`](custom_components/filament_stock/) | Polls the add-on and exposes one `sensor.filament_*` per filament (with per-color spool/refill breakdowns in attributes), a `binary_sensor.filament_low_stock_alert`, and four services (`use_spool`, `add_purchase`, `set_status`, `mark_arrived`). |
| **Blueprints** | [`blueprints/automation/filament_stock/`](blueprints/automation/filament_stock/) | Three importable automations: AMS tray emptied -> decrement stock; print-start out-of-stock alert; weekly low-stock digest. |

Why three pieces? The HA Supervisor add-on protocol requires `repository.json` and the add-on folder at the repo root, so [`addon-filament-stock/`](../addon-filament-stock/) sits there. The integration and blueprints (consumed by HACS and the blueprint importer, both of which accept arbitrary paths) live under [`home-assistant/`](.) to keep them logically grouped.

## Requirements

- Home Assistant OS or Supervised, **2024.6** or later (HACS-compatible).
- [HACS](https://hacs.xyz/) installed.
- Optional but needed for the blueprints: the [Bambu Lab HACS integration](https://github.com/greghesp/ha-bambulab) (verified compatible: v2.2.22) configured against your printer.

## Install

### 1. Add-on (the inventory dashboard)

1. Home Assistant -> **Settings -> Add-ons -> Add-on Store**, top-right **... menu -> Repositories**.
2. Add: `https://github.com/nir-azulay/FilmentsSettings`. **Add**, then **Close**.
3. Scroll the store. Open **"Filament Stock for Home Assistant" -> Filament Stock -> Install** (HA OS will build the image, ~5-10 min the first time).
4. Enable **Show in sidebar**, **Start on boot**, **Watchdog**. Click **Start**.
5. The **Filaments** panel appears in the sidebar. Open it -- empty on a fresh install.

### 2. Custom integration (HA sensors + services)

1. **HACS -> Integrations**, top-right **... menu -> Custom repositories**.
2. URL: `https://github.com/nir-azulay/FilmentsSettings`, Category: **Integration**. Click **Add**.
3. In the HACS integrations list, find **Filament Stock** -> **Download** -> **Restart Home Assistant**.
4. **Settings -> Devices & Services -> Add Integration -> "Filament Stock"**.
5. Accept the default Base URL (the integration auto-discovers the add-on hostname). Submit.

You should now see 14+ new entities under **Settings -> Devices & Services -> Filament Stock**: one sensor per filament plus the low-stock binary sensor.

### 3. Blueprints (Bambu cross-automations)

For each `.yaml` in [`blueprints/automation/filament_stock/`](blueprints/automation/filament_stock/):

1. **Settings -> Automations & Scenes -> Blueprints -> Import Blueprint**.
2. Paste the raw GitHub URL of the file, e.g.
   `https://github.com/nir-azulay/FilmentsSettings/blob/main/home-assistant/blueprints/automation/filament_stock/ams_tray_emptied_decrement.yaml`.
3. **Create Automation** from the imported blueprint, pick the Bambu tray sensor(s) and your notification target.

See the [blueprints README](blueprints/automation/filament_stock/README.md) for the exact Bambu entity names to choose.

## Data location

The add-on stores SQLite at `/config/data/filaments.db` inside its container. On HA OS this maps to `\\homeassistant\addon_configs\<hash>_filament_stock\data\filaments.db` (the hash prefix is per-install). The folder is included in HA snapshots automatically.

To inspect or back up the DB: mount that Samba path from your Mac/PC and copy the file.

## Seeding the database from a backup

1. Stop the HA add-on.
2. Drop your existing `filaments.db` into `\\homeassistant\addon_configs\<hash>_filament_stock\data\filaments.db`, overwriting the empty seed file.
3. Start the HA add-on. Schema migrations in [`../addon-filament-stock/app/db_schema.py`](../addon-filament-stock/app/db_schema.py) bring older databases forward on first start.
4. Confirm row counts in **Log tab -> `DB ready:` line**.

## Author

**Nir Azulay** -- <https://github.com/nir-azulay>
