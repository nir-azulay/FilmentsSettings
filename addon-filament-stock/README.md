# Filament Stock add-on

3D printer filament inventory with per-color stock tracking, low-stock alerts, and a React UI accessible inside Home Assistant via Ingress.

## Architecture

- **FastAPI** (Python, uvicorn) on `127.0.0.1:8000` -- REST API at `/api/*`.
- **nginx** on `:8099` -- serves the React bundle and reverse-proxies `/api/` to FastAPI. Ingress connects here.
- **SQLite** at `/config/data/filaments.db` -- persistent across add-on updates, included in HA snapshots, **visible to the Samba share** at `\\homeassistant\addon_configs\filament_stock\data\filaments.db`.
- **s6-overlay** (from the HA base image) supervises both services and restarts the container if either dies.

## Data

| Path inside container | Samba path | What |
|---|---|---|
| `/config/data/filaments.db` | `\\homeassistant\addon_configs\filament_stock\data\filaments.db` | SQLite database (filaments, color stocks, history, alert ignores) |
| `/app/app/` | -- | FastAPI source |
| `/usr/share/nginx/html/` | -- | Built React bundle |
| `/etc/nginx/nginx.conf` | -- | nginx config |

### Seeding from an existing DB

Stop the add-on, drop your `filaments.db` into `\\homeassistant\addon_configs\filament_stock\data\` (create the `data` folder if it doesn't exist), then start the add-on. The schema migrations in `app/db_schema.py` upgrade older databases on first start.

### Migrating from v0.1.0

v0.1.0 stored the DB at `/data/filaments.db` (not visible to Samba). v0.1.1 auto-copies any existing `/data/filaments.db` to `/config/data/filaments.db` on first start. The legacy file is left in place untouched as a backup; you can remove it via SSH later if you wish.

## Configuration

The add-on currently has no user-configurable options. Future versions may expose database backup interval, alert thresholds, etc.

## Companion integration

Use the [`filament_stock` custom integration](../../custom_components/filament_stock/) to expose this add-on's data as HA sensors and services for use in automations.
