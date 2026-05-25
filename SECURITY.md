# Security Policy

## Supported Versions

This is a small personal project; only the latest release is supported. Please update to the most recent version before reporting a security issue.

| Component | Supported |
|---|---|
| `addon-filament-stock/` -- latest tag / `main` | Yes |
| `home-assistant/custom_components/filament_stock/` -- latest tag / `main` | Yes |
| Older versions | No |

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security problems. Instead, contact the maintainer privately:

- GitHub Security Advisory (preferred): <https://github.com/nir-azulay/FilmentsSettings/security/advisories/new>
- Or open an issue describing the symptoms (not the exploit) and ask for a private channel.

I will acknowledge receipt within a few days, work with you on a fix on a private branch, and credit you in the release notes when the fix ships.

## Scope

In-scope:
- The FastAPI backend in [`addon-filament-stock/app/`](addon-filament-stock/app/)
- The HA custom integration in [`home-assistant/custom_components/filament_stock/`](home-assistant/custom_components/filament_stock/)
- The HA add-on container surface (Dockerfile, nginx config, s6 services)

Out of scope:
- Bambu Lab firmware, Home Assistant core, or any upstream dependency
- Bambu Studio filament profiles (text JSON files, no executable surface)

## Author

**Nir Azulay** -- <https://github.com/nir-azulay>
