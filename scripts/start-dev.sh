#!/bin/bash

echo "🚀 Démarrage d'IRMSIA Medical AI - Environnement de développement"

# Vérifier si on est dans le bon répertoire
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Erreur: Veuillez exécuter ce script depuis la racine du projet"
    exit 1
fi

# Créer les dossiers nécessaires
echo "📁 Création des dossiers nécessaires..."
mkdir -p logs
mkdir -p data/uploads
mkdir -p data/models

# Démarrer les services Docker (PostgreSQL, Redis)
echo "🐳 Démarrage des services Docker..."
docker-compose up -d postgres redis

# Attendre que PostgreSQL soit prêt
echo "⏳ Attente que PostgreSQL soit prêt..."
sleep 10

# Activer l'environnement virtuel Python
echo "🐍 Activation de l'environnement virtuel Python..."
cd backend
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Linux/Mac

# Installer les dépendances backend si nécessaire
echo "📦 Vérification des dépendances backend..."
pip install -r requirements.txt

# Démarrer le backend
echo "🔧 Démarrage du backend FastAPI..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Retourner au répertoire racine
cd ..

# Installer les dépendances frontend si nécessaire
echo "📦 Vérification des dépendances frontend..."
cd frontend
npm install

# Démarrer le frontend
echo "🎨 Démarrage du frontend React..."
npm run dev &
FRONTEND_PID=$!

# Retourner au répertoire racine
cd ..

echo ""
echo "✅ IRMSIA Medical AI est maintenant en cours d'exécution !"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "🛑 Pour arrêter l'application, exécutez: ./scripts/stop-dev.sh"
echo ""

# Attendre que l'utilisateur appuie sur Ctrl+C
trap "echo '🛑 Arrêt des services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait 