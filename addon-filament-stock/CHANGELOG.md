# Changelog

## 0.19.1 -- Brand logo on spool labels

- Spool label stickers now include the **brand logo** in the top-left corner
- Logo is auto-converted to high-contrast grayscale for thermal printing
- Falls back to the previous layout when no logo is available

## 0.19.0 -- UX, Analytics, and Export Features

### Dark Mode Support
- Automatic dark mode following system `prefers-color-scheme` setting
- All 50+ CSS custom property tokens have dark mode overrides
- Audited all 20+ component files for hardcoded colors — replaced with CSS variable references

### Mobile-Optimized Layout
- Responsive toolbar: action buttons collapse into an overflow menu on small screens
- Scan button stays inline on mobile; Add Filament and Sync move to the menu

### Export / Import Database
- **Export Database** — download a full JSON backup of all filaments, colors, spools, and assignments
- **Import Database** — restore from a backup file with confirmation and preview
- Both actions available from the toolbar overflow menu (⋮)

### Shareable Filament Profiles
- **Share** button on each filament card generates a QR code, copyable encoded string, and downloadable JSON
- **Import Shared Profile** option in the toolbar menu — paste JSON or upload a file to import a shared filament

### Drag-and-Drop Tray Assignment
- Drag a spool from the All Spools panel directly onto an AMS tray slot to assign it
- Visual feedback (dashed blue outline) during drag-over
- Existing dialog-based assignment remains as a fallback

### Usage Analytics Dashboard
- New **Usage Analytics** collapsible panel with Consumption and Predictions tabs
- **Consumption chart** — horizontal bar chart of usage grouped by material, brand, or color
- **Weekly timeline** — vertical bar chart of weekly consumption trends
- **Reorder predictions** — cards showing estimated days remaining per color based on rolling average
- **Log Usage** action per spool in the All Spools panel (manual grams entry)
- New `usage_logs` database table and migration
- API endpoints: `GET /api/analytics/usage`, `GET /api/analytics/predictions`, `POST /api/analytics/log-usage`

## 0.18.3 -- Move All Spools panel below filament cards + batch print

- **All Spools** overview panel now appears **below** the filament Dashboard cards (last section)
- Multi-select checkboxes with **"Print N Labels"** batch button in All Spools panel

## 0.18.2 -- Multi-select batch print in Spool Overview

The **All Spools** overview panel now has checkboxes on every row. Select
multiple spools (or "Select all"), then click **"Print N Labels"** to open
the batch label dialog with Download All and Print All actions. Much easier
to find than the per-color-row batch registration.

## 0.18.1 -- Fix: filters no longer jump to top of page

Removed the forced `scrollTo(top: 0)` that fired on every filter change.
Material, brand, and color filters now keep your scroll position.

## 0.18.0 -- Spool lifecycle timeline, batch labels, and overview dashboard

Three major spool tracking improvements:

**Spool Lifecycle Timeline** -- Every spool now logs lifecycle events
(created, assigned, unassigned, emptied). Click the clock icon on any spool
to see its full history as a vertical timeline. Existing spools are
backfilled from their timestamps on upgrade.

**Batch Label Printing** -- Register multiple spools at once with a quantity
picker (1-50). After batch creation, a dialog shows all labels with
"Download All" (single PNG) and "Print All" (sequential Niimbot print)
actions.

**Spool Overview Dashboard** -- New collapsible "All Spools" panel between
AMS and the filament cards. Shows every spool instance with status filters
(All/In Stock/In Tray/Empty), search, status pills, and per-row actions
(label, timeline, unassign, empty, delete). Collapse state persists in
localStorage.

## 0.17.4 -- Scan to select spool in Assign dialog

Added a **Scan** button next to the search bar in the "Assign filament to tray"
dialog. Scan a spool's QR code to instantly select that filament in the list
instead of scrolling/searching. The scanned spool's packaging type is also
auto-selected.

## 0.17.3 -- Reliable QR scanning with jsQR

Replaced `BarcodeDetector` (not available on all devices) with **jsQR** —
a pure JavaScript QR decoder that works everywhere by analyzing pixel
data on a canvas. Take a photo of the spool label with the "Take Photo"
button, and jsQR decodes it instantly. Tries full image + center crops
for best detection. Manual UID entry always available as fallback.

## 0.17.2 -- Reliable QR scanning via native BarcodeDetector

Replaced `html5-qrcode` library with the browser's **native BarcodeDetector
API** (Chrome 83+, Safari 15.4+). This is the OS-level barcode engine and
handles phone camera photos far more reliably. Falls back to progressively
cropped canvas attempts if the first pass misses. Bundle size cut in half
(662KB -> 326KB). If QR scanning isn't supported, the manual UID entry
field is shown as the primary option.

