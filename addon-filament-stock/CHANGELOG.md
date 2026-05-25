# Changelog

## 0.3.0 -- per-color spool/refill counters

`packaging_type` is no longer a filament-level setting. Each color row now
carries independent **spool** and **refill** counters, so the same color of
the same filament can have e.g. 2 spools + 3 refills tracked side by side.

Schema migration runs automatically on first start:

- For every existing color, if its parent filament was marked as `refill`,
  the existing `quantity` / `quantity_used` values are moved into the new
  `quantity_refill` / `used_refill` columns; the spool counters reset to 0.
- `filaments.packaging_type` is dropped (SQLite `ALTER TABLE DROP COLUMN`;
  silently kept on pre-3.35 SQLite which HA does not ship).

API:

- `GET /filaments` returns each color with `quantity`, `quantity_used`,
  `quantity_refill`, `used_refill`, plus server-computed `available_spool`,
  `available_refill`, `available_total`.
- `POST /filaments/{id}/colors` accepts both `quantity` and `quantity_refill`;
  when merging into an existing color, each counter accumulates independently.
- `PUT /colors/{id}` accepts the new fields too.

Companion integration `filament_stock` 0.3.0 exposes the new counters as
sensor attributes (`total_spool`, `total_refill`, per-color
`available_spool` / `available_refill`) and adds a `packaging:
auto|spool|refill` option to the `use_spool`, `mark_arrived`, and
`add_purchase` services.

UI: the per-filament packaging toggle is gone; each color row shows two
side-by-side pills (Spool / Refill) with their own Add and Use buttons.

## 0.2.0 -- first public release

First version intended for outside users. The pre-release `0.1.x` series was internal-only iteration while bringing the add-on up on the maintainer's HA OS install.

What you get:

- FastAPI + React + SQLite, packaged as a Home Assistant Supervisor add-on, served exclusively via HA Ingress (no exposed ports).
- React UI compiled to a static bundle at build time and shipped by nginx.
- SQLite database at `/config/data/filaments.db`, visible to the Samba share at `\\homeassistant\addon_configs\<hash>_filament_stock\data\`, included in HA snapshots automatically.
- Schema migrations in `app/db_schema.py` upgrade older databases on first start (including ones imported from the standalone Docker version of the app).
- Startup log line `DB ready: DATABASE_URL=... file_size=... filaments=... color_stocks=...` so it's obvious which file got opened and how many rows it has.
- Multi-arch images: `amd64`, `aarch64`.
- s6-overlay supervises both FastAPI and nginx; either dying restarts the container.
- Companion [`filament_stock` custom integration](../home-assistant/custom_components/filament_stock/) (separate HACS install) surfaces all inventory as HA entities and services.

If you are upgrading from a 0.1.x pre-release on a personal install, snapshots from before the upgrade remain restorable and the data path (`/config/data/filaments.db`) is unchanged.
