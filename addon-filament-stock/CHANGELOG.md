# Changelog

## 0.5.2 -- recognise more external-spool entity-id names

0.5.0 only matched three specific external-spool entity-id endings
(`_external_spool`, `_vt_tray`, `_external_tray`); on some Bambu printers
and ha-bambulab forks the external spool is exposed under a different
name and was silently dropped.

External-spool matcher now recognises:

- `_external_spool`, `_external_spool_tray`, `_external_tray`
- `_ext_spool`, `_ext_tray`
- `_vt_tray`, `_virtual_tray`, `_virtual_spool`
- `_x1_external`, `_external`

Plus an attribute-based fallback: any `sensor.*` whose entity_id contains
`external`, `vt_tray`, or `virtual`, and whose attributes carry Bambu
tray markers (`filament_id`, `tray_info_idx`, `tray_uuid`, `tray_type`,
`tray_sub_brands`, or `tray_color`), now classifies as the external
spool. So if a future ha-bambulab release renames it again, the panel
keeps working without a code change.

The `/api/ams/debug` endpoint now tags these matches separately
(`external_attr_fallback` vs `external_regex`) so the next mismatch is
easy to triage.

## 0.5.1 -- recognise AMS 2 Pro / AMS HT / AMS Lite tray sensors

The 0.5.0 regex only matched the classic `sensor.<printer>_ams_<n>_tray_<n>`
naming. Users with newer AMS hardware (AMS 2 Pro, AMS HT, AMS Lite, AMS HUB)
saw their additional units silently dropped from the panel because
ha-bambulab uses a different entity-id slug for each model.

Now matches all known variants:

- `sensor.<printer>_ams_<n>_tray_<n>` -- classic AMS.
- `sensor.<printer>_ams_pro_<n>_tray_<n>` / `_ams2pro_<n>_tray_<n>` -- AMS 2 Pro.
- `sensor.<printer>_ams_ht_<n>_tray_<n>` -- AMS HT.
- `sensor.<printer>_ams_lite_<n>_tray_<n>` -- AMS Lite.
- `sensor.<printer>_ams_hub_<n>_tray_<n>` -- AMS HUB.

Plus a fallback for future hardware: any `sensor.<...>_tray_<n>` whose
attributes carry Bambu tray markers (`filament_id`, `tray_info_idx`,
`tray_uuid`, `tray_type`, `tray_sub_brands`, or `tray_color`) is treated
as a tray with a best-effort AMS index sniffed from its entity_id. So
the next AMS model that ships will surface even before we cut a new
add-on release.

Tray location labels now distinguish hardware:

- Classic AMS: `AMS 1 · Slot 3`.
- AMS 2 Pro: `AMS 2 Pro #1 · Slot 4` (the `#` makes the unit index visually
  distinct from the model name).
- Same for `AMS HT #2 · Slot 1`, `AMS Lite #1 · Slot 2`, etc.

Frontend grouping was updated to group by the rendered unit label (so an
`AMS #1` and an `AMS 2 Pro #1` on the same printer get separate blocks
even though they share `ams_idx = 1`).

New diagnostic endpoint: `GET /api/ams/debug` returns every sensor whose
entity_id mentions `ams`, `tray`, or `spool`, tagged with how (or whether)
the matcher recognised it -- handy for triaging hardware that still
slips through.

## 0.5.0 -- AMS status panel (live view of what's loaded in each tray)

