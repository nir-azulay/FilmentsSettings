#!/usr/bin/with-contenv bashio
# ==============================================================================
# Ensure /config/data exists and is writable before either service starts.
# /config maps to \\homeassistant\addon_configs\filament_stock\ via Samba and is
# included in HA snapshots; /config/data holds filaments.db.
# ==============================================================================
mkdir -p /config/data
chmod 755 /config
chmod 700 /config/data
bashio::log.info "Data directory ready at /config/data"
