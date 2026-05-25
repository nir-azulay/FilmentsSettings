# Filament Stock add-on

3D-printer filament inventory dashboard for Home Assistant. Tracks per-color stock, fires low-stock alerts, and exposes a REST API the companion [`filament_stock` custom integration](../home-assistant/custom_components/filament_stock/) uses to surface entities and services to HA automations.

Author: **[Nir Azulay](https://github.com/nir-azulay)** -- MIT licensed, see [LICENSE](../LICENSE).

## Architecture

- **FastAPI** (Python, uvicorn) on `127.0.0.1:8000` -- REST API at `/api/*`.
- **nginx** on `:8099` -- serves the React bundle and reverse-proxies `/api/` to FastAPI. HA Ingress connects here.
- **SQLite** at `/config/data/filaments.db` -- persistent across add-on updates, included in HA snapshots, visible to the Samba share at `\\homeassistant\addon_configs\<hash>_filament_stock\data\filaments.db`.
- **s6-overlay** (from the HA base image) supervises both services and restarts the container if either dies.

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
