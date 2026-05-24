# Changelog

## 0.1.1

- Move SQLite DB from `/data/filaments.db` to `/config/data/filaments.db` so the user-visible Samba share `\\homeassistant\addon_configs\filament_stock\` exposes it for backup, seeding, and inspection without needing SSH.
- Auto-migrate any existing v0.1.0 DB from `/data/` to `/config/data/` on first start (legacy file left in place as a backup).
- `map: [addon_config:rw]` added to `config.yaml`.

## 0.1.0

- Initial release.
- Ingress-only nginx + FastAPI + SQLite.
- React UI ported unchanged from the standalone QNAP deployment.
- Removed `import_profiles` endpoint (was QNAP-specific, scanned bind-mounted profile folders).
