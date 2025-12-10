#!/bin/bash
# Script de déploiement force - Remplace complètement le dépôt GitHub (Linux/Mac)
# ⚠️ ATTENTION: Cette opération est DESTRUCTIVE et remplace tout l'historique Git

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

COMMIT_MESSAGE="${1:-Complete repository replacement with new Docker deployment}"
SKIP_CONFIRMATION="${2:-false}"

echo -e "${RED}========================================${NC}"
echo -e "${RED}  ⚠️  DÉPLOIEMENT FORCE GITHUB${NC}"
echo -e "${RED}========================================${NC}"
echo ""
echo -e "${YELLOW}⚠️  ATTENTION: Cette opération va:${NC}"
echo -e "${YELLOW}   1. Supprimer TOUT l'historique Git sur GitHub${NC}"
echo -e "${YELLOW}   2. Remplacer par votre version locale actuelle${NC}"
echo -e "${YELLOW}   3. Cette action est IRRÉVERSIBLE${NC}"
echo ""

# Vérifier que Git est installé
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git n'est pas installé!${NC}"
    exit 1
fi

# Vérifier que nous sommes dans un dépôt Git
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Ce répertoire n'est pas un dépôt Git!${NC}"
    exit 1
fi

# Vérifier le remote
REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
if [ -z "$REMOTE" ]; then
    echo -e "${RED}❌ Aucun remote 'origin' configuré!${NC}"
    echo -e "${YELLOW}   Configurez d'abord: git remote add origin <url>${NC}"
    exit 1
fi

echo -e "${CYAN}📋 Remote configuré: $REMOTE${NC}"
echo ""

# Confirmation
if [ "$SKIP_CONFIRMATION" != "true" ]; then
    echo -e "${YELLOW}❓ Voulez-vous vraiment continuer? (O/N): ${NC}\c"
    read -r response
    if [ "$response" != "O" ] && [ "$response" != "o" ] && [ "$response" != "Y" ] && [ "$response" != "y" ]; then
        echo -e "${RED}❌ Opération annulée.${NC}"
        exit 0
    fi
    echo ""
fi

# Étape 1: Vérifier l'état actuel
echo -e "${CYAN}📊 Étape 1: Vérification de l'état Git...${NC}"
git status --short | head -20
echo ""

# Étape 2: Ajouter tous les fichiers
echo -e "${CYAN}📦 Étape 2: Ajout de tous les fichiers...${NC}"
git add -A

STATUS=$(git status --short)
if [ -n "$STATUS" ]; then
    echo -e "${GREEN}✅ Fichiers à commiter:${NC}"
    git status --short | head -30
    echo ""
else
    echo -e "${YELLOW}⚠️  Aucun changement à commiter!${NC}"
    echo -e "${YELLOW}   Voulez-vous quand même forcer le push? (O/N): ${NC}\c"
    read -r response
    if [ "$response" != "O" ] && [ "$response" != "o" ] && [ "$response" != "Y" ] && [ "$response" != "y" ]; then
        exit 0
    fi
fi

# Étape 3: Créer un commit
echo -e "${CYAN}💾 Étape 3: Création du commit...${NC}"
git commit -m "$COMMIT_MESSAGE" || echo -e "${YELLOW}⚠️  Aucun changement à commiter (peut-être déjà commité)${NC}"

# Étape 4: Vérifier la branche
echo -e "${CYAN}🌿 Étape 4: Vérification de la branche...${NC}"
CURRENT_BRANCH=$(git branch --show-current)
echo -e "   Branche actuelle: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    echo -e "${YELLOW}⚠️  Vous n'êtes pas sur la branche main/master${NC}"
    echo -e "${YELLOW}   Voulez-vous continuer quand même? (O/N): ${NC}\c"
    read -r response
    if [ "$response" != "O" ] && [ "$response" != "o" ] && [ "$response" != "Y" ] && [ "$response" != "y" ]; then
        exit 0
    fi
fi

# Étape 5: Force push
echo ""
echo -e "${CYAN}🚀 Étape 5: Force push vers GitHub...${NC}"
echo -e "${YELLOW}   ⚠️  Cette opération va remplacer TOUT sur GitHub!${NC}"
echo ""

if [ "$SKIP_CONFIRMATION" != "true" ]; then
    echo -e "${RED}❓ Dernière confirmation - Continuer? (O/N): ${NC}\c"
    read -r response
    if [ "$response" != "O" ] && [ "$response" != "o" ] && [ "$response" != "Y" ] && [ "$response" != "y" ]; then
        echo -e "${RED}❌ Opération annulée.${NC}"
        exit 0
    fi
fi

# Force push avec --force pour remplacer complètement
echo -e "   Envoi vers GitHub..."
git push origin "$CURRENT_BRANCH" --force

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Déploiement réussi!${NC}"
    echo ""
    echo -e "${CYAN}📋 Résumé:${NC}"
    echo -e "   - Remote: $REMOTE"
    echo -e "   - Branche: $CURRENT_BRANCH"
    echo -e "   - Commit: $COMMIT_MESSAGE"
    echo ""
    echo -e "${CYAN}🌐 Vérifiez votre dépôt: $REMOTE${NC}"
else
    echo ""
    echo -e "${RED}❌ Erreur lors du push!${NC}"
    echo -e "${YELLOW}   Vérifiez:${NC}"
    echo -e "${YELLOW}   1. Vos credentials GitHub${NC}"
    echo -e "${YELLOW}   2. Vos permissions sur le dépôt${NC}"
    echo -e "${YELLOW}   3. La connexion Internet${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Déploiement terminé!${NC}"
echo -e "${GREEN}========================================${NC}"

