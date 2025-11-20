#!/bin/bash

echo "🛑 Arrêt d'IRMSIA Medical AI - Environnement de développement"

# Arrêter les processus en cours
echo "🔧 Arrêt du backend..."
pkill -f "uvicorn app.main:app" || true

echo "🎨 Arrêt du frontend..."
pkill -f "npm run dev" || true

# Arrêter les services Docker
echo "🐳 Arrêt des services Docker..."
docker-compose down

echo "✅ IRMSIA Medical AI a été arrêté avec succès !" 