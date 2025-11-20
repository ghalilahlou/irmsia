# Script de demarrage avec Docker - IRMSIA Medical AI
# PowerShell

Write-Host "Demarrage IRMSIA Medical AI avec Docker" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Verifier Docker
Write-Host "Verification de Docker..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    Write-Host "OK: Docker trouve" -ForegroundColor Green
} catch {
    Write-Host "ERREUR: Docker n'est pas installe ou pas dans le PATH" -ForegroundColor Red
    Write-Host "Installez Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Verifier Docker Compose
Write-Host "Verification de Docker Compose..." -ForegroundColor Yellow
try {
    docker-compose --version | Out-Null
    Write-Host "OK: Docker Compose trouve" -ForegroundColor Green
} catch {
    Write-Host "ERREUR: Docker Compose n'est pas installe" -ForegroundColor Red
    exit 1
}

# Verifier que .env existe
if (-not (Test-Path .env)) {
    Write-Host "ERREUR: Fichier .env non trouve" -ForegroundColor Red
    Write-Host "Executez d'abord: .\scripts\setup.ps1" -ForegroundColor Yellow
    exit 1
}

# Construire et lancer les conteneurs
Write-Host ""
Write-Host "Construction des images Docker..." -ForegroundColor Yellow
docker-compose build

Write-Host ""
Write-Host "Demarrage des conteneurs..." -ForegroundColor Yellow
docker-compose up -d

Write-Host ""
Write-Host "Attente du demarrage..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Verifier le statut
Write-Host ""
Write-Host "Statut des conteneurs:" -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "OK: Application demarree !" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "URLs:" -ForegroundColor Yellow
Write-Host "   API: http://localhost:8000" -ForegroundColor White
Write-Host "   Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Health Check: http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "Commandes utiles:" -ForegroundColor Yellow
Write-Host "   Voir les logs: docker-compose logs -f backend" -ForegroundColor Gray
Write-Host "   Arreter: docker-compose down" -ForegroundColor Gray
Write-Host "   Redemarrer: docker-compose restart" -ForegroundColor Gray
Write-Host ""

