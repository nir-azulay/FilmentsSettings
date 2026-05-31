# Changelog

## 0.10.1 -- fix "update available" badge in the HA Apps grid

The `io.hass.version` OCI label in the Dockerfile had been pinned to
`"0.1.0"` since the very first release. Supervisor reads that label
from the *installed image* to determine which version is currently
running and compares it against the `version:` field in `config.yaml`
to decide whether to show the "Update available" badge in the
**Settings -> Add-ons** grid. Because the label was hardcoded, the grid
saw `installed=0.1.0` no matter what we shipped, and the comparison
logic produced inconsistent results (badge only appeared after opening
the add-on detail page, which forces a metadata re-read).

Fix:

- Added an `ARG BUILD_VERSION` (re-declared in both build stages so it
  crosses the `FROM` boundary).
- Changed the label to `io.hass.version="${BUILD_VERSION}"`.

Supervisor automatically passes `BUILD_VERSION` = the `version:` field
on every rebuild, so from this release forward the badge will light up
correctly the moment a new commit lands on `main` and the next periodic
repository refresh runs (or you click the **Refresh** button on the
Add-on store page).

No behavioural change. The first install of 0.10.1 will still need to
go through the detail page once because Supervisor doesn't have a
correct installed-version baseline yet -- after that, future updates
will surface in the grid.

## 0.10.0 -- setup doctor + empty-state for new installs

Two new pieces of UI that turn a fresh install on someone else's Home
Assistant from "wait, why doesn't it work?" into a guided walk-through.

### Setup checklist (`/api/health` doctor)

A new `GET /api/health` endpoint runs seven best-effort checks and
returns a structured report:

| Check | What it verifies | Severity on failure |
|---|---|---|
| `supervisor_token` | `SUPERVISOR_TOKEN` env var is present | error |
| `database_writable` | SQLite DB is reachable and writable | error |
| `ha_core_reachable` | `GET http://supervisor/core/api/` succeeds | error |
| `ha_bambulab_installed` | Any entity in HA looks like ha-bambulab | error |
| `bambu_printers_found` | At least one printer slug detected | warn |
| `ams_entities_found` | At least one AMS/external spool entity | warn |
| `bambu_set_filament_service_available` | `bambu_lab.set_filament` is registered (LAN mode) | warn |

Each check returns `{id, name, ok, severity, message, hint, detail}` so
the frontend can render a single sticky card at the top of the page
with a clear "what to do" for every failing item. The card auto-hides
when everything passes and auto-expands when any check has `error`
severity. Live "Re-check now" button so users don't have to refresh
the page after fixing something.

Implementation: `app/health.py` (new) -- each check is wrapped so it
never raises; the orchestrator runs them with at most one shared
`/api/states` fetch and one `/api/services` fetch. `app/ha_client.py`
gained two helpers: `ping_core()` (boolean liveness probe) and
`list_services()` (enumerates HA services).

### Empty-state card

When the filament list is empty -- whether on first launch or after
the user deletes every row -- the dashboard shows a friendly card
instead of a blank grid:

* **Add your first filament** -- opens the existing Add dialog.
* **Load sample list** -- POSTs to a new `POST /api/seed-now` endpoint
  that runs the seed routine on demand. Idempotent: existing rows are
  never overwritten, and the user gets a toast saying "Added N sample
  filaments" or "All N samples were already in your stock."
* Footer tip explaining the AMS auto-detection so users know the
  panel above wakes up once `ha-bambulab` is wired in.

The seed routine itself was refactored: `_run_seed()` is shared
between the startup seed (still gated on the
`seed_demo_filaments_on_first_run` option) and the new
`seed_filaments_force()` (used by the on-demand endpoint, bypasses
the gate).

### Liveness probe renamed

The old trivial `/api/health` (which just returned `{"status": "ok"}`)
moved to `/api/ping`. Anyone using it as a Docker / nginx liveness
probe should update their config to point at `/api/ping` instead.

## 0.9.0 -- four new configuration toggles

Adds four new user-configurable options in the add-on's Configuration tab,
all with friendly labels and descriptions:

- **Pre-tick "Also update the printer's AMS display"**
  (`default_push_to_printer`, default `false`) -- controls whether the
  push-to-printer checkbox in the Assign-from-stock dialog opens already
  ticked. Useful if you're on LAN mode and always want assignments mirrored
  to the printer's tray display.

