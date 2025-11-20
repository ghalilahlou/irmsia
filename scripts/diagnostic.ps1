# Script de diagnostic - IRMSIA Medical AI
# Identifie les problemes de demarrage

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DIAGNOSTIC IRMSIA" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$errors = @()
$warnings = @()

# 1. Verifier le fichier .env
Write-Host "[1/8] Verification du fichier .env..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  OK: Fichier .env trouve" -ForegroundColor Green
    
    $envContent = Get-Content .env
    $requiredVars = @("SECRET_KEY", "ENCRYPTION_KEY")
    foreach ($var in $requiredVars) {
        $found = $false
        foreach ($line in $envContent) {
            if ($line -match "^$var=") {
                $value = ($line -split "=", 2)[1].Trim()
                if ($value -and $value -ne "") {
                    Write-Host "  OK: $var est defini" -ForegroundColor Green
                    $found = $true
                    break
                }
            }
        }
        if (-not $found) {
            $errors += "Variable $var manquante ou vide dans .env"
            Write-Host "  ERREUR: $var manquant ou vide" -ForegroundColor Red
        }
    }
} else {
    $errors += "Fichier .env non trouve"
    Write-Host "  ERREUR: Fichier .env non trouve" -ForegroundColor Red
}

# 2. Verifier l'environnement virtuel
Write-Host ""
Write-Host "[2/8] Verification de l'environnement virtuel..." -ForegroundColor Yellow
if (Test-Path "backend\venv\Scripts\python.exe") {
    Write-Host "  OK: Environnement virtuel trouve" -ForegroundColor Green
} else {
    $errors += "Environnement virtuel non trouve"
    Write-Host "  ERREUR: Environnement virtuel non trouve" -ForegroundColor Red
    Write-Host "  Executez: .\scripts\setup.ps1" -ForegroundColor Yellow
}

# 3. Verifier les dependances Python
Write-Host ""
Write-Host "[3/8] Verification des dependances Python..." -ForegroundColor Yellow
if (Test-Path "backend\venv\Scripts\python.exe") {
    $python = "backend\venv\Scripts\python.exe"
    $requiredModules = @("fastapi", "uvicorn", "pydantic", "jose", "passlib", "cryptography")
    foreach ($module in $requiredModules) {
        $result = & $python -c "import $module" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  OK: $module installe" -ForegroundColor Green
        } else {
            $errors += "Module Python $module non installe"
            Write-Host "  ERREUR: $module non installe" -ForegroundColor Red
        }
    }
} else {
    $warnings += "Impossible de verifier les dependances (venv non trouve)"
}

# 4. Verifier les repertoires de stockage
Write-Host ""
Write-Host "[4/8] Verification des repertoires de stockage..." -ForegroundColor Yellow
$directories = @("storage\uploads", "storage\encrypted", "storage\png", "logs")
foreach ($dir in $directories) {
    if (Test-Path $dir) {
        Write-Host "  OK: $dir existe" -ForegroundColor Green
    } else {
        Write-Host "  ATTENTION: $dir n'existe pas (sera cree au demarrage)" -ForegroundColor Yellow
        $warnings += "Repertoire $dir manquant"
    }
}

# 5. Verifier les imports Python critiques
Write-Host ""
Write-Host "[5/8] Verification des imports Python..." -ForegroundColor Yellow
if (Test-Path "backend\venv\Scripts\python.exe") {
    $python = "backend\venv\Scripts\python.exe"
    
    # Test import config
    $result = & $python -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path('.').absolute())); from backend.core.config import settings" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK: Import de config reussi" -ForegroundColor Green
    } else {
        $errors += "Erreur d'import de config: $result"
        Write-Host "  ERREUR: Import de config echoue" -ForegroundColor Red
        Write-Host "  Details: $result" -ForegroundColor Gray
    }
    
    # Test import security
    $result = & $python -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path('.').absolute())); from backend.core.security import security_manager" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK: Import de security reussi" -ForegroundColor Green
    } else {
        $errors += "Erreur d'import de security: $result"
        Write-Host "  ERREUR: Import de security echoue" -ForegroundColor Red
        Write-Host "  Details: $result" -ForegroundColor Gray
    }
}

# 6. Verifier le frontend
Write-Host ""
Write-Host "[6/8] Verification du frontend..." -ForegroundColor Yellow
if (Test-Path "frontend-next") {
    Write-Host "  OK: Repertoire frontend-next trouve" -ForegroundColor Green
    
    if (Test-Path "frontend-next\.env.local") {
        Write-Host "  OK: Fichier .env.local trouve" -ForegroundColor Green
    } else {
        $warnings += "Fichier frontend-next/.env.local non trouve"
        Write-Host "  ATTENTION: .env.local non trouve" -ForegroundColor Yellow
    }
    
    if (Test-Path "frontend-next\node_modules") {
        Write-Host "  OK: node_modules trouve" -ForegroundColor Green
    } else {
        $warnings += "node_modules non trouve dans frontend-next"
        Write-Host "  ATTENTION: node_modules non trouve" -ForegroundColor Yellow
    }
} else {
    $warnings += "Repertoire frontend-next non trouve"
    Write-Host "  ATTENTION: Repertoire frontend-next non trouve" -ForegroundColor Yellow
}

# 7. Verifier les ports
Write-Host ""
Write-Host "[7/8] Verification des ports..." -ForegroundColor Yellow
$ports = @(8000, 3000)
foreach ($port in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        $warnings += "Port $port deja utilise"
        Write-Host "  ATTENTION: Port $port deja utilise" -ForegroundColor Yellow
    } else {
        Write-Host "  OK: Port $port disponible" -ForegroundColor Green
    }
}

# 8. Test de demarrage backend (dry-run)
Write-Host ""
Write-Host "[8/8] Test de demarrage backend (dry-run)..." -ForegroundColor Yellow
if (Test-Path "backend\venv\Scripts\python.exe") {
    $python = "backend\venv\Scripts\python.exe"
    $result = & $python -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path('.').absolute())); from backend.main import app; print('OK')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK: Application peut etre importee" -ForegroundColor Green
    } else {
        $errors += "Erreur lors de l'import de l'application: $result"
        Write-Host "  ERREUR: Import de l'application echoue" -ForegroundColor Red
        Write-Host "  Details: $result" -ForegroundColor Gray
    }
}

# Resume
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESUME" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($errors.Count -eq 0) {
    Write-Host "Aucune erreur critique trouvee!" -ForegroundColor Green
    if ($warnings.Count -gt 0) {
        Write-Host ""
        Write-Host "ATTENTIONS:" -ForegroundColor Yellow
        foreach ($warning in $warnings) {
            Write-Host "  - $warning" -ForegroundColor Yellow
        }
    }
    Write-Host ""
    Write-Host "L'application devrait pouvoir demarrer." -ForegroundColor Green
} else {
    Write-Host "ERREURS CRITIQUES TROUVEES:" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "  - $error" -ForegroundColor Red
    }
    Write-Host ""
    if ($warnings.Count -gt 0) {
        Write-Host "ATTENTIONS:" -ForegroundColor Yellow
        foreach ($warning in $warnings) {
            Write-Host "  - $warning" -ForegroundColor Yellow
        }
        Write-Host ""
    }
    Write-Host "Corrigez ces erreurs avant de demarrer l'application." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Pour demarrer l'application:" -ForegroundColor Cyan
Write-Host "  Backend:  .\scripts\start.ps1" -ForegroundColor White
Write-Host "  Frontend: cd frontend-next && npm run dev" -ForegroundColor White

