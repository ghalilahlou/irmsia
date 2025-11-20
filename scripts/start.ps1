# Script de demarrage - IRMSIA Medical AI
# PowerShell

Write-Host "Demarrage IRMSIA Medical AI" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Verifier qu'on est a la racine du projet
if (-not (Test-Path "backend\main.py") -or -not (Test-Path "scripts\start.ps1")) {
    Write-Host "ERREUR: Ce script doit etre execute depuis la racine du projet" -ForegroundColor Red
    Write-Host "Repertoire actuel: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "" -ForegroundColor Yellow
    Write-Host "Revenez a la racine avec:" -ForegroundColor Yellow
    Write-Host "  cd C:\Users\ghali\irmsia" -ForegroundColor Cyan
    Write-Host "" -ForegroundColor Yellow
    Write-Host "Puis relancez:" -ForegroundColor Yellow
    Write-Host "  .\scripts\start.ps1" -ForegroundColor Cyan
    exit 1
}

# Verifier que .env existe
if (-not (Test-Path .env)) {
    Write-Host "ERREUR: Fichier .env non trouve" -ForegroundColor Red
    Write-Host "Executez d'abord: .\scripts\setup.ps1" -ForegroundColor Yellow
    exit 1
}

# Verifier les repertoires
$directories = @("storage\uploads", "storage\encrypted", "storage\png", "logs")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
}

# Activer l'environnement virtuel depuis la racine
if (Test-Path "backend\venv\Scripts\activate.ps1") {
    Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Yellow
    & "backend\venv\Scripts\activate.ps1"
} else {
    Write-Host "ATTENTION: Environnement virtuel non trouve" -ForegroundColor Yellow
    Write-Host "Executez d'abord: .\scripts\setup.ps1" -ForegroundColor Yellow
}

# Verifier que les dependances sont installees
Write-Host "Verification des dependances..." -ForegroundColor Yellow
try {
    python -c "import fastapi" 2>&1 | Out-Null
    Write-Host "OK: Dependances installees" -ForegroundColor Green
} catch {
    Write-Host "ERREUR: Dependances manquantes" -ForegroundColor Red
    Write-Host "Installation des dependances..." -ForegroundColor Yellow
    cd backend
    pip install -r requirements.txt
    cd ..
}

# Lancer l'application depuis la racine
Write-Host ""
Write-Host "Demarrage de l'application..." -ForegroundColor Green
Write-Host "API disponible sur: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Appuyez sur Ctrl+C pour arreter" -ForegroundColor Yellow
Write-Host ""

# Lancer depuis la racine pour que les imports fonctionnent
python -m backend.main

