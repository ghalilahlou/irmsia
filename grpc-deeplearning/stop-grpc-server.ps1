# Script pour arrêter le serveur gRPC

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  ARRET SERVEUR gRPC" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

$port = 50051
$connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue

if ($connections) {
    Write-Host "[1/2] Arret des processus sur le port $port..." -ForegroundColor Yellow
    
    $processes = $connections | ForEach-Object { Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue } | Select-Object -Unique
    
    foreach ($proc in $processes) {
        Write-Host "   Arret du processus: $($proc.ProcessName) (PID: $($proc.Id))" -ForegroundColor Gray
        try {
            Stop-Process -Id $proc.Id -Force
            Write-Host "   Processus arrete: OK" -ForegroundColor Green
        } catch {
            Write-Host "   ERREUR: Impossible d'arreter le processus" -ForegroundColor Red
        }
    }
    
    Start-Sleep -Seconds 2
    
    # Verifier
    $remaining = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($remaining) {
        Write-Host "   ATTENTION: Le port est toujours utilise" -ForegroundColor Yellow
    } else {
        Write-Host "   Port $port libere: OK" -ForegroundColor Green
    }
} else {
    Write-Host "[1/2] Aucun processus sur le port $port" -ForegroundColor Green
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "  ARRET TERMINE" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""


