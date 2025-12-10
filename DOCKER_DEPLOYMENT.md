# 🐳 Guide de Déploiement Docker - IRMSIA

Ce guide vous explique comment déployer l'application IRMSIA complète avec Docker et Docker Compose.

## 📋 Prérequis

1. **Docker Desktop** installé et en cours d'exécution
   - Windows/Mac: [Docker Desktop](https://www.docker.com/products/docker-desktop)
   - Linux: [Docker Engine](https://docs.docker.com/engine/install/)

2. **Docker Compose** (inclus avec Docker Desktop)
   - Vérifier: `docker-compose --version` ou `docker compose version`

3. **Au moins 4 GB de RAM** disponible pour Docker

## 🚀 Déploiement Rapide

### Méthode 1 : Script Automatique (Recommandé)

#### Windows (PowerShell)
```powershell
.\scripts\deploy-docker.ps1
```

#### Linux/Mac (Bash)
```bash
chmod +x scripts/deploy-docker.sh
./scripts/deploy-docker.sh
```

Le script vous guidera interactivement ou vous pouvez utiliser les options:
- `--build` : Construire les images
- `--up` : Démarrer les services
- `--build-up` : Construire et démarrer
- `--down` : Arrêter les services
- `--logs` : Voir les logs
- `--restart` : Redémarrer les services

### Méthode 2 : Commandes Docker Compose Manuelles

#### 1. Préparer l'environnement

```bash
# Copier le fichier d'environnement
cp env.example .env

# Éditer .env avec vos valeurs (optionnel pour développement)
# Les valeurs par défaut fonctionnent pour un déploiement de test
```

#### 2. Construire les images

```bash
docker-compose build
```

#### 3. Démarrer tous les services

```bash
docker-compose up -d
```

#### 4. Vérifier le statut

```bash
docker-compose ps
```

## 📊 Services Déployés

Une fois déployé, les services suivants seront disponibles:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Interface utilisateur Next.js |
| **Backend API** | http://localhost:8000 | API FastAPI |
| **API Documentation** | http://localhost:8000/docs | Documentation Swagger |
| **gRPC Server** | localhost:50051 | Service de diagnostic Deep Learning |

## 🔧 Configuration

### Variables d'environnement

Le fichier `.env` à la racine contrôle la configuration. Principales variables:

```env
# Backend
SECRET_KEY=your-secret-key-change-in-production
ENCRYPTION_KEY=your-encryption-key-32-bytes-hex
DEBUG=false
AI_PROVIDER=mock
BLOCKCHAIN_TYPE=mock

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Database
DATABASE_URL=sqlite:///./medical_audit.db
```

### Volumes Docker

Les données sont persistées dans des volumes:

- `./storage` : Fichiers uploadés et résultats
- `./logs` : Fichiers de logs
- `./backend` : Code backend (monté en développement)
- `./grpc-deeplearning/models` : Modèles de deep learning
- `./grpc-deeplearning/logs` : Logs du service gRPC

## 📝 Commandes Utiles

### Voir les logs

```bash
# Tous les services
docker-compose logs -f

# Un service spécifique
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f grpc-server
```

### Redémarrer un service

```bash
docker-compose restart frontend
docker-compose restart backend
docker-compose restart grpc-server
```

### Arrêter les services

```bash
# Arrêter sans supprimer les volumes
docker-compose stop

# Arrêter et supprimer les conteneurs
docker-compose down

# Arrêter et supprimer les volumes (⚠️ supprime les données)
docker-compose down -v
```

### Reconstruire une image

```bash
# Reconstruire une image spécifique
docker-compose build --no-cache frontend

# Reconstruire toutes les images
docker-compose build --no-cache
```

### Accéder à un conteneur

```bash
# Shell dans le conteneur backend
docker-compose exec backend bash

# Shell dans le conteneur frontend
docker-compose exec frontend sh
```

## 🔍 Vérification de Santé

### Health Checks

Chaque service a un health check configuré:

```bash
# Vérifier le statut des health checks
docker-compose ps

# Tester manuellement
curl http://localhost:8000/health
curl http://localhost:3000
```

### Logs de Démarrage

Si un service ne démarre pas:

```bash
# Voir les logs d'erreur
docker-compose logs backend
docker-compose logs frontend
docker-compose logs grpc-server
```

## 🐛 Dépannage

### Problème: Port déjà utilisé

**Erreur:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution:** Arrêter le service qui utilise le port ou modifier les ports dans `docker-compose.yml`

```yaml
ports:
  - "8001:8000"  # Utiliser le port 8001 au lieu de 8000
```

### Problème: Erreur de build

**Erreur:** `ERROR: failed to solve: process "/bin/sh -c npm ci" did not complete successfully`

**Solution:** 
1. Vérifier que Docker a assez de mémoire (minimum 4GB)
2. Nettoyer le cache Docker: `docker system prune -a`
3. Reconstruire: `docker-compose build --no-cache`

### Problème: Frontend ne se connecte pas au backend

**Symptôme:** Erreurs CORS ou 404 dans le frontend

**Solution:**
1. Vérifier que `NEXT_PUBLIC_API_URL` dans `.env` pointe vers `http://localhost:8000`
2. Vérifier que le backend est démarré: `docker-compose ps`
3. Vérifier les logs: `docker-compose logs backend`

### Problème: gRPC Server ne démarre pas

**Symptôme:** Le service grpc-server est en état "unhealthy" ou "restarting"

**Solution:**
1. Vérifier les logs: `docker-compose logs grpc-server`
2. Vérifier que les fichiers proto sont générés
3. Pour GPU: Vérifier que Docker Desktop a accès au GPU (Settings > Resources > Advanced)

### Problème: Permissions sur les volumes

**Erreur:** `Permission denied` lors de l'écriture dans les volumes

**Solution (Linux):**
```bash
sudo chown -R $USER:$USER ./storage ./logs
```

## 🚀 Déploiement en Production

### 1. Configuration Production

Créer un fichier `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  frontend:
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=https://api.votre-domaine.com
    # ... autres configurations

  backend:
    environment:
      - DEBUG=false
      - SECRET_KEY=${SECRET_KEY}  # Depuis variables d'environnement sécurisées
      - DATABASE_URL=${DATABASE_URL}  # PostgreSQL en production
    # ... autres configurations

  postgres:
    profiles:
      - production
    # ... configuration PostgreSQL
```

### 2. Utiliser PostgreSQL

```bash
# Démarrer avec le profil production
docker-compose --profile production up -d postgres

# Mettre à jour DATABASE_URL dans .env
DATABASE_URL=postgresql://irmsia:password@postgres:5432/medical_audit
```

### 3. Variables d'environnement sécurisées

Ne jamais commiter `.env` en production. Utiliser:
- Docker Secrets
- Variables d'environnement du système
- Services de gestion de secrets (AWS Secrets Manager, HashiCorp Vault)

### 4. Reverse Proxy (Nginx/Traefik)

Pour la production, ajouter un reverse proxy devant les services:

```yaml
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend
```

## 📦 Structure des Images

- **frontend**: Node.js 20 Alpine, Next.js standalone
- **backend**: Python 3.11 Slim, FastAPI avec Uvicorn
- **grpc-server**: Python 3.11 Slim, PyTorch pour Deep Learning

## 🔐 Sécurité

### Bonnes Pratiques

1. **Ne jamais commiter `.env`** - Utiliser `.env.example` comme template
2. **Changer les secrets par défaut** - Les valeurs dans `env.example` sont pour le développement
3. **Utiliser HTTPS en production** - Configurer un reverse proxy avec SSL
4. **Limiter les ports exposés** - Ne pas exposer de ports inutiles
5. **Mettre à jour régulièrement** - `docker-compose pull` pour les images de base

### Secrets

Pour générer des clés sécurisées:

```bash
# SECRET_KEY (32+ caractères)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# ENCRYPTION_KEY (64 caractères hex pour AES-256)
python -c "import secrets; print(secrets.token_hex(32))"
```

## 📚 Ressources

- [Documentation Docker](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Next.js Docker Deployment](https://nextjs.org/docs/deployment#docker-image)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

## 🆘 Support

En cas de problème:

1. Vérifier les logs: `docker-compose logs`
2. Vérifier le statut: `docker-compose ps`
3. Vérifier les ressources Docker: Docker Desktop > Settings > Resources
4. Consulter la documentation ci-dessus

---

**Bon déploiement ! 🚀**

