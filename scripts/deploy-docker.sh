#!/bin/bash
# Script de déploiement Docker pour IRMSIA (Linux/Mac)
# Ce script construit et démarre tous les services avec Docker Compose

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  IRMSIA - Déploiement Docker${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas installé!${NC}"
    echo -e "${YELLOW}   Installez Docker depuis: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

# Vérifier que Docker Compose est disponible
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose n'est pas disponible!${NC}"
    exit 1
fi

# Vérifier que Docker est en cours d'exécution
if ! docker ps &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas en cours d'exécution!${NC}"
    echo -e "${YELLOW}   Démarrez Docker et réessayez.${NC}"
    exit 1
fi

# Vérifier les fichiers d'environnement
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Fichier .env non trouvé!${NC}"
    echo -e "${YELLOW}   Création d'un fichier .env à partir de env.example...${NC}"
    
    if [ -f "env.example" ]; then
        cp env.example .env
        echo -e "${GREEN}✅ Fichier .env créé. Veuillez le modifier avec vos valeurs!${NC}"
    else
        echo -e "${RED}❌ env.example non trouvé!${NC}"
        exit 1
    fi
fi

# Fonction pour construire les images
build_images() {
    echo -e "${CYAN}🔨 Construction des images Docker...${NC}"
    echo ""
    
    docker-compose build --no-cache
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Images construites avec succès!${NC}"
    else
        echo ""
        echo -e "${RED}❌ Erreur lors de la construction des images!${NC}"
        exit 1
    fi
}

# Fonction pour démarrer les services
start_services() {
    echo -e "${CYAN}🚀 Démarrage des services Docker...${NC}"
    echo ""
    
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Services démarrés avec succès!${NC}"
        echo ""
        echo -e "${CYAN}📊 Statut des services:${NC}"
        docker-compose ps
        echo ""
        echo -e "${CYAN}🌐 URLs:${NC}"
        echo -e "   Frontend:  http://localhost:3000"
        echo -e "   Backend:   http://localhost:8000"
        echo -e "   API Docs:  http://localhost:8000/docs"
        echo -e "   gRPC:      localhost:50051"
        echo ""
        echo -e "${YELLOW}📝 Pour voir les logs: ./scripts/deploy-docker.sh --logs${NC}"
    else
        echo ""
        echo -e "${RED}❌ Erreur lors du démarrage des services!${NC}"
        exit 1
    fi
}

# Fonction pour arrêter les services
stop_services() {
    echo -e "${CYAN}🛑 Arrêt des services Docker...${NC}"
    echo ""
    
    docker-compose down
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Services arrêtés avec succès!${NC}"
    else
        echo ""
        echo -e "${RED}❌ Erreur lors de l'arrêt des services!${NC}"
        exit 1
    fi
}

# Fonction pour afficher les logs
show_logs() {
    if [ -n "$1" ]; then
        echo -e "${CYAN}📋 Logs du service: $1${NC}"
        docker-compose logs -f "$1"
    else
        echo -e "${CYAN}📋 Logs de tous les services${NC}"
        docker-compose logs -f
    fi
}

# Fonction pour redémarrer les services
restart_services() {
    echo -e "${CYAN}🔄 Redémarrage des services Docker...${NC}"
    echo ""
    
    docker-compose restart
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Services redémarrés avec succès!${NC}"
    else
        echo ""
        echo -e "${RED}❌ Erreur lors du redémarrage des services!${NC}"
        exit 1
    fi
}

# Gestion des arguments
case "${1:-}" in
    --build)
        build_images
        ;;
    --up)
        start_services
        ;;
    --build-up)
        build_images
        start_services
        ;;
    --down)
        stop_services
        ;;
    --logs)
        show_logs "$2"
        ;;
    --restart)
        restart_services
        ;;
    *)
        # Mode interactif par défaut
        echo -e "${CYAN}Que souhaitez-vous faire?${NC}"
        echo "1. Construire les images"
        echo "2. Démarrer les services"
        echo "3. Construire et démarrer"
        echo "4. Arrêter les services"
        echo "5. Voir les logs"
        echo "6. Redémarrer les services"
        echo ""
        read -p "Votre choix (1-6): " choice
        
        case "$choice" in
            1) build_images ;;
            2) start_services ;;
            3) build_images; start_services ;;
            4) stop_services ;;
            5) show_logs ;;
            6) restart_services ;;
            *)
                echo -e "${RED}❌ Choix invalide!${NC}"
                exit 1
                ;;
        esac
        ;;
esac

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Déploiement terminé!${NC}"
echo -e "${CYAN}========================================${NC}"

