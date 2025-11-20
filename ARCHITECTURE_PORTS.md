# 🏗️ Architecture des Ports - IRMSIA Medical AI

## 📍 Ports Utilisés

### Port 3000 - Frontend (Next.js)
- **Rôle** : Interface utilisateur web
- **URLs d'accès** :
  - `http://localhost:3000` (accès local)
  - `http://10.5.0.2:3000` (accès réseau)
- **Fonctionnalités** :
  - Page de connexion
  - Dashboard
  - Upload de fichiers DICOM
  - Visualisation des analyses IA
  - Logs d'audit blockchain

### Port 8000 - Backend (FastAPI)
- **Rôle** : API REST pour les données
- **URLs d'accès** :
  - `http://localhost:8000` (accès local)
  - `http://10.5.0.2:8000` (accès réseau)
- **Fonctionnalités** :
  - Authentification JWT
  - Upload et traitement DICOM
  - Analyse IA
  - Gestion blockchain
  - Documentation API (`/docs`)

## 🔄 Communication Frontend ↔ Backend

```
┌─────────────────┐         HTTP Requests         ┌─────────────────┐
│   Frontend      │ ────────────────────────────> │    Backend      │
│  Port 3000      │                               │   Port 8000     │
│  (Next.js)      │ <──────────────────────────── │   (FastAPI)     │
│                 │         JSON Responses         │                 │
└─────────────────┘                               └─────────────────┘
```

### Exemple de Requête

Quand vous vous connectez sur `http://10.5.0.2:3000/login` :

1. **Frontend** (port 3000) affiche la page de connexion
2. Vous entrez vos identifiants et cliquez sur "Se connecter"
3. **Frontend** envoie une requête HTTP POST vers :
   - `http://localhost:8000/api/v1/auth/login` (si accès via localhost)
   - `http://10.5.0.2:8000/api/v1/auth/login` (si accès via réseau)
4. **Backend** (port 8000) traite la requête et retourne un token JWT
5. **Frontend** stocke le token et redirige vers le dashboard

## ⚠️ Important

**C'est NORMAL que le port 8000 n'affiche pas le frontend !**

Le port 8000 est le **backend API** qui retourne du **JSON**, pas une interface web.

Pour voir l'interface utilisateur, utilisez le **port 3000**.

## 🔧 Configuration

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend CORS
Le backend autorise les requêtes depuis :
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `http://10.5.0.2:3000` (accès réseau)

### Content Security Policy (CSP)
La CSP autorise les connexions vers :
- `http://localhost:8000`
- `http://10.5.0.2:8000`
- `http://127.0.0.1:8000`

## 🚀 Démarrage

### Backend
```powershell
.\scripts\start.ps1
# Ou
cd backend
python -m backend.main
```
Backend accessible sur : `http://localhost:8000`

### Frontend
```powershell
cd frontend-next
npm run dev
```
Frontend accessible sur : `http://localhost:3000`

## 🧪 Test de Connexion

### Test Backend
```powershell
# Health check
curl http://localhost:8000/health

# Documentation API
# Ouvrir dans le navigateur : http://localhost:8000/docs
```

### Test Frontend → Backend
1. Ouvrir `http://localhost:3000` (ou `http://10.5.0.2:3000`)
2. Se connecter avec `admin` / `admin123`
3. Vérifier la console du navigateur (F12) pour les requêtes API

## 📝 Notes

- Si vous accédez au frontend via l'adresse réseau (`10.5.0.2:3000`), assurez-vous que :
  - Le backend est aussi accessible via cette adresse
  - Les CORS autorisent cette origine
  - La CSP autorise les connexions vers cette adresse

- En production, les deux services peuvent être déployés sur le même domaine avec un reverse proxy (nginx, etc.)

