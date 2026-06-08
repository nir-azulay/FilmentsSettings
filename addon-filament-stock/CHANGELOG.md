# Changelog

## 0.16.14 -- Fix QR code URL for Ingress (scan-to-assign)

QR codes on spool labels now use the correct HA Ingress path instead of
a bare `/filaments/` path. The add-on auto-detects its Ingress entry
from the Supervisor API, so scanning a label QR code with your phone
camera now opens the assign dialog correctly via Nabu Casa or local URL.

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
