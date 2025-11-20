#!/bin/bash
# Script de démarrage - Frontend Next.js
# Linux/Mac

echo "🚀 Démarrage Frontend IRMSIA"
echo "================================"
echo ""

# Vérifier que .env.local existe
if [ ! -f ".env.local" ]; then
    echo "⚠️  ATTENTION: Fichier .env.local non trouvé"
    if [ -f "env.example" ]; then
        echo "📝 Création de .env.local depuis env.example..."
        cp env.example .env.local
        echo "✅ OK: .env.local créé"
    else
        echo "❌ ERREUR: Fichier env.example non trouvé"
        exit 1
    fi
fi

# Vérifier que node_modules existe
if [ ! -d "node_modules" ]; then
    echo "📦 Installation des dépendances..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ ERREUR: Installation des dépendances échouée"
        exit 1
    fi
    echo "✅ OK: Dépendances installées"
fi

# Lancer le serveur de développement
echo ""
echo "🚀 Démarrage du serveur de développement..."
echo "Frontend disponible sur: http://localhost:3000"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter"
echo ""

npm run dev

