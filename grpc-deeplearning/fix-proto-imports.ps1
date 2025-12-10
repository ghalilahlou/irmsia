# Script pour corriger les imports dans les fichiers proto générés

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  CORRECTION IMPORTS PROTO" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Vérifier qu'on est dans le bon répertoire
if (-Not (Test-Path "proto\irmsia_dicom.proto")) {
    Write-Host "ERREUR: Executez ce script depuis grpc-deeplearning\" -ForegroundColor Red
    exit 1
}

Write-Host "[1/3] Generation des fichiers proto..." -ForegroundColor Yellow
try {
    python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/irmsia_dicom.proto
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   Fichiers proto generes: OK" -ForegroundColor Green
    } else {
        Write-Host "   ERREUR lors de la generation" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "   ERREUR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/3] Correction des imports..." -ForegroundColor Yellow

$grpcFile = "proto\irmsia_dicom_pb2_grpc.py"
if (Test-Path $grpcFile) {
    $content = Get-Content $grpcFile -Raw
    if ($content -match "import irmsia_dicom_pb2 as irmsia__dicom__pb2") {
        $content = $content -replace "import irmsia_dicom_pb2 as irmsia__dicom__pb2", "from proto import irmsia_dicom_pb2 as irmsia__dicom__pb2"
        Set-Content -Path $grpcFile -Value $content -NoNewline
        Write-Host "   Import corrige dans irmsia_dicom_pb2_grpc.py: OK" -ForegroundColor Green
    } else {
        Write-Host "   Import deja correct ou format different" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ERREUR: Fichier $grpcFile introuvable" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[3/3] Verification..." -ForegroundColor Yellow

try {
    $test = python -c "from proto import irmsia_dicom_pb2_grpc; print('OK')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   Import fonctionne: OK" -ForegroundColor Green
        
        $hasMethod = python -c "from proto import irmsia_dicom_pb2_grpc; print(hasattr(irmsia_dicom_pb2_grpc, 'add_DicomDiagnosticServiceServicer_to_server'))" 2>&1
        if ($hasMethod -match "True") {
            Write-Host "   Methode add_DicomDiagnosticServiceServicer_to_server: OK" -ForegroundColor Green
        } else {
            Write-Host "   ATTENTION: Methode non trouvee" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ERREUR: Import echoue" -ForegroundColor Red
        Write-Host "   Details: $test" -ForegroundColor Gray
        exit 1
    }
} catch {
    Write-Host "   ERREUR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "  CORRECTION TERMINEE" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Vous pouvez maintenant demarrer le serveur gRPC:" -ForegroundColor Yellow
Write-Host "   python server\diagnostic_server.py" -ForegroundColor Cyan
Write-Host ""

