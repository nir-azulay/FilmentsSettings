"""Constants for the Filament Stock integration."""

DOMAIN = "filament_stock"

# Configuration keys (used in config_flow and __init__).
CONF_BASE_URL = "base_url"
CONF_POLL_INTERVAL = "poll_interval"

# Defaults. Inside the HA hassio docker network, custom add-ons are reachable
# at hostname "addon_<slug_with_underscores>" (e.g. "addon_filament_stock") on
# the port declared by ingress_port in the add-on's config.yaml. The default
# below assumes the add-on slug "filament_stock" and ingress_port 8099.
# Users on non-standard installs can override this in the config flow.
DEFAULT_BASE_URL = "http://addon_filament_stock:8099"
DEFAULT_POLL_INTERVAL = 30  # seconds

# Manufacturer string shown on each filament Device card in HA.
MANUFACTURER = "Filament Stock"

# Status values that mirror the backend (app/models.py).
STATUS_IN_STOCK = "in_stock"
STATUS_ORDERED = "ordered"
STATUS_OUT_OF_STOCK = "out_of_stock"
