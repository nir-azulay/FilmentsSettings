$target = "$env:APPDATA\BambuStudio\user\2189385007"
$source = $PSScriptRoot

Write-Host "Deploying azul- profiles to Bambu Studio..." -ForegroundColor Cyan

Copy-Item "$source\filament\base\azul-*" "$target\filament\base\" -Force
Write-Host "  Filament base profiles deployed" -ForegroundColor Green

Copy-Item "$source\filament\azul-*" "$target\filament\" -Force
Write-Host "  Filament user presets deployed" -ForegroundColor Green

Copy-Item "$source\process\azul-*" "$target\process\" -Force
Write-Host "  Process presets deployed" -ForegroundColor Green

Write-Host ""
Write-Host "Done! Restart Bambu Studio to see the profiles." -ForegroundColor Yellow
