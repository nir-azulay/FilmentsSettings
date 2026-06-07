# Changelog

## 0.15.5 -- Move Spools & Labels to card footer

Moved the "Spools & Labels" button from inside each color row to the
card's action area (below Delete). Clicking it expands a panel showing
all colors with their individual spool records, labels, and actions.

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
