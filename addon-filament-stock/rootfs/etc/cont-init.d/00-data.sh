#!/usr/bin/with-contenv bashio
# ==============================================================================
# Ensure /data is present and writable before either service starts. /data is a
# persistent volume managed by HA Supervisor and is included in HA snapshots.
# ==============================================================================
mkdir -p /data
chmod 700 /data
bashio::log.info "Data directory ready at /data"
