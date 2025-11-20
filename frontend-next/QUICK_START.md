# 🚀 Quick Start - Frontend Next.js

## Installation rapide

```bash
# 1. Aller dans le dossier frontend-next
cd frontend-next

# 2. Installer les dépendances
npm install

# 3. Le fichier .env.local est déjà créé
# Si besoin, recréer avec: Copy-Item env.example .env.local

# 4. Vérifier que le backend est lancé sur http://localhost:8000

# 5. Lancer le frontend
npm run dev
```

## Accès

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentation API: http://localhost:8000/docs

## Première connexion

1. Ouvrir http://localhost:3000
2. Vous serez redirigé vers `/login`
3. Utiliser les identifiants de votre backend
4. Une fois connecté, accéder au dashboard

## Structure des pages

- `/login` - Page de connexion
- `/dashboard` - Tableau de bord principal
- `/upload` - Upload de fichiers DICOM
- `/analysis/[imageId]` - Analyse IA d'une image
- `/logs` - Logs d'audit blockchain

## Commandes utiles

```bash
# Développement
npm run dev

# Build production
npm run build

# Lancer en production
npm start

# Linter
npm run lint
```

