#!/bin/bash

# 🧠 IRMSIA Medical AI - Script de Setup Développement
# ===================================================

set -e

echo "🚀 Démarrage du setup IRMSIA Medical AI..."

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérification des prérequis
check_prerequisites() {
    print_status "Vérification des prérequis..."
    
    # Vérifier Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3.9+ est requis"
        exit 1
    fi
    
    # Vérifier Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js 18+ est requis"
        exit 1
    fi
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        print_warning "Docker n'est pas installé. Installation des dépendances locales..."
        USE_DOCKER=false
    else
        USE_DOCKER=true
    fi
    
    # Vérifier Git
    if ! command -v git &> /dev/null; then
        print_error "Git est requis"
        exit 1
    fi
    
    print_success "Prérequis vérifiés"
}

# Création de la structure du projet
create_project_structure() {
    print_status "Création de la structure du projet..."
    
    # Dossiers principaux
    mkdir -p frontend/src/{components,pages,services,utils,styles,context}
    mkdir -p frontend/src/components/{viewer,ui,common}
    mkdir -p frontend/public
    
    mkdir -p backend/app/{api,core,models,services,schemas,utils}
    mkdir -p backend/app/api/v1
    mkdir -p backend/app/models/{brain_tumor,vascular,preprocessing}
    mkdir -p backend/app/services
    
    mkdir -p ml/{models,training,datasets,configs,scripts}
    mkdir -p ml/models/{brain_tumor,vascular,common}
    mkdir -p ml/datasets/{brats,tcia,custom}
    
    mkdir -p docs/{api,user_guide,developer,medical}
    mkdir -p scripts
    mkdir -p docker/{nginx,prometheus,grafana}
    mkdir -p tests/{frontend,backend,ml}
    
    # Dossiers de données
    mkdir -p data/{raw,processed,models}
    mkdir -p data/raw/{brats,tcia,custom}
    mkdir -p data/processed/{training,validation,test}
    mkdir -p data/models/{brain_tumor,vascular,checkpoints}
    
    # Dossiers de logs
    mkdir -p logs
    mkdir -p uploads
    mkdir -p models
    
    print_success "Structure du projet créée"
}

# Setup du backend Python
setup_backend() {
    print_status "Configuration du backend Python..."
    
    cd backend
    
    # Créer l'environnement virtuel
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Environnement virtuel créé"
    fi
    
    # Activer l'environnement virtuel
    source venv/bin/activate
    
    # Installer les dépendances
    if [ -f "requirements.txt" ]; then
        pip install --upgrade pip
        pip install -r requirements.txt
        print_success "Dépendances Python installées"
    else
        print_warning "requirements.txt non trouvé"
    fi
    
    # Créer le fichier .env
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# Configuration IRMSIA Medical AI
DEBUG=true
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=postgresql://irmsia:password@localhost:5432/irmsia
REDIS_URL=redis://localhost:6379
ALLOWED_HOSTS=http://localhost:3000,http://localhost:3001
UPLOAD_DIR=./uploads
MODELS_DIR=./models
LOG_LEVEL=INFO
GPU_ENABLED=true
EOF
        print_success "Fichier .env créé"
    fi
    
    cd ..
}

# Setup du frontend React
setup_frontend() {
    print_status "Configuration du frontend React..."
    
    cd frontend
    
    # Installer les dépendances
    if [ -f "package.json" ]; then
        npm install
        print_success "Dépendances Node.js installées"
    else
        print_warning "package.json non trouvé"
    fi
    
    # Créer le fichier .env
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# Configuration Frontend IRMSIA
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
REACT_APP_ENVIRONMENT=development
EOF
        print_success "Fichier .env créé"
    fi
    
    cd ..
}

