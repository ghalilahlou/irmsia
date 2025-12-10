# Script de nettoyage - Suppression ancien frontend
# IRMSIA Medical AI - Frontend Modernization

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  NETTOYAGE FRONTEND - IRMSIA Medical AI" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Confirmation
Write-Host "Ce script va supprimer le dossier 'frontend/' (ancien frontend Vite)" -ForegroundColor Yellow
Write-Host "Le frontend Next.js moderne ('frontend-next/') sera conservé." -ForegroundColor Green
Write-Host ""
$confirm = Read-Host "Continuer? (Y/N)"

if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "Annulé." -ForegroundColor Red
    exit
}

# Chemin
$oldFrontend = "frontend"
$newFrontend = "frontend-next"

# Vérifier existence
if (-Not (Test-Path $oldFrontend)) {
    Write-Host "❌ Dossier '$oldFrontend' introuvable" -ForegroundColor Red
    exit
}

if (-Not (Test-Path $newFrontend)) {
    Write-Host "⚠️  ATTENTION: Le nouveau frontend '$newFrontend' n'existe pas!" -ForegroundColor Red
    $continue = Read-Host "Continuer quand même? (Y/N)"
    if ($continue -ne "Y" -and $continue -ne "y") {
        exit
    }
}

# Suppression
Write-Host ""
Write-Host "📁 Suppression de '$oldFrontend'..." -ForegroundColor Cyan

try {
    Remove-Item -Path $oldFrontend -Recurse -Force
    Write-Host "✅ Ancien frontend supprimé avec succès!" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur lors de la suppression: $_" -ForegroundColor Red
    exit 1
}

# Mise à jour du docker-compose si présent
$dockerCompose = "docker-compose.yml"
if (Test-Path $dockerCompose) {
    Write-Host ""
    Write-Host "📝 Mise à jour de docker-compose.yml..." -ForegroundColor Cyan
    
    $content = Get-Content $dockerCompose -Raw
    
    if ($content -match "frontend:") {
        Write-Host "⚠️  docker-compose.yml contient encore une référence 'frontend:'" -ForegroundColor Yellow
        Write-Host "   Veuillez mettre à jour manuellement pour utiliser 'frontend-next'" -ForegroundColor Yellow
    }
}

# Résumé
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  ✅ NETTOYAGE TERMINÉ" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📂 Structure finale:" -ForegroundColor White
Write-Host "   ✅ frontend-next/  (Frontend moderne Next.js)" -ForegroundColor Green
Write-Host "   ❌ frontend/       (Supprimé)" -ForegroundColor Red
Write-Host ""
Write-Host "🚀 Pour démarrer le frontend:" -ForegroundColor Cyan
Write-Host "   cd frontend-next" -ForegroundColor Gray
Write-Host "   npm install" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "📖 Documentation complète: FRONTEND_ANOMALY_DETECTION_GUIDE.md" -ForegroundColor Cyan
Write-Host ""


