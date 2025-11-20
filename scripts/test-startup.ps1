# Script de test de demarrage - IRMSIA Medical AI
# Teste le demarrage et capture les erreurs

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TEST DE DEMARRAGE BACKEND" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verifier qu'on est a la racine
if (-not (Test-Path "backend\main.py")) {
    Write-Host "ERREUR: Executez depuis la racine du projet" -ForegroundColor Red
    exit 1
}

# Activer l'environnement virtuel
if (Test-Path "backend\venv\Scripts\activate.ps1") {
    Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Yellow
    & "backend\venv\Scripts\activate.ps1"
} else {
    Write-Host "ERREUR: Environnement virtuel non trouve" -ForegroundColor Red
    exit 1
}

# Test 1: Import de la configuration
Write-Host ""
Write-Host "[Test 1] Import de la configuration..." -ForegroundColor Yellow
try {
    $result = python -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path('.').absolute())); from backend.core.config import settings; print('OK')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK: Configuration importee" -ForegroundColor Green
    } else {
        Write-Host "  ERREUR: $result" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ERREUR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Import du SecurityManager
Write-Host ""
Write-Host "[Test 2] Import du SecurityManager..." -ForegroundColor Yellow
try {
    $result = python -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path('.').absolute())); from backend.core.security import security_manager; print('OK')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK: SecurityManager importe" -ForegroundColor Green
    } else {
        Write-Host "  ERREUR: $result" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ERREUR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 3: Import de l'application FastAPI
Write-Host ""
Write-Host "[Test 3] Import de l'application FastAPI..." -ForegroundColor Yellow
try {
    $result = python -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path('.').absolute())); from backend.main import app; print('OK')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK: Application FastAPI importee" -ForegroundColor Green
    } else {
        Write-Host "  ERREUR: $result" -ForegroundColor Red
        Write-Host "  Details complets:" -ForegroundColor Gray
        $result | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
        exit 1
    }
} catch {
    Write-Host "  ERREUR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 4: Demarrage avec timeout (5 secondes)
Write-Host ""
Write-Host "[Test 4] Test de demarrage avec timeout (5 secondes)..." -ForegroundColor Yellow
Write-Host "  (Si l'application crash, vous verrez l'erreur ci-dessous)" -ForegroundColor Gray
Write-Host ""

$job = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & "backend\venv\Scripts\python.exe" -m backend.main
}

Start-Sleep -Seconds 5

if ($job.State -eq "Running") {
    Write-Host "  OK: Application demarree et fonctionne" -ForegroundColor Green
    Stop-Job $job
    Remove-Job $job
} else {
    $output = Receive-Job $job
    Write-Host "  ERREUR: Application a crash ou erreur detectee" -ForegroundColor Red
    Write-Host "  Sortie:" -ForegroundColor Yellow
    $output | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
    Remove-Job $job
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TOUS LES TESTS REUSSIS" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "L'application peut etre demarree avec:" -ForegroundColor Cyan
Write-Host "  .\scripts\start.ps1" -ForegroundColor White