- **Default low-stock alert threshold**
  (`default_low_stock_threshold`, default `1`, range `1..100`) -- the
  threshold applied to **newly created** filaments. The add-on raises an
  alert when a color's total drops to this number or below. Existing
  filaments keep their per-row threshold; this only affects new rows.

- **Seed sample filaments on first run**
  (`seed_demo_filaments_on_first_run`, default `true`) -- when off, the
  add-on doesn't auto-populate the DB with the curated SUNLU / Inslogic /
  Jayo filament list on first launch. Set to off if you want to start from
  an empty stock. Existing rows are never overwritten either way.

- **AMS panel refresh interval (seconds)**
  (`ams_poll_interval_seconds`, default `15`, range `5..300`) -- how often
  the AMS Status panel polls Home Assistant for tray state. Lower for
  active monitoring during a print, raise to reduce load on slower setups.

Internals: `app/addon_options.py` grew matching dataclass fields with a
new `_coerce_int(value, default, *, lo, hi)` helper that clamps + parses
defensively. `GET /api/config` now returns all five fields. The frontend
`AddonConfig` interface, `DEFAULT_ADDON_CONFIG`, `AmsPanel`, and
`AssignTrayDialog` were updated to consume the new fields. The seed
gate and threshold fallback live in the backend so even direct curl
calls to `POST /filaments` pick up the configured default.

## 0.8.7 -- friendly labels for add-on configuration options

The add-on's Configuration tab in Home Assistant now shows a
human-readable label and description for each option instead of the raw
schema key. For `ask_if_replaced_spool_empty` you'll see:

> **Ask if the replaced spool is empty**
> When you assign a new spool to an AMS tray that's already assigned,
> show a "Yes / No" prompt asking whether the spool you're replacing is
> empty. When OFF (the default), the replaced spool is silently returned
> to your stock -- safe for the common "swap colours mid-job" case.
> Turn this ON if you frequently run spools to empty and want to mark
> them as used up at the moment of swap.

Implementation: a new `translations/en.yaml` file in the add-on root
that HA Supervisor reads to render the Configuration UI. Adding more
options later just means appending another entry under `configuration:`
in the same file.

## 0.8.6 -- cleaner add-on icon

Replaces `icon.png` with a properly-square (256x256) stylised 3D spool on
a true transparent background. Previously the icon was a landscape image
that HA was stretching/squishing into the square tile in the Apps grid,
and the "background" was a fake checkerboard rendered as opaque grey
pixels.

The `logo.png` (shown only on the add-on detail page) is unchanged.

## 0.8.5 -- user-configurable add-on options (start with empty-spool prompt)

Adds support for native Home Assistant add-on configuration. Open
**Settings → Add-ons → Filament Stock → Configuration** in HA to see the
new options panel. The first setting:

- **`ask_if_replaced_spool_empty`** (default: `false`)

  Controls whether the Assign-from-stock dialog prompts you with
  *"Is the replaced spool empty? Yes / No, return to stock"* when you
  replace one assignment with another on the same tray.

  - `false` (default) -- the prompt is hidden. Replaced spools are
    always returned to your stock (the safe, non-destructive default).
    A small italic note in the dialog explains what's happening and
    where to flip the toggle.
  - `true` -- the prompt is shown every time, exactly like the old
    behaviour. Pick this if you frequently swap colours mid-print and
    need to mark spools as used up.

Saving the option in HA's Configuration tab restarts the add-on (HA
handles this), which re-reads `/data/options.json` and applies the new
value.

### Plumbing for future options

This release lays the groundwork for adding more user-configurable
toggles cheaply:

- `addon-filament-stock/app/addon_options.py` -- reads
  `/data/options.json` once at startup, caches the resolved values,
  and falls back to compiled-in defaults when run outside Supervisor
  (local dev / smoke tests).
- New `GET /api/config` endpoint -- surfaces the resolved options to
  the frontend so the UI can honour the user's preferences.
- New `fetchAddonConfig()` + `AddonConfig` type on the frontend.

To add a new toggle in future:

  1. Add it to `options:` + `schema:` in `config.yaml`.
  2. Add the matching default to `AddonOptions` + the coercion in
     `addon_options.py`.
  3. Add the field to `options_as_dict()` and the frontend
     `AddonConfig` interface.
  4. Read `config.your_field` in the UI component that should honour it.

## 0.6.0 -- "I just loaded this spool" tray assignment + optional printer push

You can now tell the add-on which physical spool from your stock you put
into an AMS tray. Each tray card in the AMS panel grows two new buttons:

