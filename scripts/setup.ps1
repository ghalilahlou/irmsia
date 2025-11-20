# Script de configuration et demarrage - IRMSIA Medical AI
# PowerShell

Write-Host "Configuration IRMSIA Medical AI" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Verifier Python
Write-Host "Verification de Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "OK: Python trouve - $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERREUR: Python n'est pas installe ou pas dans le PATH" -ForegroundColor Red
    exit 1
}

# Verifier/Creer le fichier .env
Write-Host ""
Write-Host "Configuration du fichier .env..." -ForegroundColor Yellow
if (-not (Test-Path .env)) {
    if (Test-Path env.example) {
        Copy-Item env.example .env
        Write-Host "OK: Fichier .env cree depuis env.example" -ForegroundColor Green
    } else {
        Write-Host "ERREUR: Fichier env.example non trouve" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "OK: Fichier .env existe deja" -ForegroundColor Green
}

# Generer les cles de securite si necessaire
Write-Host ""
Write-Host "Generation des cles de securite..." -ForegroundColor Yellow
$envContent = Get-Content .env -Raw

if ($envContent -match "SECRET_KEY=change-this" -or $envContent -match "ENCRYPTION_KEY=change-this") {
    Write-Host "Generation de nouvelles cles..." -ForegroundColor Yellow
    
    $secretKey = python -c "import secrets; print(secrets.token_urlsafe(32))"
    $encryptionKey = python -c "import secrets; print(secrets.token_hex(32))"
    
    $envContent = $envContent -replace "SECRET_KEY=.*", "SECRET_KEY=$secretKey"
    $envContent = $envContent -replace "ENCRYPTION_KEY=.*", "ENCRYPTION_KEY=$encryptionKey"
    
    Set-Content -Path .env -Value $envContent -NoNewline
    Write-Host "OK: Cles de securite generees et ajoutees" -ForegroundColor Green
} else {
    Write-Host "OK: Cles de securite deja configurees" -ForegroundColor Green
}

# Creer les repertoires necessaires
Write-Host ""
Write-Host "Creation des repertoires..." -ForegroundColor Yellow
$directories = @(
    "storage\uploads",
    "storage\encrypted",
    "storage\png",
    "storage\png\temp",
    "logs"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        Write-Host "OK: Cree - $dir" -ForegroundColor Green
    } else {
        Write-Host "OK: Existe - $dir" -ForegroundColor Gray
    }
}

# Verifier l'environnement virtuel
Write-Host ""
Write-Host "Verification de l'environnement virtuel..." -ForegroundColor Yellow
if (-not (Test-Path backend\venv)) {
    Write-Host "Creation de l'environnement virtuel..." -ForegroundColor Yellow
    python -m venv backend\venv
    Write-Host "OK: Environnement virtuel cree" -ForegroundColor Green
} else {
    Write-Host "OK: Environnement virtuel existe deja" -ForegroundColor Green
}

# Activer l'environnement virtuel et installer les dependances
Write-Host ""
Write-Host "Installation des dependances..." -ForegroundColor Yellow
$venvPython = "backend\venv\Scripts\python.exe"
$venvPip = "backend\venv\Scripts\pip.exe"

if (Test-Path $venvPython) {
    & $venvPip install --upgrade pip | Out-Null
    Write-Host "Installation des packages..." -ForegroundColor Yellow
    & $venvPip install -r backend\requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK: Dependances installees avec succes" -ForegroundColor Green
    } else {
        Write-Host "ERREUR: Erreur lors de l'installation des dependances" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "ATTENTION: Environnement virtuel non trouve, installation globale..." -ForegroundColor Yellow
    pip install --upgrade pip | Out-Null
    pip install -r backend\requirements.txt
}

# Resume
Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "OK: Configuration terminee !" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Prochaines etapes:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Lancer l'application:" -ForegroundColor White
Write-Host "   .\scripts\start.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "   OU avec Docker:" -ForegroundColor White
Write-Host "   .\scripts\start-docker.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Acceder a l'API:" -ForegroundColor White
Write-Host "   http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Comptes de test:" -ForegroundColor White
Write-Host "   Admin: admin / admin123" -ForegroundColor Gray
Write-Host "   Radiologist: radiologist / radio123" -ForegroundColor Gray
Write-Host ""

