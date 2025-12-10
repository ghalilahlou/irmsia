# Script de déploiement Docker pour IRMSIA
# Ce script construit et démarre tous les services avec Docker Compose

param(
    [switch]$Build,
    [switch]$Up,
    [switch]$Down,
    [switch]$Logs,
    [switch]$Restart,
    [string]$Service = ""
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  IRMSIA - Déploiement Docker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que Docker est installé
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker n'est pas installé!" -ForegroundColor Red
    Write-Host "   Installez Docker Desktop depuis: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Vérifier que Docker Compose est disponible
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue) -and 
    -not (docker compose version 2>$null)) {
    Write-Host "❌ Docker Compose n'est pas disponible!" -ForegroundColor Red
    exit 1
}

# Vérifier que Docker est en cours d'exécution
try {
    docker ps | Out-Null
} catch {
    Write-Host "❌ Docker n'est pas en cours d'exécution!" -ForegroundColor Red
    Write-Host "   Démarrez Docker Desktop et réessayez." -ForegroundColor Yellow
    exit 1
}

# Vérifier les fichiers d'environnement
$envFile = ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "⚠️  Fichier .env non trouvé!" -ForegroundColor Yellow
    Write-Host "   Création d'un fichier .env à partir de env.example..." -ForegroundColor Yellow
    
    if (Test-Path "env.example") {
        Copy-Item "env.example" $envFile
        Write-Host "✅ Fichier .env créé. Veuillez le modifier avec vos valeurs!" -ForegroundColor Green
    } else {
        Write-Host "❌ env.example non trouvé!" -ForegroundColor Red
        exit 1
    }
}

# Fonction pour construire les images
function Build-Images {
    Write-Host "🔨 Construction des images Docker..." -ForegroundColor Cyan
    Write-Host ""
    
    docker-compose build --no-cache
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Images construites avec succès!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ Erreur lors de la construction des images!" -ForegroundColor Red
        exit 1
    }
}

# Fonction pour démarrer les services
function Start-Services {
    Write-Host "🚀 Démarrage des services Docker..." -ForegroundColor Cyan
    Write-Host ""
    
    docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Services démarrés avec succès!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📊 Statut des services:" -ForegroundColor Cyan
        docker-compose ps
        Write-Host ""
        Write-Host "🌐 URLs:" -ForegroundColor Cyan
        Write-Host "   Frontend:  http://localhost:3000" -ForegroundColor White
        Write-Host "   Backend:   http://localhost:8000" -ForegroundColor White
        Write-Host "   API Docs:  http://localhost:8000/docs" -ForegroundColor White
        Write-Host "   gRPC:      localhost:50051" -ForegroundColor White
        Write-Host ""
        Write-Host "📝 Pour voir les logs: .\scripts\deploy-docker.ps1 -Logs" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "❌ Erreur lors du démarrage des services!" -ForegroundColor Red
        exit 1
    }
}

# Fonction pour arrêter les services
function Stop-Services {
    Write-Host "🛑 Arrêt des services Docker..." -ForegroundColor Cyan
    Write-Host ""
    
    docker-compose down
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Services arrêtés avec succès!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ Erreur lors de l'arrêt des services!" -ForegroundColor Red
        exit 1
    }
}

# Fonction pour afficher les logs
function Show-Logs {
    if ($Service) {
        Write-Host "📋 Logs du service: $Service" -ForegroundColor Cyan
        docker-compose logs -f $Service
    } else {
        Write-Host "📋 Logs de tous les services" -ForegroundColor Cyan
        docker-compose logs -f
    }
}

# Fonction pour redémarrer les services
function Restart-Services {
    Write-Host "🔄 Redémarrage des services Docker..." -ForegroundColor Cyan
    Write-Host ""
    
    docker-compose restart
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Services redémarrés avec succès!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ Erreur lors du redémarrage des services!" -ForegroundColor Red
        exit 1
    }
}

# Exécution des commandes
if ($Build) {
    Build-Images
} elseif ($Up) {
    Start-Services
} elseif ($Down) {
    Stop-Services
} elseif ($Logs) {
    Show-Logs
} elseif ($Restart) {
    Restart-Services
} else {
    # Mode interactif par défaut
    Write-Host "Que souhaitez-vous faire?" -ForegroundColor Cyan
    Write-Host "1. Construire les images" -ForegroundColor White
    Write-Host "2. Démarrer les services" -ForegroundColor White
    Write-Host "3. Construire et démarrer" -ForegroundColor White
    Write-Host "4. Arrêter les services" -ForegroundColor White
    Write-Host "5. Voir les logs" -ForegroundColor White
    Write-Host "6. Redémarrer les services" -ForegroundColor White
    Write-Host ""
    $choice = Read-Host "Votre choix (1-6)"
    
    switch ($choice) {
        "1" { Build-Images }
        "2" { Start-Services }
        "3" { Build-Images; Start-Services }
        "4" { Stop-Services }
        "5" { Show-Logs }
        "6" { Restart-Services }
        default {
            Write-Host "❌ Choix invalide!" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Déploiement terminé!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

