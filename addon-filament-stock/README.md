# Filament Stock add-on

3D-printer filament inventory dashboard for Home Assistant. Tracks per-color stock, fires low-stock alerts, and exposes a REST API the companion [`filament_stock` custom integration](../home-assistant/custom_components/filament_stock/) uses to surface entities and services to HA automations.

Author: **[Nir Azulay](https://github.com/nir-azulay)** -- MIT licensed, see [LICENSE](../LICENSE).

## Architecture

- **FastAPI** (Python, uvicorn) on `127.0.0.1:8000` -- REST API at `/api/*`.
- **nginx** on `:8099` -- serves the React bundle and reverse-proxies `/api/` to FastAPI. HA Ingress connects here.
- **SQLite** at `/config/data/filaments.db` -- persistent across add-on updates, included in HA snapshots, visible to the Samba share at `\\homeassistant\addon_configs\<hash>_filament_stock\data\filaments.db`.
- **s6-overlay** (from the HA base image) supervises both services and restarts the container if either dies.

## BambuStudio profile downloader (0.4.0+)

Each filament card has a **Profile** button that expands an inline panel with
two sections:

- **Filament configuration** -- the metadata you have stored for the filament:
  brand, material, type, density, nozzle and bed temps, low-stock threshold,
  Amazon URL.
- **BambuStudio profile** -- if a profile bundle ships with the add-on image
  for this filament, this section shows the base profile's key fields per
  extruder (Standard / High Flow) plus a per-nozzle table of process presets,
  each with its own **Download JSON** link. A **Download all (.zip)** button
  packages every file in the bundle ready for `user/<id>/filament/base/`,
  `user/<id>/filament/`, and `user/<id>/process/` in BambuStudio.

Bundles ship for the filaments tracked in this repo (SUNLU PETG/PETG HS/PLA/PA
E-PA/TPU 95A, Inslogic ASA/Matte PLA/Nebulux PLA/PETG Pro/PLA Pro/Silk PLA/TPU
95A), targeting the **Bambu Lab H2S**. Filaments outside that set still show
the configuration metadata; the profile section just displays a friendly empty
state and a pointer at [`.cursor/rules/add-filament.mdc`](../.cursor/rules/add-filament.mdc)
for authoring a new one.

### Keeping the bundle in sync

The `addon-filament-stock/profiles/` folder is a **build-time mirror** of
the canonical profile sources in `SUNLU/` and `Inslogic/`. It has to live
inside the add-on folder because the HA Supervisor build context can't reach
files above it. There's a repo-managed git **pre-commit hook** that takes
care of this for you:

```bash
# Once per fresh clone:
./scripts/install-git-hooks.sh
```

After that, any commit that touches a `.json` or `.info` under `SUNLU/` or
`Inslogic/` will automatically:

1. Re-run `addon-filament-stock/sync_profiles.sh` (which copies the canonical
   files into `addon-filament-stock/profiles/`, filtering out `my-*` legacy
   names, `*Calibrated*` per-printer overrides, and `baseline_full_filament`
   templates).
2. Stage the resulting changes in `addon-filament-stock/profiles/` alongside
   your original edits.

So the only "manual" rule is **install the hook once per clone**. Drift is
impossible after that. You can still run `./addon-filament-stock/sync_profiles.sh`
by hand any time -- e.g. for a quick local rebuild without committing.

After committing, the new profiles ship inside the next add-on image build.
On HA: **Settings -> Add-ons -> Filament Stock -> Update / Reinstall**.
(A plain restart will NOT pick up new profiles -- the image has to be rebuilt.)

The relevant API endpoints (used by the in-app UI; also reachable from
HA REST calls if you want):

| Endpoint | Returns |
|---|---|
| `GET /api/filaments/{id}/profile` | Metadata: which files are bundled, summary of key fields, list of nozzle entries |
| `GET /api/filaments/{id}/profile/file/{name}` | One bundled file (JSON or `.info`) as `attachment` |
| `GET /api/filaments/{id}/profile/zip` | All files for that filament packaged as a `.zip` |

## Per-color spool vs refill (0.3.0+)

Each color tracks **spool** and **refill** counts independently. The same color of the same filament can hold e.g. 2 spools + 3 refills at once, so you don't have to pick one packaging type per filament.

| Counter | Meaning |
|---|---|
| `quantity`, `quantity_used` | Spool count and spools used. The original column names; kept so older integrations and the history log keep working. |
| `quantity_refill`, `used_refill` | Refill count and refills used (added in 0.3.0). |
| `available_spool`, `available_refill`, `available_total` | Server-computed convenience fields on `GET /api/filaments`. |

Low-stock alerts treat **spools left + refills left** as the available pool for a color, so a filament with no spools but plenty of refills won't fire a low-stock alert.

The UI shows two side-by-side pills per color row, each with its own +Add and Use buttons. A pill is dimmed (but still has +Add) when its counter is zero, so you can start tracking the other packaging type any time without re-creating the color.

When a 0.2.x database upgrades to 0.3.0, the migration in [`app/db_schema.py`](app/db_schema.py) automatically moves data off the dropped `filaments.packaging_type`: colors whose parent filament was a `refill` get their `quantity` / `quantity_used` shifted into `quantity_refill` / `used_refill` and the spool counters zeroed. Run is idempotent and safe on snapshots.

## Data

| Path inside container | Samba path on host | What |
|---|---|---|
| `/config/data/filaments.db` | `\\homeassistant\addon_configs\<hash>_filament_stock\data\filaments.db` | SQLite database (filaments, color stocks, history, alert ignores) |
| `/app/app/` | -- | FastAPI source |
| `/usr/share/nginx/html/` | -- | Built React bundle |
| `/etc/nginx/nginx.conf` | -- | nginx config |

The `<hash>_` prefix on the Samba folder is assigned per-install by HA Supervisor; you'll see something like `4a1dd1d6_filament_stock`. It's stable for the life of the install.

### Seeding from an existing database

Stop the add-on, drop your `filaments.db` into `\\homeassistant\addon_configs\<hash>_filament_stock\data\` (overwriting the file the add-on created on first start), then start the add-on. Schema migrations in [`app/db_schema.py`](app/db_schema.py) upgrade older databases automatically.

To verify the DB loaded with your data, check the **Log** tab for the line:

```
DB ready: DATABASE_URL=sqlite:////config/data/filaments.db file_size=<size> filaments=<count> color_stocks=<count>
```

## Configuration

The add-on has no user-configurable options today. Future versions may expose database backup interval and alert defaults.

## Companion integration

The [`filament_stock` custom integration](../home-assistant/custom_components/filament_stock/) -- installed separately via HACS -- polls this add-on's `/api/` and exposes one `sensor.filament_*` per filament plus four services (`use_spool`, `add_purchase`, `set_status`, `mark_arrived`) usable from HA automations. The [companion blueprints](../home-assistant/blueprints/automation/filament_stock/) wire those services to your Bambu Lab integration so AMS trays going empty auto-decrement stock.

## Author

**Nir Azulay** -- <https://github.com/nir-azulay>
