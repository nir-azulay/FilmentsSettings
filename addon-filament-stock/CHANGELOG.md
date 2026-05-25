# Changelog

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
