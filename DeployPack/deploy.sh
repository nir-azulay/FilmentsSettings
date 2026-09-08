#!/usr/bin/env bash
# Deploy custom BambuStudio profiles to the local BambuStudio installation.
# Works on macOS. Windows users should use deploy.ps1 instead.
set -euo pipefail

BAMBU="$HOME/Library/Application Support/BambuStudio/user/2189385007"
SOURCE="$(cd "$(dirname "$0")" && pwd)"

echo "Deploying custom profiles to Bambu Studio..."
echo ""

# Clean old profiles
echo "  Cleaning old custom profiles..."
rm -f "$BAMBU/filament/base/SUNLU"* "$BAMBU/filament/base/Inslogic"* 2>/dev/null || true
rm -f "$BAMBU/filament/SUNLU"* "$BAMBU/filament/Inslogic"* 2>/dev/null || true
rm -f "$BAMBU/process/SUNLU"* "$BAMBU/process/Inslogic"* 2>/dev/null || true
rm -f "$BAMBU/filament/base/my-"* "$BAMBU/filament/my-"* "$BAMBU/process/my-"* 2>/dev/null || true
echo "  Old profiles removed"

# Base filament profiles
for f in "$SOURCE"/*@Bambu\ Lab\ H2S.json "$SOURCE"/*@Bambu\ Lab\ H2S.info; do
    base=$(basename "$f")
    case "$base" in *Calibrated*|*preset*|*mm\ @H2S*) continue ;; esac
    cp "$f" "$BAMBU/filament/base/"
done
echo "  Filament base profiles deployed ✓"

# User presets (sparse .preset.* -> rename) + Calibrated overrides
for f in "$SOURCE"/*.preset.json; do cp "$f" "$BAMBU/filament/$(basename "$f" .preset.json).json"; done
for f in "$SOURCE"/*.preset.info; do cp "$f" "$BAMBU/filament/$(basename "$f" .preset.info).info"; done
cp "$SOURCE"/*Calibrated.json "$BAMBU/filament/" 2>/dev/null || true
cp "$SOURCE"/*Calibrated.info "$BAMBU/filament/" 2>/dev/null || true
echo "  Filament user presets deployed ✓"

# Process presets
cp "$SOURCE"/*mm\ @H2S*nozzle.json "$BAMBU/process/" 2>/dev/null || true
cp "$SOURCE"/*mm\ @H2S*nozzle.info "$BAMBU/process/" 2>/dev/null || true
echo "  Process presets deployed ✓"

echo ""
echo "Done! Restart Bambu Studio to see the profiles."
