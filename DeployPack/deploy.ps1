$target = "$env:APPDATA\BambuStudio\user\2189385007"
if ($PSScriptRoot) {
    $source = $PSScriptRoot
} else {
    $source = "C:\GitHub\filments settings\DeployPack"
}

Write-Host "Deploying my- profiles to Bambu Studio..." -ForegroundColor Cyan
Write-Host ""

# Clean old profiles first to avoid stale duplicates
Write-Host "  Cleaning old my- profiles..." -ForegroundColor DarkGray
Remove-Item "$target\filament\base\my-*" -Force -ErrorAction SilentlyContinue
Remove-Item "$target\filament\my-*" -Force -ErrorAction SilentlyContinue
Remove-Item "$target\process\my-*" -Force -ErrorAction SilentlyContinue
Write-Host "  Old profiles removed" -ForegroundColor DarkGray

# Filament base profiles (full JSON with all 145 fields)
Copy-Item "$source\my-*@Bambu Lab H2S*nozzle.json" "$target\filament\base\" -Force
Copy-Item "$source\my-*@Bambu Lab H2S*nozzle.info" "$target\filament\base\" -Force
Write-Host "  Filament base profiles deployed" -ForegroundColor Green

# Filament user presets (sparse inheriting presets + Calibrated overrides)
Get-ChildItem "$source\my-*.preset.json" | ForEach-Object {
    $dest = $_.Name -replace '\.preset\.json$', '.json'
    Copy-Item $_.FullName "$target\filament\$dest" -Force
}
Get-ChildItem "$source\my-*.preset.info" | ForEach-Object {
    $dest = $_.Name -replace '\.preset\.info$', '.info'
    Copy-Item $_.FullName "$target\filament\$dest" -Force
}
Copy-Item "$source\my-*Calibrated.json" "$target\filament\" -Force
Copy-Item "$source\my-*Calibrated.info" "$target\filament\" -Force
Write-Host "  Filament user presets deployed" -ForegroundColor Green

# Process presets
Copy-Item "$source\my-*mm @H2S*nozzle.json" "$target\process\" -Force
Copy-Item "$source\my-*mm @H2S*nozzle.info" "$target\process\" -Force
Write-Host "  Process presets deployed" -ForegroundColor Green

Write-Host ""
Write-Host "Done! Restart Bambu Studio to see the profiles." -ForegroundColor Yellow