# Setup de la base de données
setup_database() {
    print_status "Configuration de la base de données..."
    
    if [ "$USE_DOCKER" = true ]; then
        # Démarrer PostgreSQL avec Docker
        docker run -d \
            --name irmsia-postgres \
            -e POSTGRES_DB=irmsia \
            -e POSTGRES_USER=irmsia \
            -e POSTGRES_PASSWORD=password \
            -p 5432:5432 \
            postgres:15-alpine
        
        # Démarrer Redis avec Docker
        docker run -d \
            --name irmsia-redis \
            -p 6379:6379 \
            redis:7-alpine
        
        print_success "Base de données démarrée avec Docker"
    else
        print_warning "Docker non disponible. Veuillez installer PostgreSQL et Redis manuellement."
    fi
}

# Téléchargement des modèles IA
download_models() {
    print_status "Téléchargement des modèles IA..."
    
    # Créer le dossier des modèles
    mkdir -p models/{brain_tumor,vascular}
    
    # Télécharger les modèles pré-entraînés (exemple)
    # curl -L -o models/brain_tumor/unet_3d.pth https://example.com/models/unet_3d.pth
    # curl -L -o models/vascular/stroke_detector.pth https://example.com/models/stroke_detector.pth
    
    print_success "Modèles IA configurés"
}

# Configuration des scripts de développement
setup_dev_scripts() {
    print_status "Configuration des scripts de développement..."
    
    # Script de démarrage rapide
    cat > start-dev.sh << 'EOF'
#!/bin/bash

echo "🚀 Démarrage d'IRMSIA Medical AI en mode développement..."

# Démarrer le backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Démarrer le frontend
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Services démarrés:"
echo "   - Backend: http://localhost:8000"
echo "   - Frontend: http://localhost:3000"
echo "   - API Docs: http://localhost:8000/docs"

# Attendre l'interruption
trap "echo '🛑 Arrêt des services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF
    
    chmod +x start-dev.sh
    
    # Script de test
    cat > test-all.sh << 'EOF'
#!/bin/bash

echo "🧪 Lancement des tests..."

# Tests backend
cd backend
source venv/bin/activate
pytest tests/ -v

# Tests frontend
cd ../frontend
npm test

echo "✅ Tests terminés"
EOF
    
    chmod +x test-all.sh
    
    print_success "Scripts de développement créés"
}

# Configuration de Git
setup_git() {
    print_status "Configuration de Git..."
    
    # Créer .gitignore
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# React
build/
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Data
data/
uploads/
models/

# Environment
.env
.env.local

# Docker
.dockerignore

# Testing
.coverage
htmlcov/
.pytest_cache/

# Documentation
docs/_build/
EOF
    
    print_success "Configuration Git terminée"
}

# Affichage des informations finales
show_final_info() {
    echo ""
    echo "🎉 Setup IRMSIA Medical AI terminé !"
    echo "====================================="
    echo ""
    echo "📁 Structure créée:"
    echo "   - Frontend React: ./frontend/"
    echo "   - Backend FastAPI: ./backend/"
    echo "   - Modèles IA: ./ml/"
    echo "   - Documentation: ./docs/"
    echo ""
    echo "🚀 Pour démarrer le développement:"
    echo "   ./start-dev.sh"
    echo ""
    echo "🧪 Pour lancer les tests:"
    echo "   ./test-all.sh"
    echo ""
    echo "🐳 Pour utiliser Docker:"
    echo "   docker-compose up -d"
    echo ""
    echo "📚 Documentation:"
    echo "   - API: http://localhost:8000/docs"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Grafana: http://localhost:3001"
    echo ""
    echo "🔧 Prochaines étapes:"
    echo "   1. Configurer les modèles IA"
    echo "   2. Ajouter les données de test"
    echo "   3. Personnaliser l'interface"
    echo "   4. Configurer la sécurité"
    echo ""
}

# Fonction principale
main() {
    echo "🧠 IRMSIA Medical AI - Setup Développement"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    create_project_structure
    setup_backend
    setup_frontend
    setup_database
    download_models
    setup_dev_scripts
    setup_git
    show_final_info
}

# Exécution du script
main "$@" 