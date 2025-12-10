# Script de configuration du serveur gRPC

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  CONFIGURATION SERVEUR gRPC" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Vérifier qu'on est dans le bon répertoire
if (-Not (Test-Path "server\diagnostic_server.py")) {
    Write-Host "ERREUR: Executez ce script depuis grpc-deeplearning\" -ForegroundColor Red
    exit 1
}

# Étape 1: Générer les fichiers proto
Write-Host "[1/3] Generation des fichiers proto..." -ForegroundColor Yellow
if (-Not (Test-Path "proto\irmsia_dicom.proto")) {
    Write-Host "ERREUR: proto\irmsia_dicom.proto introuvable!" -ForegroundColor Red
    exit 1
}

try {
    python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/irmsia_dicom.proto
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   Fichiers proto generes: OK" -ForegroundColor Green
    } else {
        Write-Host "   ERREUR lors de la generation des fichiers proto" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "   ERREUR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Étape 2: Installer les dépendances essentielles
Write-Host ""
Write-Host "[2/3] Installation des dependances essentielles..." -ForegroundColor Yellow

$packages = @(
    "timm==0.9.12",
    "efficientnet-pytorch==0.7.1",
    "pydicom==2.4.4",
    "SimpleITK==2.3.1",
    "nibabel==5.2.0",
    "opencv-python==4.8.1.78",
    "Pillow==10.1.0",
    "scikit-image==0.22.0",
    "numpy==1.26.2",
    "scipy==1.11.4",
    "tqdm==4.66.1",
    "pyyaml==6.0.1",
    "colorlog==6.8.0"
)

foreach ($package in $packages) {
    Write-Host "   Installation: $package" -ForegroundColor Gray
    try {
        python -m pip install $package --quiet
        if ($LASTEXITCODE -ne 0) {
            Write-Host "   ATTENTION: Echec installation $package" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ERREUR: Impossible d'installer $package" -ForegroundColor Red
    }
}

Write-Host "   Dependances installees" -ForegroundColor Green

# Étape 3: Vérification
Write-Host ""
Write-Host "[3/3] Verification..." -ForegroundColor Yellow

$checks = @(
    @{Name="Proto files"; Test={Test-Path "proto\irmsia_dicom_pb2.py"}},
    @{Name="timm"; Test={python -c "import timm; print('OK')" 2>&1 | Out-Null; $LASTEXITCODE -eq 0}},
    @{Name="torch"; Test={python -c "import torch; print('OK')" 2>&1 | Out-Null; $LASTEXITCODE -eq 0}},
    @{Name="pydicom"; Test={python -c "import pydicom; print('OK')" 2>&1 | Out-Null; $LASTEXITCODE -eq 0}}
)

$allOk = $true
foreach ($check in $checks) {
    try {
        $result = & $check.Test
        if ($result) {
            Write-Host "   $($check.Name): OK" -ForegroundColor Green
        } else {
            Write-Host "   $($check.Name): MANQUANT" -ForegroundColor Red
            $allOk = $false
        }
    } catch {
        Write-Host "   $($check.Name): ERREUR" -ForegroundColor Red
        $allOk = $false
    }
}

Write-Host ""
if ($allOk) {
    Write-Host "=============================================" -ForegroundColor Green
    Write-Host "  CONFIGURATION TERMINEE" -ForegroundColor Green
    Write-Host "=============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Vous pouvez maintenant demarrer le serveur gRPC:" -ForegroundColor Yellow
    Write-Host "   python server\diagnostic_server.py" -ForegroundColor Cyan
} else {
    Write-Host "=============================================" -ForegroundColor Red
    Write-Host "  CONFIGURATION INCOMPLETE" -ForegroundColor Red
    Write-Host "=============================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Certaines dependances sont manquantes." -ForegroundColor Yellow
    Write-Host "Installez-les manuellement avec:" -ForegroundColor Yellow
    Write-Host "   python -m pip install -r requirements.txt" -ForegroundColor Cyan
    exit 1
}

Write-Host ""

