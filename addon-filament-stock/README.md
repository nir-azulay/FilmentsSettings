# Filament Stock add-on

3D-printer filament inventory dashboard for Home Assistant. Tracks per-color stock, fires low-stock alerts, and exposes a REST API the companion [`filament_stock` custom integration](../home-assistant/custom_components/filament_stock/) uses to surface entities and services to HA automations.

Author: **[Nir Azulay](https://github.com/nir-azulay)** -- MIT licensed, see [LICENSE](../LICENSE).

## Installing on a fresh Home Assistant system (0.10.0+)

The add-on is designed to **just work** on any HA OS / Supervised
install: it never asks for tokens, passwords, or API keys. Supervisor
auto-injects a short-lived `SUPERVISOR_TOKEN` into the container when
the add-on starts, and the add-on uses that to talk to HA Core's
internal API at `http://supervisor/core/api/`.

### Prerequisites

- **Home Assistant OS** or **Supervised** (Container-only installs can't
  run add-ons; use the source under `addon-filament-stock/` directly).
- **[ha-bambulab](https://github.com/greghesp/ha-bambulab)** integration
  installed via HACS, with at least one Bambu printer added. The add-on
  doesn't talk to your printer or Bambu Cloud directly -- it reads tray
  state from ha-bambulab's sensors and (optionally, opt-in per
  assignment) calls `bambu_lab.set_filament` to push tray metadata back
  to the printer.

### First-launch experience

On first open, the dashboard shows a **Setup checklist** card at the
top with seven live checks (Supervisor token, HA Core API, ha-bambulab
detected, AMS entities found, etc.). Anything that's not configured
correctly is flagged with a short hint -- no need to grep logs.

When the filament grid is empty, a friendly **Get started** card
offers two choices: add your first filament manually, or load a small
curated sample list so you can see how the dashboard looks before
deciding what to track. Both options live inside the add-on -- no
external dependencies, no GitHub clone needed.

## Configuration (0.8.5+)

The add-on exposes user-editable options through HA's standard add-on
Configuration tab (**Settings → Add-ons → Filament Stock → Configuration**).
Saving a change automatically restarts the add-on so the new values take
effect.

| Option | Default | What it does |
|---|---|---|
| `ask_if_replaced_spool_empty` | `false` | When `true`, the Assign-from-stock dialog asks *"Is the replaced spool empty?"* every time you assign a new spool to an already-assigned tray. When `false` (default), replaced spools are silently returned to your stock. |
| `default_push_to_printer` | `false` | When `true`, the "Also update the printer's AMS display" checkbox in the Assign-from-stock dialog opens pre-ticked. Convenient on LAN-mode setups; leave off for Cloud-only. |
| `default_low_stock_threshold` | `1` | Low-stock alert threshold applied to **newly created** filaments. Range `1..100`. Existing filaments keep their per-row threshold. |
| `seed_demo_filaments_on_first_run` | `true` | When `false`, the add-on doesn't auto-populate the DB with curated SUNLU / Inslogic / Jayo demo filaments on first launch. Existing rows are never overwritten. |
| `ams_poll_interval_seconds` | `15` | How often the AMS Status panel polls Home Assistant for tray state. Range `5..300`. Lower for active print monitoring, raise for slow setups. |
| `disable_bambu_integration` | `false` | Master opt-out for Bambu Lab features. When `true`, the AMS Status panel is hidden and the setup checklist skips the Bambu-related health checks. Useful if you don't own a Bambu printer -- the rest of the add-on still works as a manual filament stock tracker. |

To add more options later, follow the recipe in the 0.8.5 section of
[CHANGELOG.md](CHANGELOG.md).

## Architecture

- **FastAPI** (Python, uvicorn) on `127.0.0.1:8000` -- REST API at `/api/*`.
- **nginx** on `:8099` -- serves the React bundle and reverse-proxies `/api/` to FastAPI. HA Ingress connects here.
- **SQLite** at `/config/data/filaments.db` -- persistent across add-on updates, included in HA snapshots, visible to the Samba share at `\\homeassistant\addon_configs\<hash>_filament_stock\data\filaments.db`.
- **Supervisor HA Core API** (`http://supervisor/core/api`) -- used by the AMS Status panel (0.5.0+) to fetch Bambu AMS tray state, and (0.6.0+) to optionally call `bambu_lab.set_filament` when you assign a spool from stock to a tray with **Also tell the printer** ticked. Authenticated with the auto-injected `SUPERVISOR_TOKEN`. All read paths are read-only; the printer-push service call only fires on explicit user opt-in per assignment.
- **s6-overlay** (from the HA base image) supervises both services and restarts the container if either dies.

## AMS Status panel (0.5.0+)

A panel at the top of the dashboard renders the live contents of every Bambu
Lab AMS slot (and the external spool) reported by the
[`greghesp/ha-bambulab`](https://github.com/greghesp/ha-bambulab) HACS
integration, and cross-references each tray against your local stock.

For every tray you see:

- Where it is -- `AMS 1 · Slot 3`, `External spool`, etc.
- What's loaded -- filament name, color swatch, hex code, material code.
- How much is left -- a coloured remaining-% pill (green ≥50% / amber ≥20% / red).
- A stock badge:
  - **✓ Color in stock: N spools · M refills** (green) when matched and you have some.
  - **✗ Color in stock: 0 spools · 0 refills** (red) when matched but exhausted.
  - **◐ Brand Material -- color not in stock** (blue) when the filament is tracked but this hex isn't.
  - **⚠ Not tracked in stock** (amber) when no `Filament` row matches the tray's `filament_id`.
- Click a matched badge to jump straight to the corresponding filament card.

The panel polls `GET /api/ams/trays` every 15s; there's also a manual
**Refresh** button. Empty trays render muted.

Under the hood this needs Supervisor's HA Core API token, which is granted
by `homeassistant_api: true` in [`config.yaml`](config.yaml). The add-on
uses it strictly read-only (only `GET /core/api/states` -- no service calls,
no writes). If the add-on came from a build before 0.5.0 the new permission
needs a one-time **Restart** to take effect; the panel surfaces a clear
error if the token is missing.

If the Bambu HACS integration isn't installed, the panel renders a friendly
empty state with a link to its repo.

Backend code: [`app/ha_client.py`](app/ha_client.py) (Supervisor wrapper),
[`app/routers/ams.py`](app/routers/ams.py) (tray parsing + stock matching).

## Tray assignment from stock (0.6.0+)

Each tray card in the AMS panel has two new buttons:

- **Assign from stock** -- opens a picker pre-filtered by the tray's
  current material (PETG tray surfaces PETG filaments first, PLA tray
  surfaces PLA, etc.). Pick a filament + color, choose **spool** or
  **refill**, optionally tick **Also tell the printer**, and click
  **Assign**. The add-on:
  1. Decrements the chosen `ColorStock`'s spool/refill counter so the
     in-stock totals stay accurate.
  2. Writes a `TrayAssignment` row linking the AMS entity to the
     `ColorStock`.
  3. *(If the box was ticked)* calls `bambu_lab.set_filament` via the
     HA Supervisor so the printer's AMS display also updates with a
     Bambu-recognised generic filament (`Generic PETG` etc.), your
     stock's color, and the nozzle temp range from the local filament
     row.
- **Unassign** -- closes the live assignment and **restores** the
  spool/refill to your stock counter. The printer's slot is left
  alone (assign a different spool to overwrite the AMS metadata).

A purple "From your stock: <brand> <material> · <color>" badge appears
below each tray that has a live assignment. Click it to jump to the
matching filament card in the dashboard.

### Why generic Bambu IDs for the printer push

When pushing metadata to the printer, the add-on sends one of Bambu's
generic filament IDs (`GFL99` for PLA, `GFG99` for PETG, `GFB99` for
ASA, `GFN99` for PA, `GFU99` for TPU, `GFB98` for ABS, `GFC99` for
PC) instead of your local filament ID. The printer's firmware uses
`tray_info_idx` to look up its own curated profile; if it doesn't
recognise the value, the AMS display just says "Unknown". The
generic IDs make the slot read as e.g. "Generic PETG" with your
color and temps, while the link back to your specific brand stays
local on the `TrayAssignment` row.

If the push fails (printer offline, ha-bambulab not installed, the
integration's service signature changed), **the local assignment is
still saved**. The dialog surfaces a clear error so you can decide
whether to keep the local-only assignment or retry once the printer
is back online. Counter decrements are never rolled back by a push
failure.

Backend code:
[`app/bambu_mapping.py`](app/bambu_mapping.py) (material → Bambu family table),
[`app/routers/assignments.py`](app/routers/assignments.py) (assign / unassign / suggestions endpoints),
[`app/ha_client.py`](app/ha_client.py) (`call_service` helper -- the only
write path the add-on exposes, guarded behind explicit opt-in per
assignment).

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