- **Assign from stock** — opens a picker filtered by the tray's current
  material (PETG tray → PETG filaments first, then PLA, etc.). Pick a
  filament + color, choose spool or refill, optionally tick **Also tell
  the printer**, and click Assign. The add-on:
  1. Decrements the chosen ColorStock's spool or refill counter (so your
     in-stock totals stay accurate).
  2. Writes a `TrayAssignment` row that links the AMS entity to the
     ColorStock row.
  3. *(If you ticked the box)* calls `bambu_lab.set_filament` on the HA
     side, which pushes the new tray metadata to the printer over MQTT
     — your AMS display updates to show a Bambu-recognised generic
     filament (`Generic PETG` etc.) with your stock's nozzle temp range
     and color.

- **Unassign** — closes the live assignment and **restores** the
  spool/refill to your stock counter. Does NOT clear the tray on the
  printer side; assign a different spool to overwrite the AMS slot
  metadata.

A small purple "From your stock: SUNLU PETG HS · Black (spool, pushed)"
badge appears below each tray that has a live assignment. Click it to
jump to the matching filament card.

### How push-to-printer works

When you tick **Also tell the printer** the add-on calls
`bambu_lab.set_filament` with:

| Field | Value |
|---|---|
| `entity_id` | the tray sensor (e.g. `sensor.h2s_ams_1_tray_3`) |
| `tray_info_idx` | a generic Bambu filament ID — `GFL99` (Generic PLA), `GFG99` (Generic PETG), `GFB99` (Generic ASA), `GFN99` (Generic PA), `GFU99` (Generic TPU), `GFB98` (Generic ABS), `GFC99` (Generic PC), picked from your filament's `filament_type` + `material` |
| `tray_color` | `RRGGBBFF` derived from the ColorStock's `color_hex` |
| `tray_type` | `PLA` / `PETG` / `ASA` / `PA` / `TPU` / `ABS` / `PC` |
| `nozzle_temp_min` / `nozzle_temp_max` | from the local Filament row, clamped to Bambu's 160-300°C range |

Why generic IDs and not your specific brand? Bambu's firmware uses
`tray_info_idx` to look up curated print profiles. Sending one of your
local IDs (e.g. `P759ffa0` for SUNLU PETG HS) would just show
"Unknown" on the AMS display. Sending `GFG99` lets the printer treat
the spool as a generic PETG with your nozzle temps, which is exactly
what you want — and the link back to your specific brand is kept
locally on the assignment row.

