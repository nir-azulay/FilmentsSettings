# Filament Stock add-on

3D printer filament inventory with per-color stock tracking, low-stock alerts, and a React UI accessible inside Home Assistant via Ingress.

## Architecture

- **FastAPI** (Python, uvicorn) on `127.0.0.1:8000` -- REST API at `/api/*`.
- **nginx** on `:8099` -- serves the React bundle and reverse-proxies `/api/` to FastAPI. Ingress connects here.
- **SQLite** at `/data/filaments.db` -- persistent across add-on updates, included in HA snapshots.
- **s6-overlay** (from the HA base image) supervises both services and restarts the container if either dies.

## Data

| Path inside container | What |
|---|---|
| `/data/filaments.db` | SQLite database (filaments, color stocks, history, alert ignores) |
| `/app/app/` | FastAPI source |
| `/usr/share/nginx/html/` | Built React bundle |
| `/etc/nginx/nginx.conf` | nginx config |

## Configuration

The add-on currently has no user-configurable options. Future versions may expose database backup interval, alert thresholds, etc.

## Companion integration

Use the [`filament_stock` custom integration](../../custom_components/filament_stock/) to expose this add-on's data as HA sensors and services for use in automations.
