# 🚀 Guide de Démarrage - IRMSIA Medical AI

## 📋 Méthode 1 : Script Automatique (Recommandé)

### Étape 1 : Configuration initiale
```powershell
.\scripts\setup.ps1
```

Ce script va :
- ✅ Vérifier Python
- ✅ Créer le fichier `.env`
- ✅ Générer les clés de sécurité
- ✅ Créer les répertoires nécessaires
- ✅ Créer l'environnement virtuel
- ✅ Installer les dépendances

### Étape 2 : Lancer l'application

#### Option A : Localement
```powershell
.\scripts\start.ps1
```

#### Option B : Avec Docker
```powershell
.\scripts\start-docker.ps1
```

---

## 📋 Méthode 2 : Manuel (Étape par étape)

### Étape 1 : Créer le fichier .env
```powershell
Copy-Item env.example .env
```

### Étape 2 : Générer les clés de sécurité
```powershell
# Générer SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Générer ENCRYPTION_KEY
python -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_hex(32))"
```

Copiez les valeurs générées dans le fichier `.env`.

### Étape 3 : Créer les répertoires
```powershell
New-Item -ItemType Directory -Force -Path storage\uploads
New-Item -ItemType Directory -Force -Path storage\encrypted
New-Item -ItemType Directory -Force -Path storage\png
New-Item -ItemType Directory -Force -Path storage\png\temp
New-Item -ItemType Directory -Force -Path logs
```

### Étape 4 : Installer les dépendances

#### Avec environnement virtuel (Recommandé)
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

#### Sans environnement virtuel
```powershell
cd backend
pip install -r requirements.txt
```

### Étape 5 : Lancer l'application

#### Localement
```powershell
cd backend
python main.py
```

#### Avec Docker
```powershell
docker-compose up -d
```

---

## ✅ Vérification

Une fois l'application lancée, vérifiez :

1. **Health Check** : http://localhost:8000/health
2. **Documentation API** : http://localhost:8000/docs

---

## 🔐 Comptes de test

- **Admin** : `admin` / `admin123`
- **Radiologist** : `radiologist` / `radio123`

⚠️ **À changer en production !**

---

## 🐛 Dépannage

### Erreur : "SECRET_KEY not set"
```powershell
# Vérifier que .env existe
Test-Path .env

# Vérifier le contenu
Get-Content .env | Select-String "SECRET_KEY"
```

### Erreur : "Module not found"
```powershell
# Réinstaller les dépendances
cd backend
pip install -r requirements.txt
```

### Erreur : "Port already in use"
```powershell
# Trouver le processus utilisant le port 8000
netstat -ano | findstr :8000

# Arrêter le processus (remplacer PID par le numéro trouvé)
taskkill /PID <PID> /F
```

### Erreur : "Permission denied" (PowerShell)
```powershell
# Autoriser l'exécution de scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📝 Commandes Docker utiles

```powershell
# Voir les logs
docker-compose logs -f backend

# Arrêter les conteneurs
docker-compose down

# Redémarrer
docker-compose restart

# Reconstruire les images
docker-compose build --no-cache

# Voir le statut
docker-compose ps
```

---

## 🎯 Prochaines étapes

1. ✅ Configuration terminée
2. ✅ Application lancée
3. 📖 Consulter la documentation : http://localhost:8000/docs
4. 🧪 Tester l'API avec les comptes de test
5. 📤 Uploader un fichier DICOM de test

---

**Besoin d'aide ?** Consultez `README.md` pour la documentation complète.