If the printer push fails (printer offline, ha-bambulab not installed,
the integration's service signature changed), the **local assignment
is still saved** and you get a clear error message in the dialog. The
counter decrement is never rolled back by a push failure.

### Backend

New module `app/bambu_mapping.py` holds the material-to-Bambu family
table (extend `_FAMILY_RULES` to add more materials), plus tiny helpers
for the color and nozzle-temp normalisation.

New table `tray_assignments`:

```
id, entity_id, location_label, color_stock_id, packaging,
pushed_to_printer, push_error, assigned_at, unassigned_at, notes
```

Soft-deleted via `unassigned_at IS NULL` so the assignment history is
preserved (see `GET /ams/trays/{entity_id}/assignment-history`).

New endpoints:

```
GET  /api/ams/trays/{entity_id}/suggestions?material_hint=PETG
POST /api/ams/trays/{entity_id}/assign
POST /api/ams/trays/{entity_id}/unassign
GET  /api/ams/trays/{entity_id}/assignment-history
```

`GET /api/ams/trays` now also includes the live assignment on each
tray (single batch query — O(1) extra DB cost regardless of tray
count).

`HaClient.call_service(domain, service, payload)` is the new mutation
path — strictly opt-in per request, never invoked unless the user
ticks "Also tell the printer".

### Sanity-checked

Backend smoke test exercises the assign/unassign counter math, the
material mapping for every supported family (PLA / PETG / ASA / PA /
TPU + unknown fallback), the color hex normaliser, and the nozzle-temp
clamping. Frontend builds cleanly with no TypeScript errors.

## 0.5.4 -- detect duplicate-suffixed AMS tray entities + friendly_name labels

Fixes the panel silently dropping half the trays on printers with multiple
AMS units of the same model.

ha-bambulab assigns the same base entity_id slug to both AMS 2 Pros on a
printer (because their internal AMS index is `1` for both); Home Assistant
disambiguates by appending `_2`, `_3`, ... to the second / third / Nth
copy. So two AMS 2 Pros produce eight tray entities:

```
sensor.<printer>_ams_1_tray_{1..4}      (AMS 2 Pro #1)
sensor.<printer>_ams_1_tray_{1..4}_2    (AMS 2 Pro #2)
```

The 0.5.3 regex only matched the un-suffixed form, so the second AMS 2
Pro's four trays were silently dropped from the panel.

Now:

- `_AMS_TRAY_RE` and `_FALLBACK_TRAY_RE` accept an optional trailing
  `_<n>` group (`dupe`) that we use as an `instance_idx` discriminator
  (defaults to 1, suffix `_2` -> 2, `_3` -> 3, ...).
- `_renumber_ams_units` now buckets AMS units by `(ams_idx, instance_idx)`
  instead of `ams_idx` alone, so two AMS 2 Pros that both have raw
  `ams_idx=1` produce two distinct unit cards instead of collapsing.
- Tray dicts carry a new `unit_label` field (e.g. `"AMS 2 Pro #1"`) which
  the frontend now uses as the grouping key, replacing the old
  string-split heuristic.

Bonus: the panel now prefers HA's `friendly_name` attribute on tray
sensors when available. ha-bambulab sets it to e.g. `"AMS 2 Pro #1 Tray
1"`, which is the gold-standard label and removes any chance of the
add-on guessing the wrong hardware model name. The model label
extracted from `friendly_name` also feeds the model-label resolution
chain ahead of the device-registry `model` field, since friendly_name
is always populated whereas device-registry lookups can fail.

Smoke-tested against the actual entity_id set reported by ha-bambulab
on a printer with 2x AMS 2 Pro + 2x AMS HT + external spool: all 11
trays parse, group as 5 distinct units, with correct labels.

## 0.5.3 -- AMS panel: friendly device names, hardware models, clean numbering

The AMS Status panel now looks up each tray entity in Home Assistant's
device registry (via `POST /api/template`) and uses the registry data for
the labels instead of guessing from the entity_id. With this:

- Group titles show the printer's friendly name from HA -- e.g. `H2S 3D
  Printer · AMS 1` instead of `h2s_0938bc5c2200107 · AMS 1`. When no
  device info is available the printer slug is still title-cased
  (e.g. `H2S 0938bc5c2200107`) so it never falls back to lowercase noise.
- Each tray's hardware model is taken from `device_attr(..., 'model')`
  and normalised: `AMS`, `AMS 2 Pro`, `AMS HT`, `AMS Lite`, `AMS HUB`.
- The external spool tile no longer has its device suffix
  (`_externalspool`) appearing in the group title.
- AMS units with ha-bambulab's internal device IDs (e.g. `128`, `129`)
  are now **renumbered in display order**: an AMS 2 Pro #1 and #2,
  not AMS 128 and AMS 129. The renumbering is per-bucket (per-printer
  + per-model) so a classic AMS 1 and an AMS 2 Pro #1 on the same
  printer don't collide.
- The `#<n>` suffix on named variants is only shown when there's more
  than one unit of that model on the same printer -- single-unit
  setups just say `AMS 2 Pro`, not `AMS 2 Pro #1`.
- `remain_pct` values of `-1` (or any value outside 0..100) -- which
  ha-bambulab uses to mean "unknown" for Generic / non-RFID filaments
  -- are now hidden instead of rendered as red "-1%" pills.

New backend pieces:

- `app/ha_client.py`: `render_template()` POSTs to HA Core's
  `/api/template` (rendering only, no service calls or state mutations)
  so we can read device-registry fields the plain `/api/states` doesn't
  expose.
- `app/routers/ams.py`: `_fetch_device_info()` renders a single Jinja2
  template that returns `{entity_id: {name, model, manufacturer,
  via_name, ...}}` for every tray we care about in one call,
  `_enrich_with_device_info()` annotates each tray with `printer_label`
  / `model_label`, `_renumber_ams_units()` collapses internal AMS device
  IDs to sequential 1-based numbers, `_pretty_model()` /
  `_strip_ams_suffix()` / `_slug_to_label()` are the formatting helpers.
  All best-effort: if the template call fails, the panel still renders
  with the old entity-id-derived labels.

Frontend:

- `api.ts` `AmsTray` gains optional `printer_label`, `model_label`,
  `device_name`.
- `components/AmsPanel.tsx` grouping now keys on `printer_label`.
- No new dependencies.

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
