# Script de deploiement force - Remplace completement le depot GitHub
# ATTENTION: Cette operation est DESTRUCTIVE et remplace tout l'historique Git

param(
    [string]$CommitMessage = "Complete repository replacement with new Docker deployment",
    [switch]$SkipConfirmation
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Red
Write-Host "  DEPLOIEMENT FORCE GITHUB" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""
Write-Host "ATTENTION: Cette operation va:" -ForegroundColor Yellow
Write-Host "   1. Supprimer TOUT l'historique Git sur GitHub" -ForegroundColor Yellow
Write-Host "   2. Remplacer par votre version locale actuelle" -ForegroundColor Yellow
Write-Host "   3. Cette action est IRREVERSIBLE" -ForegroundColor Yellow
Write-Host ""

# Verifier que Git est installe
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "ERREUR: Git n'est pas installe!" -ForegroundColor Red
    exit 1
}

# Verifier que nous sommes dans un depot Git
if (-not (Test-Path ".git")) {
    Write-Host "ERREUR: Ce repertoire n'est pas un depot Git!" -ForegroundColor Red
    exit 1
}

# Verifier le remote
$remote = git remote get-url origin 2>$null
if (-not $remote) {
    Write-Host "ERREUR: Aucun remote 'origin' configure!" -ForegroundColor Red
    Write-Host "   Configurez d'abord: git remote add origin <url>" -ForegroundColor Yellow
    exit 1
}

Write-Host "Remote configure: $remote" -ForegroundColor Cyan
Write-Host ""

# Verifier les fichiers sensibles
Write-Host "Verification des fichiers sensibles..." -ForegroundColor Cyan
$sensitiveFiles = @(".env", "*.db", "backend/.env", "backend/medical_audit.db")
$foundSensitive = $false

foreach ($pattern in $sensitiveFiles) {
    $files = Get-ChildItem -Path . -Filter $pattern -Recurse -ErrorAction SilentlyContinue | Where-Object { -not $_.FullName.Contains("node_modules") -and -not $_.FullName.Contains("venv") }
    if ($files) {
        Write-Host "   Fichier sensible trouve: $($files[0].FullName)" -ForegroundColor Yellow
        $foundSensitive = $true
    }
}

if ($foundSensitive) {
    Write-Host ""
    Write-Host "Des fichiers sensibles ont ete detectes!" -ForegroundColor Yellow
    Write-Host "   Assurez-vous qu'ils sont dans .gitignore" -ForegroundColor Yellow
    Write-Host ""
}

# Confirmation
if (-not $SkipConfirmation) {
    Write-Host "Voulez-vous vraiment continuer? (O/N): " -ForegroundColor Yellow -NoNewline
    $response = Read-Host
    if ($response -ne "O" -and $response -ne "o" -and $response -ne "Y" -and $response -ne "y") {
        Write-Host "Operation annulee." -ForegroundColor Red
        exit 0
    }
    Write-Host ""
}

# Etape 1: Verifier l'etat actuel
Write-Host "Etape 1: Verification de l'etat Git..." -ForegroundColor Cyan
git status --short | Select-Object -First 20
Write-Host ""

# Etape 2: Ajouter tous les fichiers
Write-Host "Etape 2: Ajout de tous les fichiers..." -ForegroundColor Cyan
git add -A

$status = git status --short
if ($status) {
    Write-Host "Fichiers a commiter:" -ForegroundColor Green
    git status --short | Select-Object -First 30
    Write-Host ""
} else {
    Write-Host "Aucun changement a commiter!" -ForegroundColor Yellow
    Write-Host "   Voulez-vous quand meme forcer le push? (O/N): " -NoNewline
    $response = Read-Host
    if ($response -ne "O" -and $response -ne "o" -and $response -ne "Y" -and $response -ne "y") {
        exit 0
    }
}

# Etape 3: Creer un commit
Write-Host "Etape 3: Creation du commit..." -ForegroundColor Cyan
git commit -m $CommitMessage

if ($LASTEXITCODE -ne 0) {
    Write-Host "Aucun changement a commiter (peut-etre deja commite)" -ForegroundColor Yellow
}

# Etape 4: Verifier la branche
Write-Host "Etape 4: Verification de la branche..." -ForegroundColor Cyan
$currentBranch = git branch --show-current
Write-Host "   Branche actuelle: $currentBranch" -ForegroundColor White

if ($currentBranch -ne "main" -and $currentBranch -ne "master") {
    Write-Host "Vous n'etes pas sur la branche main/master" -ForegroundColor Yellow
    Write-Host "   Voulez-vous continuer quand meme? (O/N): " -NoNewline
    $response = Read-Host
    if ($response -ne "O" -and $response -ne "o" -and $response -ne "Y" -and $response -ne "y") {
        exit 0
    }
}

# Etape 5: Force push
Write-Host ""
Write-Host "Etape 5: Force push vers GitHub..." -ForegroundColor Cyan
Write-Host "   Cette operation va remplacer TOUT sur GitHub!" -ForegroundColor Yellow
Write-Host ""

if (-not $SkipConfirmation) {
    Write-Host "Derniere confirmation - Continuer? (O/N): " -ForegroundColor Red -NoNewline
    $response = Read-Host
    if ($response -ne "O" -and $response -ne "o" -and $response -ne "Y" -and $response -ne "y") {
        Write-Host "Operation annulee." -ForegroundColor Red
        exit 0
    }
}

# Force push avec --force pour remplacer completement
Write-Host "   Envoi vers GitHub..." -ForegroundColor White
git push origin $currentBranch --force

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Deploiement reussi!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Resume:" -ForegroundColor Cyan
    Write-Host "   - Remote: $remote" -ForegroundColor White
    Write-Host "   - Branche: $currentBranch" -ForegroundColor White
    Write-Host "   - Commit: $CommitMessage" -ForegroundColor White
    Write-Host ""
    Write-Host "Verifiez votre depot: $remote" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "Erreur lors du push!" -ForegroundColor Red
    Write-Host "   Verifiez:" -ForegroundColor Yellow
    Write-Host "   1. Vos credentials GitHub" -ForegroundColor Yellow
    Write-Host "   2. Vos permissions sur le depot" -ForegroundColor Yellow
    Write-Host "   3. La connexion Internet" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Deploiement termine!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
