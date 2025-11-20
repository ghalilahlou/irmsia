# 🚀 Script de Démarrage IRMSIA Medical AI - Windows
# Ce script démarre l'environnement de développement complet

Write-Host "🚀 Démarrage d'IRMSIA Medical AI - Environnement de développement" -ForegroundColor Green

# Vérifier si on est dans le bon répertoire
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ Erreur: Veuillez exécuter ce script depuis la racine du projet" -ForegroundColor Red
    exit 1
}

# Créer les dossiers nécessaires
Write-Host "📁 Création des dossiers nécessaires..." -ForegroundColor Blue
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "data/uploads" | Out-Null
New-Item -ItemType Directory -Force -Path "data/models" | Out-Null

# Démarrer les services Docker (PostgreSQL, Redis)
Write-Host "🐳 Démarrage des services Docker..." -ForegroundColor Blue
docker-compose up -d postgres redis

# Attendre que PostgreSQL soit prêt
Write-Host "⏳ Attente que PostgreSQL soit prêt..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Activer l'environnement virtuel Python
Write-Host "🐍 Activation de l'environnement virtuel Python..." -ForegroundColor Blue
Set-Location backend
& "venv\Scripts\Activate.ps1"

# Installer les dépendances backend si nécessaire
Write-Host "📦 Vérification des dépendances backend..." -ForegroundColor Blue
pip install -r requirements.txt

# Démarrer le backend
Write-Host "🔧 Démarrage du backend FastAPI..." -ForegroundColor Blue
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"

# Retourner au répertoire racine
Set-Location ..

# Installer les dépendances frontend si nécessaire
Write-Host "📦 Vérification des dépendances frontend..." -ForegroundColor Blue
Set-Location frontend
npm install

# Démarrer le frontend
Write-Host "🎨 Démarrage du frontend React..." -ForegroundColor Blue
Start-Process -NoNewWindow -FilePath "npm" -ArgumentList "run", "dev"

# Retourner au répertoire racine
Set-Location ..

Write-Host ""
Write-Host "✅ IRMSIA Medical AI est maintenant en cours d'exécution !" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "🛑 Pour arrêter l'application, exécutez: .\scripts\stop-dev.ps1" -ForegroundColor Yellow
Write-Host ""

# Attendre que l'utilisateur appuie sur une touche
Write-Host "Appuyez sur une touche pour arrêter les services..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 