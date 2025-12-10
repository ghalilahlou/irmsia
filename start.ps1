# IRMSIA - Script de demarrage
# Usage: .\start.ps1 [backend|frontend|all]

param(
    [Parameter(Position=0)]
    [ValidateSet("backend", "frontend", "all")]
    [string]$Mode = "all"
)

$ErrorActionPreference = "Stop"

function Write-Title {
    param([string]$Text)
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor White
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host ""
}

function Start-Backend {
    Write-Title "Demarrage du Backend"
    
    Push-Location backend
    
    # Verifier l'environnement virtuel
    if (-not (Test-Path "venv")) {
        Write-Host "Creation de l'environnement virtuel..." -ForegroundColor Yellow
        python -m venv venv
    }
    
    # Activer l'environnement
    .\venv\Scripts\Activate.ps1
    
    # Installer les dependances si necessaire
    if (-not (Test-Path "venv\Lib\site-packages\fastapi")) {
        Write-Host "Installation des dependances..." -ForegroundColor Yellow
        pip install -r requirements.txt
    }
    
    Write-Host "Backend en cours de demarrage sur http://localhost:8000" -ForegroundColor Green
    Write-Host "Documentation API: http://localhost:8000/docs" -ForegroundColor Cyan
    
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    
    Pop-Location
}

function Start-Frontend {
    Write-Title "Demarrage du Frontend"
    
    Push-Location frontend-next
    
    # Installer les dependances si necessaire
    if (-not (Test-Path "node_modules")) {
        Write-Host "Installation des dependances npm..." -ForegroundColor Yellow
        npm install
    }
    
    Write-Host "Frontend en cours de demarrage sur http://localhost:3000" -ForegroundColor Green
    
    npm run dev
    
    Pop-Location
}

function Start-All {
    Write-Title "Demarrage de IRMSIA"
    
    # Backend en arriere-plan
    Write-Host "Lancement du backend en arriere-plan..." -ForegroundColor Yellow
    $backend = Start-Process powershell -ArgumentList "-NoProfile -Command `"cd backend; .\venv\Scripts\Activate.ps1; uvicorn main:app --reload --host 0.0.0.0 --port 8000`"" -PassThru
    
    Start-Sleep -Seconds 3
    
    # Frontend
    Write-Host "Lancement du frontend..." -ForegroundColor Yellow
    Start-Frontend
}

# Execution
switch ($Mode) {
    "backend" { Start-Backend }
    "frontend" { Start-Frontend }
    "all" { Start-All }
}

