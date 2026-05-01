$target = "$env:APPDATA\BambuStudio\user\2189385007"
$source = $PSScriptRoot

Write-Host "Deploying my- profiles to Bambu Studio..." -ForegroundColor Cyan

# Filament base profiles (full JSON with all settings)
Copy-Item "$source\my-*@Bambu Lab H2S*nozzle.json" "$target\filament\base\" -Force
Copy-Item "$source\my-*@Bambu Lab H2S*nozzle.info" "$target\filament\base\" -Force
Write-Host "  Filament base profiles deployed" -ForegroundColor Green

# Filament user presets (including Calibrated)
Copy-Item "$source\my-*@Bambu Lab H2S*nozzle.json" "$target\filament\" -Force
Copy-Item "$source\my-*@Bambu Lab H2S*nozzle.info" "$target\filament\" -Force
Copy-Item "$source\my-*Calibrated.json" "$target\filament\" -Force
Copy-Item "$source\my-*Calibrated.info" "$target\filament\" -Force
Write-Host "  Filament user presets deployed" -ForegroundColor Green

# Process presets
Copy-Item "$source\my-*mm @H2S*nozzle.json" "$target\process\" -Force
Copy-Item "$source\my-*mm @H2S*nozzle.info" "$target\process\" -Force
Write-Host "  Process presets deployed" -ForegroundColor Green

Write-Host ""
Write-Host "Done! Restart Bambu Studio to see the profiles." -ForegroundColor Yellow
