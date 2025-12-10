# Script de déploiement sur GitHub pour IRMSIA
# Ce script prépare et pousse le projet sur GitHub

Write-Host "🚀 Préparation du déploiement IRMSIA sur GitHub" -ForegroundColor Cyan
Write-Host ""

# Vérifier que Git est installé
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git n'est pas installé. Veuillez installer Git d'abord." -ForegroundColor Red
    exit 1
}

# Vérifier que nous sommes dans le bon répertoire
if (-not (Test-Path "backend") -or -not (Test-Path "frontend-next")) {
    Write-Host "❌ Ce script doit être exécuté depuis la racine du projet IRMSIA" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Vérification de l'état Git..." -ForegroundColor Yellow
$gitStatus = git status --porcelain
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors de la vérification de l'état Git" -ForegroundColor Red
    exit 1
}

# Vérifier les fichiers sensibles
Write-Host ""
Write-Host "🔒 Vérification des fichiers sensibles..." -ForegroundColor Yellow
$sensitiveFiles = @(
    ".env",
    "backend/.env",
    "frontend-next/.env",
    "backend/medical_audit.db",
    "medical_audit.db"
)

$foundSensitive = $false
foreach ($file in $sensitiveFiles) {
    if (Test-Path $file) {
        $gitStatus = git check-ignore $file 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠️  Attention: $file existe et n'est pas ignoré par Git!" -ForegroundColor Yellow
            $foundSensitive = $true
        }
    }
}

if ($foundSensitive) {
    Write-Host ""
    Write-Host "⚠️  Des fichiers sensibles ont été détectés. Assurez-vous qu'ils sont dans .gitignore!" -ForegroundColor Yellow
    $continue = Read-Host "Continuer quand même? (o/N)"
    if ($continue -ne "o" -and $continue -ne "O") {
        Write-Host "❌ Déploiement annulé" -ForegroundColor Red
        exit 1
    }
}

# Afficher les fichiers modifiés
Write-Host ""
Write-Host "📝 Fichiers à commiter:" -ForegroundColor Cyan
git status --short

Write-Host ""
$confirm = Read-Host "Voulez-vous ajouter tous les fichiers et créer un commit? (o/N)"
if ($confirm -ne "o" -and $confirm -ne "O") {
    Write-Host "❌ Déploiement annulé" -ForegroundColor Red
    exit 1
}

# Ajouter les fichiers
Write-Host ""
Write-Host "➕ Ajout des fichiers..." -ForegroundColor Yellow
git add .

# Créer le commit
Write-Host ""
$commitMessage = Read-Host "Message de commit (ou appuyez sur Entrée pour utiliser le message par défaut)"
if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $commitMessage = "Deploy IRMSIA project to GitHub - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
}

Write-Host "💾 Création du commit..." -ForegroundColor Yellow
git commit -m $commitMessage

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors de la création du commit" -ForegroundColor Red
    exit 1
}

# Vérifier si un remote existe
Write-Host ""
Write-Host "🔗 Vérification du remote GitHub..." -ForegroundColor Yellow
$remoteUrl = git remote get-url origin 2>$null

if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($remoteUrl)) {
    Write-Host ""
    Write-Host "📦 Aucun remote GitHub configuré." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Pour créer un dépôt GitHub et pousser le code:" -ForegroundColor Cyan
    Write-Host "1. Allez sur https://github.com/new" -ForegroundColor White
    Write-Host "2. Créez un nouveau dépôt (par exemple: irmsia)" -ForegroundColor White
    Write-Host "3. Ne cochez PAS 'Initialize with README'" -ForegroundColor White
    Write-Host "4. Exécutez ensuite:" -ForegroundColor White
    Write-Host ""
    Write-Host "   git remote add origin https://github.com/VOTRE_USERNAME/irmsia.git" -ForegroundColor Green
    Write-Host "   git branch -M main" -ForegroundColor Green
    Write-Host "   git push -u origin main" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ou si vous avez déjà créé le dépôt, entrez l'URL maintenant:" -ForegroundColor Yellow
    $newRemote = Read-Host "URL du dépôt GitHub (ou appuyez sur Entrée pour ignorer)"
    
    if (-not [string]::IsNullOrWhiteSpace($newRemote)) {
        git remote add origin $newRemote
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Remote ajouté avec succès" -ForegroundColor Green
            $remoteUrl = $newRemote
        } else {
            Write-Host "❌ Erreur lors de l'ajout du remote" -ForegroundColor Red
        }
    }
} else {
    Write-Host "✅ Remote trouvé: $remoteUrl" -ForegroundColor Green
}

# Proposer de pousser
if (-not [string]::IsNullOrWhiteSpace($remoteUrl)) {
    Write-Host ""
    $push = Read-Host "Voulez-vous pousser le code sur GitHub maintenant? (o/N)"
    if ($push -eq "o" -or $push -eq "O") {
        Write-Host ""
        Write-Host "🚀 Push vers GitHub..." -ForegroundColor Yellow
        
        # Vérifier la branche
        $currentBranch = git branch --show-current
        if ($currentBranch -ne "main" -and $currentBranch -ne "master") {
            Write-Host "⚠️  Vous n'êtes pas sur la branche main/master. Branche actuelle: $currentBranch" -ForegroundColor Yellow
            $rename = Read-Host "Voulez-vous renommer cette branche en 'main'? (o/N)"
            if ($rename -eq "o" -or $rename -eq "O") {
                git branch -M main
                $currentBranch = "main"
            }
        }
        
        # Push
        git push -u origin $currentBranch
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Déploiement réussi sur GitHub!" -ForegroundColor Green
            Write-Host "🔗 Votre dépôt: $remoteUrl" -ForegroundColor Cyan
        } else {
            Write-Host ""
            Write-Host "❌ Erreur lors du push. Vérifiez vos permissions GitHub." -ForegroundColor Red
            Write-Host "💡 Vous pouvez essayer manuellement: git push -u origin $currentBranch" -ForegroundColor Yellow
        }
    } else {
        Write-Host ""
        Write-Host "📝 Commit créé avec succès. Pour pousser plus tard:" -ForegroundColor Cyan
        Write-Host "   git push -u origin $(git branch --show-current)" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "✨ Terminé!" -ForegroundColor Green