## 0.17.1 -- Fix QR scanner: use photo capture instead of live camera

The live camera stream (`getUserMedia`) is blocked inside HA Ingress iframes.
Replaced with a **photo capture** approach: tap the camera button, snap a photo
of the QR code, and the app decodes the spool UID from the image. Also added a
**manual UID entry** field as a fallback.

## 0.17.0 -- In-app QR scanner for scan-to-assign

Added a **Scan** button in the toolbar that opens the phone camera to
scan spool QR codes directly inside the add-on. No more URL/Ingress
issues -- the scanner reads the spool UID from the QR code and opens
the assign dialog immediately. QR codes now encode just the spool UID
(simpler = faster to scan).

## 0.16.15 -- Fix QR code URL for Ingress (scan-to-assign)

QR codes now use the correct user-facing HA Ingress URL format:
`/hassio/ingress/<addon-slug>/` instead of the internal API path.
The add-on auto-detects its slug from the Supervisor API. Scanning a
label QR with the HA Companion app opens the assign dialog correctly.

## 0.16.8 -- Label layout: parameters at bottom, each on own line

Redesigned label layout: filament identity (type, brand, color) stays at
the top, printing parameters (nozzle, bed, chamber, density) are now at
the bottom above the UID row, each on its own separate line.

## 0.16.7 -- Convert Generic ABS to YS Filament ABS

Automatically upgrades the "Generic ABS" filament entry to "YS Filament ABS"
with all TDS data: nozzle 220-260°C, bed 80-110°C, chamber 60°C, density
1.04 g/cm³, and Amazon URL. No manual editing needed.

## 0.16.6 -- Auto-fill filament data from bundled profiles

On startup, the add-on now reads the bundled BambuStudio profiles and
automatically fills in missing filament fields (nozzle temp range, bed
temp range, density). This means labels will show printing parameters
for all filaments that have bundled profiles, without any manual editing.

## 0.16.5 -- Editable filament configuration

Added an Edit button to the Filament Configuration panel. You can now
update brand, material, nozzle/bed/chamber temps, density, and all other
filament details inline without recreating the filament.

## 0.16.4 -- Label printing parameters (bed temp range, chamber temp)

Added bed temperature range and chamber temperature fields to filaments.
Labels now show all major printing parameters: nozzle range, bed range,
chamber temp, and density. The Create Filament dialog also has the new fields.

## 0.15.6 -- Spools & Labels per color row

The "Spools & Labels" button is now below the delete icon on each color
row. Clicking it expands the spool list inline under that specific color.

## 0.15.4 -- Fix update dialog (trimmed changelog)

Trimmed the massive changelog that was preventing HA's update dialog
from enabling the Update button. No code changes from 0.15.3.

## 0.15.2 -- Individual spool tracking + label printing

Track each physical spool/refill individually with a unique `SP-XXXXXXXX` ID
and lifecycle status (in_stock → in_tray → empty). Print QR-code labels for
your Niimbot B21 Pro (50×30mm, 300 DPI) and scan them to assign spools to
AMS trays.

### What's new

- **SpoolInstance model** -- each physical spool or refill gets a unique UID,
  independent of the aggregate ColorStock counters (which still work as before
  for backward compatibility).
- **Label generation** -- 591×354px PNG labels with QR code, brand/material/color,
  nozzle/bed temps, UID, and a color swatch. Download as PNG or print directly
  to a Niimbot B21 Pro over Bluetooth.
- **Scan-to-assign** -- scan a spool's QR code with your phone to open the
  Filament Stock panel with a pre-filled tray assignment dialog.
- **SpoolListPanel** -- expandable panel on each color row listing individual
  spools with status badges, label/assign/empty/delete actions, and a
  "+ Register" button to create new spool records.
- **Migration** -- existing aggregate stock counts are automatically converted
  into individual SpoolInstance records on first startup after the update.

### New add-on options

- `ha_external_url` -- your HA external URL for QR code links (leave empty
  for plain-text QR content).
- `niimbot_address` -- Bluetooth MAC of your Niimbot B21 Pro (leave empty
  to disable direct printing; download-only mode still works).

### New dependencies

- `qrcode[pil]`, `Pillow` (label rendering)
- `bleak`, `bleak-retry-connector` (Bluetooth LE for Niimbot)
- Alpine packages: `dbus`, `bluez`, `ttf-dejavu`
- `host_dbus: true` in config.yaml for BLE access from the container

## 0.14.0 -- Remove custom icon.png to restore HA native update indicator

Removed `icon.png` so the Apps grid uses HA's native update indicator.

*For older changelog entries, see the git history.*
