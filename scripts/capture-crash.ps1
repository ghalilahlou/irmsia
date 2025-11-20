# Script de capture de crash - IRMSIA Medical AI
# Capture les erreurs lors du demarrage

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CAPTURE DE CRASH" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ce script va demarrer l'application et capturer toutes les erreurs" -ForegroundColor Yellow
Write-Host "Appuyez sur Ctrl+C pour arreter" -ForegroundColor Gray
Write-Host ""

# Verifier qu'on est a la racine
if (-not (Test-Path "backend\main.py")) {
    Write-Host "ERREUR: Executez depuis la racine du projet" -ForegroundColor Red
    exit 1
}

# Activer l'environnement virtuel
if (Test-Path "backend\venv\Scripts\activate.ps1") {
    & "backend\venv\Scripts\activate.ps1"
} else {
    Write-Host "ERREUR: Environnement virtuel non trouve" -ForegroundColor Red
    exit 1
}

# Creer le fichier de log
$logFile = "crash-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
Write-Host "Les logs seront sauvegardes dans: $logFile" -ForegroundColor Cyan
Write-Host ""

# Demarrer l'application et capturer les erreurs
try {
    python -m backend.main 2>&1 | Tee-Object -FilePath $logFile
} catch {
    Write-Host ""
    Write-Host "ERREUR CAPTUREE:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Add-Content -Path $logFile -Value "`nERREUR: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Logs sauvegardes dans: $logFile" -ForegroundColor Yellow
}

