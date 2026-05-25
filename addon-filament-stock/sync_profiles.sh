#!/usr/bin/env bash
# Refresh addon-filament-stock/profiles/ from the canonical BambuStudio
# profile source folders at the repo root (SUNLU/, Inslogic/).
#
# These files get baked into the add-on Docker image and served by the
# in-app "BambuStudio profile" downloader. Re-run this whenever you add or
# regenerate a filament profile via SUNLU/PETG-HS/gen_sunlu_petg_hs.py or
# by hand.
#
# Filters out:
#   - my-* legacy names (per .cursor/rules/add-filament.mdc: "names do NOT
#     use a my- prefix")
#   - *Calibrated* user overrides (per-printer, not for redistribution)
#   - baseline_full_filament* (template / clone source, not a real profile)
#   - TDS PDFs, READMEs, generator scripts

set -euo pipefail

cd "$(dirname "$0")"

REPO_ROOT="$(cd .. && pwd)"
DEST="$(pwd)/profiles"

mkdir -p "$DEST"
# Wipe and re-copy so removed source files disappear from the bundle too.
rm -f "$DEST"/*.json "$DEST"/*.info

shopt -s nullglob
for src in "$REPO_ROOT"/SUNLU/PETG-HS/*.json "$REPO_ROOT"/SUNLU/PETG-HS/*.info \
           "$REPO_ROOT"/Inslogic/*.json "$REPO_ROOT"/Inslogic/*.info; do
    base="$(basename "$src")"
    case "$base" in
        my-*|*Calibrated*|baseline_full_filament*) continue ;;
    esac
    cp -- "$src" "$DEST/"
done

count=$(find "$DEST" -maxdepth 1 -type f \( -name '*.json' -o -name '*.info' \) | wc -l | tr -d ' ')
if [[ "$count" -eq 0 ]]; then
    echo "sync_profiles: no profile files found in SUNLU/ or Inslogic/; nothing copied" >&2
    exit 1
fi
# Quiet by default. Set SYNC_PROFILES_VERBOSE=1 to print the count.
if [[ -n "${SYNC_PROFILES_VERBOSE:-}" ]]; then
    echo "Synced $count files into $DEST"
fi
