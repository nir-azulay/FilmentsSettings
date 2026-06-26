$target = "$env:APPDATA\BambuStudio\user\2189385007"
if ($PSScriptRoot) {
    $source = $PSScriptRoot
} else {
    $source = "C:\GitHub\filments settings\DeployPack"
}

Write-Host "Deploying custom profiles to Bambu Studio..." -ForegroundColor Cyan
Write-Host ""

# Clean old profiles first to avoid stale duplicates
Write-Host "  Cleaning old custom profiles..." -ForegroundColor DarkGray
Remove-Item "$target\filament\base\SUNLU*" -Force -ErrorAction SilentlyContinue
Remove-Item "$target\filament\base\Inslogic*" -Force -ErrorAction SilentlyContinue
Remove-Item "$target\filament\SUNLU*" -Force -ErrorAction SilentlyContinue
Remove-Item "$target\filament\Inslogic*" -Force -ErrorAction SilentlyContinue
Remove-Item "$target\process\SUNLU*" -Force -ErrorAction SilentlyContinue
Remove-Item "$target\process\Inslogic*" -Force -ErrorAction SilentlyContinue
# Also clean old my- prefixed profiles
Remove-Item "$target\filament\base\my-*" -Force -ErrorAction SilentlyContinue
Remove-Item "$target\filament\my-*" -Force -ErrorAction SilentlyContinue
Remove-Item "$target\process\my-*" -Force -ErrorAction SilentlyContinue
Write-Host "  Old profiles removed" -ForegroundColor DarkGray

# Filament base profiles (full JSON with all 145 fields)
Copy-Item "$source\*@Bambu Lab H2S.json" "$target\filament\base\" -Force -Exclude "*Calibrated*","*.preset*","*mm @H2S*"
Copy-Item "$source\*@Bambu Lab H2S.info" "$target\filament\base\" -Force -Exclude "*Calibrated*","*.preset*","*mm @H2S*"
Write-Host "  Filament base profiles deployed" -ForegroundColor Green

# Filament user presets (sparse inheriting presets + Calibrated overrides)
Get-ChildItem "$source\*.preset.json" | ForEach-Object {
    $dest = $_.Name -replace '\.preset\.json$', '.json'
    Copy-Item $_.FullName "$target\filament\$dest" -Force
}
Get-ChildItem "$source\*.preset.info" | ForEach-Object {
    $dest = $_.Name -replace '\.preset\.info$', '.info'
    Copy-Item $_.FullName "$target\filament\$dest" -Force
}
Copy-Item "$source\*Calibrated.json" "$target\filament\" -Force
Copy-Item "$source\*Calibrated.info" "$target\filament\" -Force
Write-Host "  Filament user presets deployed" -ForegroundColor Green

# Process presets
Copy-Item "$source\*mm @H2S*nozzle.json" "$target\process\" -Force
Copy-Item "$source\*mm @H2S*nozzle.info" "$target\process\" -Force
Write-Host "  Process presets deployed" -ForegroundColor Green

Write-Host ""
Write-Host "Done! Restart Bambu Studio to see the profiles." -ForegroundColor Yellow
