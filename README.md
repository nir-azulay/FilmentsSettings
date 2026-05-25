# FilmentsSettings

3D-printing toolkit for [Bambu Lab](https://bambulab.com/) printers built and maintained by **[Nir Azulay](https://github.com/nir-azulay)**. Two independent pieces share this repo:

| What | Where |
|---|---|
| **Filament Stock for Home Assistant** -- native HA add-on + integration + blueprints for tracking spools and wiring them to AMS automations | [`addon-filament-stock/`](addon-filament-stock/) + [`home-assistant/`](home-assistant/) |
| **Bambu Lab filament profiles** -- tested filament + process JSON profiles for the H2S, with the generators that produced them | [`SUNLU/`](SUNLU/), [`Inslogic/`](Inslogic/), [`DeployPack/`](DeployPack/) |

## Filament Stock for Home Assistant

Inventory dashboard, low-stock alerts, and full Home Assistant integration so your AMS trays auto-decrement spools, your push notifications fire when a print starts on a depleted color, and your weekly digest shows what to restock. Tracks **spools and refills independently per color** -- the same color can hold both packaging types side by side. Add-on 0.5.0+ also renders a live **AMS Status panel** showing what's loaded in each Bambu AMS slot right now, cross-referenced with your stock.

**[Setup guide -> home-assistant/README.md](home-assistant/README.md)**

Components:
- [`addon-filament-stock/`](addon-filament-stock/) -- HA Supervisor add-on (FastAPI + React + SQLite, served via HA Ingress).
- [`home-assistant/custom_components/filament_stock/`](home-assistant/custom_components/filament_stock/) -- HACS integration that exposes one `sensor.filament_*` per filament plus 4 services for use/restock automations.
- [`home-assistant/blueprints/automation/filament_stock/`](home-assistant/blueprints/automation/filament_stock/) -- three importable automations bridging Bambu Lab and Filament Stock.

## Bambu filament profiles

Per-filament folders contain Bambu Studio user profile JSONs, process presets, and the manufacturer TDS PDF. A Python generator script drives them so changes propagate consistently across all four nozzle sizes (0.2 / 0.4 / 0.6 / 0.8mm).

The full workflow for adding a new filament is documented in [`.cursor/rules/add-filament.mdc`](.cursor/rules/add-filament.mdc).

## First-time setup (contributors / maintainers)

If you're going to edit profile JSONs in `SUNLU/` or `Inslogic/`, install the
repo's git hooks once per clone so the add-on's bundled profile mirror stays in
sync automatically:

```bash
./scripts/install-git-hooks.sh
```

That sets `core.hooksPath` to `.githooks/` for this repo (no global git
config touched). The `pre-commit` hook re-runs `addon-filament-stock/sync_profiles.sh`
whenever a commit modifies a profile source file, and stages the resulting
`addon-filament-stock/profiles/` changes alongside your edits. See
[`addon-filament-stock/README.md`](addon-filament-stock/README.md#keeping-the-bundle-in-sync)
for details.

## Author

**Nir Azulay** -- <https://github.com/nir-azulay>

## License

MIT -- see [LICENSE](LICENSE).
