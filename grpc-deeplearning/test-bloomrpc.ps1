# Script de test avec BloomRPC

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  TEST AVEC BLOOMRPC" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que le serveur est démarré
Write-Host "[1/3] Verification du serveur gRPC..." -ForegroundColor Yellow
$connection = Get-NetTCPConnection -LocalPort 50051 -ErrorAction SilentlyContinue
if ($connection) {
    Write-Host "   Serveur gRPC: ACTIF sur le port 50051" -ForegroundColor Green
} else {
    Write-Host "   ATTENTION: Serveur gRPC non detecte sur le port 50051" -ForegroundColor Red
    Write-Host ""
    Write-Host "Demarrez le serveur avec:" -ForegroundColor Yellow
    Write-Host "   cd grpc-deeplearning" -ForegroundColor Gray
    Write-Host "   python server\diagnostic_server.py" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

# Vérifier que le fichier proto existe
Write-Host ""
Write-Host "[2/3] Verification du fichier proto..." -ForegroundColor Yellow
$protoPath = "proto\irmsia_dicom.proto"
if (Test-Path $protoPath) {
    Write-Host "   Fichier proto: OK" -ForegroundColor Green
    Write-Host "   Chemin: $((Resolve-Path $protoPath).Path)" -ForegroundColor Gray
} else {
    Write-Host "   ERREUR: Fichier proto introuvable!" -ForegroundColor Red
    Write-Host "   Recherche dans: $((Get-Location).Path)" -ForegroundColor Gray
    exit 1
}

# Instructions BloomRPC
Write-Host ""
Write-Host "[3/3] Instructions BloomRPC:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Ouvrez BloomRPC" -ForegroundColor Cyan
Write-Host "2. Cliquez sur 'Import Proto' ou '+'" -ForegroundColor Cyan
Write-Host "3. Selectionnez le fichier:" -ForegroundColor Cyan
Write-Host "   $((Resolve-Path $protoPath).Path)" -ForegroundColor White
Write-Host ""
Write-Host "4. Configurez la connexion:" -ForegroundColor Cyan
Write-Host "   Host: localhost" -ForegroundColor White
Write-Host "   Port: 50051" -ForegroundColor White
Write-Host ""
Write-Host "5. Testez les methodes suivantes:" -ForegroundColor Cyan
Write-Host "   - HealthCheck (requete vide: {})" -ForegroundColor White
Write-Host "   - GetAvailableModels (requete vide: {})" -ForegroundColor White
Write-Host "   - DiagnoseDicom (requete avec donnees DICOM)" -ForegroundColor White
Write-Host ""

Write-Host "=============================================" -ForegroundColor Green
Write-Host "  PRET POUR BLOOMRPC" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

