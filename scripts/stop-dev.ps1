# 🛑 Script d'Arrêt IRMSIA Medical AI - Windows
# Ce script arrête proprement l'environnement de développement

Write-Host "🛑 Arrêt d'IRMSIA Medical AI - Environnement de développement" -ForegroundColor Yellow

# Arrêter les processus en cours
Write-Host "🔧 Arrêt du backend..." -ForegroundColor Blue
Get-Process | Where-Object {$_.ProcessName -eq "python" -and $_.CommandLine -like "*uvicorn*"} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "🎨 Arrêt du frontend..." -ForegroundColor Blue
Get-Process | Where-Object {$_.ProcessName -eq "node" -and $_.CommandLine -like "*vite*"} | Stop-Process -Force -ErrorAction SilentlyContinue

# Arrêter les services Docker
Write-Host "🐳 Arrêt des services Docker..." -ForegroundColor Blue
docker-compose down

Write-Host "✅ IRMSIA Medical AI a été arrêté avec succès !" -ForegroundColor Green 