A new **AMS Status** panel at the top of the dashboard shows the current
contents of every Bambu Lab AMS slot (and the external spool) reported by
the [`greghesp/ha-bambulab`](https://github.com/greghesp/ha-bambulab) HACS
integration, and cross-references each tray against the local stock.

For every tray you see:

- Location (`AMS 1 · Slot 3`, `External spool`).
- Loaded filament: brand/material name, color swatch, hex code, material
  code (PETG / ASA / …).
- Remaining percentage as a coloured pill (green ≥50% / amber ≥20% / red).
- A **stock badge** showing the matching local color row:
  - `✓ Black in stock: 2 spools · 1 refill` (green) when matched and in stock.
  - `✗ Black in stock: 0 spools · 0 refills` (red) when matched but exhausted.
  - `◐ SUNLU PETG HS — color not in stock` (blue) when the filament is tracked
    but this exact hex isn't.
  - `⚠ Not tracked in stock` (amber) when no `Filament` row has the tray's
    `filament_id`.
- Clicking a matched badge scrolls to the corresponding filament card on the
  page and briefly highlights it.

The panel polls `/api/ams/trays` every 15s and has a manual **Refresh**
button. Empty trays show as muted with "No filament loaded".

New backend pieces:

- `app/ha_client.py` -- thin async wrapper around the Supervisor-proxied
  `http://supervisor/core/api/states` endpoint, using the auto-injected
  `SUPERVISOR_TOKEN`. Read-only; no service calls, no writes.
- `app/routers/ams.py` -- `GET /api/ams/trays` parses each
  `sensor.<printer>_ams_<n>_tray_<n>` and `sensor.<printer>_external_spool`
  (also `vt_tray` / `external_tray` variants) state, normalises Bambu's
  `#RRGGBBAA` color attribute to `#RRGGBB`, and joins each tray to the local
  `Filament.filament_id` + `ColorStock.color_hex` rows (with a single-color
  fallback for filaments that have only one color tracked).
- `httpx>=0.27` added to `requirements.txt`.
- `config.yaml` now sets `homeassistant_api: true` so Supervisor provides
  the API token. No other permissions are granted; the add-on stays
  Ingress-only with no exposed ports.

If the integration isn't installed yet the panel renders a friendly empty
state with a link to the HACS repo. If the Supervisor token is missing
(usually because the user hasn't restarted the add-on after the 0.5.0
update) it surfaces the error instead of failing silently.

## 0.4.2 -- color name is actually visible

Fixes the color-row layout regression introduced in 0.4.1: applying
`display: inline-flex` inline on the `.color-stock-row__name` span cancelled
its `flex: 1 1 0` from the stylesheet, collapsing the span to zero width on
narrow cards so the color-name text and the new swatch chip both clipped to
nothing. On mobile / panel widths the row looked like just `[spool icon]
[Spool pill] [Refill pill]` with no name at all.

The swatch chip is gone (it was the cause of the collapse). The color name
now renders as a bold 15px span with a high-contrast white text-shadow so it
stays legible over both light and dark tinted row backgrounds, with
`min-width: 80px` / `flex: 1 1 80px` so it never fully collapses again.
Hovering the name still shows a `"<Color name> • #hex"` tooltip.

Frontend-only change; no backend, database, or API impact.

## 0.4.1 -- color swatch chip on color rows

Each color row in the filament card now shows a small flat color-swatch chip
next to the color name, in addition to the existing tinted spool icon and row
background. The chip is filled with the literal `color_hex` so very light or
very dark colors stay unambiguous on any row background, and it dims for
`ordered` / `out_of_stock` rows to match the muted icon styling. Hovering the
name shows a `"<Color name> • #hex"` tooltip.

Frontend-only change; no backend, database, or API impact.

## 0.4.0 -- in-app filament configuration & BambuStudio profile downloader

Each filament card now has a **Profile** button that expands an inline panel
showing:

- The stock-tracking metadata you've configured (brand, material, density,
  nozzle/bed temps, low-stock threshold, Amazon URL).
- The BambuStudio profile bundle that ships with the add-on for this filament,
  if there is one: the base filament profile + user preset + per-nozzle process
  presets, summarised with the key fields (nozzle/bed temp, max volumetric
  speed, retraction, Tg) split out for Standard and High Flow extruders.
- One-click downloads:
  - **Per file** (single JSON per nozzle size, plus the base/preset files).
  - **Full bundle** as a `.zip` ready to drop into BambuStudio's
    `user/<id>/{filament,filament/base,process}` folders.

Bundled profiles cover the filaments tracked in the maintainer's repo (SUNLU
PETG/PETG HS/PLA/PA E-PA/TPU 95A, Inslogic ASA/Matte PLA/Nebulux PLA/PETG
Pro/PLA Pro/Silk PLA/TPU 95A) targeting the **Bambu Lab H2S**. Filaments
without a bundled profile show a friendly empty state pointing at the
`.cursor/rules/add-filament.mdc` workflow.

New backend pieces:

- `app/profile_bundle.py` -- on-disk profile lookup with exact-product matching
  (so `SUNLU PETG` and `SUNLU PETG HS` stay disambiguated despite the shared
  prefix), with path-traversal hardening on file downloads.
- `app/routers/profiles.py` -- `GET /api/filaments/{id}/profile` (metadata),
  `GET /api/filaments/{id}/profile/file/{name}` (single file), and
  `GET /api/filaments/{id}/profile/zip` (full bundle).
- Profile files live at `/app/profiles/` inside the image, baked in from
  `addon-filament-stock/profiles/` at build time. Refresh that mirror from the
  canonical `SUNLU/` and `Inslogic/` source folders with
  [`sync_profiles.sh`](sync_profiles.sh) before re-building.

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
- Schema migrations in `app/db_schema.py` upgrade older databases on first start.
- Startup log line `DB ready: DATABASE_URL=... file_size=... filaments=... color_stocks=...` so it's obvious which file got opened and how many rows it has.
- Multi-arch images: `amd64`, `aarch64`.
- s6-overlay supervises both FastAPI and nginx; either dying restarts the container.
- Companion [`filament_stock` custom integration](../home-assistant/custom_components/filament_stock/) (separate HACS install) surfaces all inventory as HA entities and services.

If you are upgrading from a 0.1.x pre-release on a personal install, snapshots from before the upgrade remain restorable and the data path (`/config/data/filaments.db`) is unchanged.
