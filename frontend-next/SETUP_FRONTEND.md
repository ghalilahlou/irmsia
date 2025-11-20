# 📋 Guide de Configuration - Frontend Next.js

## ✅ Problèmes résolus

### 1. Problème bcrypt
- **Problème**: `AttributeError: module 'bcrypt' has no attribute '__about__'`
- **Solution**: Installation de `bcrypt==4.0.1` (version compatible avec passlib)
- **Status**: ✅ Corrigé

### 2. Warning Pydantic
- **Problème**: `model_used` en conflit avec namespace protégé
- **Solution**: Renommé en `ai_model` dans tous les fichiers
- **Status**: ✅ Corrigé

## 🎯 Frontend Next.js 15 créé

### Structure complète

```
frontend-next/
├── app/                          # Pages Next.js (App Router)
│   ├── login/page.tsx           # Page de connexion
│   ├── dashboard/page.tsx        # Tableau de bord
│   ├── upload/page.tsx           # Upload DICOM
│   ├── analysis/[imageId]/page.tsx  # Analyse IA
│   ├── logs/page.tsx            # Logs d'audit
│   ├── layout.tsx               # Layout principal
│   ├── providers.tsx             # Providers React Query
│   └── globals.css               # Styles globaux
├── components/                   # Composants React
│   ├── ui/                      # Composants UI (ShadCN style)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── input.tsx
│   ├── Navbar.tsx               # Barre de navigation
│   ├── Dropzone.tsx             # Upload drag & drop
│   ├── DicomPreview.tsx         # Aperçu DICOM
│   ├── AnalysisCard.tsx         # Carte d'analyse IA
│   └── BlockchainLogTable.tsx   # Table des logs
├── lib/                         # Utilitaires
│   ├── api.ts                   # Client API Axios
│   ├── auth.ts                  # Helpers authentification
│   └── utils.ts                 # Fonctions utilitaires
└── package.json                 # Dépendances
```

## 🚀 Installation

### 1. Installer les dépendances

```bash
cd frontend-next
npm install
```

### 2. Configuration

Créer `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_COOKIE_NAME=irmsia_token
NEXT_PUBLIC_COOKIE_MAX_AGE=86400
```

### 3. Lancer le frontend

```bash
npm run dev
```

Le frontend sera disponible sur: http://localhost:3000

## 📡 Intégration avec le backend

### Endpoints utilisés

- `POST /api/v1/auth/login` - Connexion
- `POST /api/v1/auth/register` - Inscription
- `GET /api/v1/auth/me` - Informations utilisateur
- `POST /api/v1/dicom/upload` - Upload DICOM
- `GET /api/v1/dicom/{image_id}/metadata` - Métadonnées
- `POST /api/v1/ai/analyze/{image_id}` - Analyse IA
- `GET /api/v1/blockchain/access-logs/{image_id}` - Logs d'accès
- `GET /health` - Health check

## 🔐 Sécurité

- ✅ JWT stocké dans cookie HTTP-only
- ✅ Pas de PHI dans localStorage
- ✅ Headers CSP configurés
- ✅ Refresh automatique du token
- ✅ Redirection automatique sur 401

## 🎨 Fonctionnalités

### Pages

1. **Login** (`/login`)
   - Formulaire de connexion
   - Gestion des erreurs
   - Redirection automatique

2. **Dashboard** (`/dashboard`)
   - Health check du backend
   - Statut des services
   - Actions rapides

3. **Upload** (`/upload`)
   - Drag & drop DICOM
   - Prévisualisation
   - Upload avec progression

4. **Analysis** (`/analysis/[imageId]`)
   - Affichage de l'image DICOM
   - Résultats d'analyse IA
   - Score de risque
   - Findings et recommandations

5. **Logs** (`/logs`)
   - Table des logs d'audit
   - Filtrage et recherche
   - Informations blockchain

## 🛠️ Technologies

- **Next.js 15** - Framework React
- **TypeScript** - Typage statique
- **TailwindCSS** - Styling
- **React Query** - Gestion des données
- **Axios** - Client HTTP
- **Lucide React** - Icônes

## 📝 Notes

- Le frontend est entièrement statique (pas de SSR sauf nécessaire)
- Toutes les données viennent du backend via REST API
- Le backend doit être lancé sur le port 8000
- Les tokens JWT sont gérés automatiquement

## 🐛 Dépannage

### Erreur de connexion API

- Vérifier que le backend est lancé
- Vérifier `NEXT_PUBLIC_API_URL` dans `.env.local`
- Vérifier les CORS dans le backend

### Problème d'authentification

- Vérifier que le cookie est bien défini
- Vérifier la validité du token
- Vérifier les endpoints d'authentification

### Erreurs de build

- Supprimer `.next` et rebuilder
- Vérifier les erreurs TypeScript
- Vérifier les dépendances

