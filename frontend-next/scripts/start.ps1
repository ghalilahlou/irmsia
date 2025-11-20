# Script de demarrage - Frontend Next.js
# PowerShell

Write-Host "Demarrage Frontend IRMSIA" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Verifier que .env.local existe
if (-not (Test-Path ".env.local")) {
    Write-Host "ATTENTION: Fichier .env.local non trouve" -ForegroundColor Yellow
    if (Test-Path "env.example") {
        Write-Host "Creation de .env.local depuis env.example..." -ForegroundColor Yellow
        Copy-Item env.example .env.local
        Write-Host "OK: .env.local cree" -ForegroundColor Green
    } else {
        Write-Host "ERREUR: Fichier env.example non trouve" -ForegroundColor Red
        exit 1
    }
}

# Verifier que node_modules existe
if (-not (Test-Path "node_modules")) {
    Write-Host "Installation des dependances..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERREUR: Installation des dependances echouee" -ForegroundColor Red
        exit 1
    }
    Write-Host "OK: Dependances installees" -ForegroundColor Green
}

# Lancer le serveur de developpement
Write-Host ""
Write-Host "Demarrage du serveur de developpement..." -ForegroundColor Green
Write-Host "Frontend disponible sur: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Appuyez sur Ctrl+C pour arreter" -ForegroundColor Yellow
Write-Host ""

npm run dev

