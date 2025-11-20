# 🚀 Démarrage Rapide - IRMSIA Medical AI

## ✅ Étape 1 : Configuration de l'environnement

Le fichier `.env` a été créé. Maintenant, générez les clés de sécurité :

### Option A : Utiliser le script Python (Recommandé)
```powershell
python scripts/generate-keys.py
```

### Option B : Générer manuellement
```powershell
# Générer SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Générer ENCRYPTION_KEY
python -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_hex(32))"
```

Copiez les valeurs générées dans votre fichier `.env`.

## ✅ Étape 2 : Installer les dépendances

```powershell
cd backend
pip install -r requirements.txt
```

## ✅ Étape 3 : Créer les répertoires de stockage

```powershell
# Depuis la racine du projet
New-Item -ItemType Directory -Force -Path storage\uploads
New-Item -ItemType Directory -Force -Path storage\encrypted
New-Item -ItemType Directory -Force -Path storage\png
New-Item -ItemType Directory -Force -Path logs
```

## ✅ Étape 4 : Lancer l'application

### Option A : Avec Docker (Recommandé)
```powershell
docker-compose up -d
```

### Option B : Localement
```powershell
cd backend
python main.py
```

## ✅ Étape 5 : Vérifier que tout fonctionne

1. **Health Check** : http://localhost:8000/health
2. **Documentation API** : http://localhost:8000/docs

## 🔐 Comptes de test

- **Admin** : `admin` / `admin123`
- **Radiologist** : `radiologist` / `radio123`

⚠️ **À changer en production !**

## 📝 Exemple d'utilisation

### 1. Se connecter
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method POST `
  -ContentType "application/x-www-form-urlencoded" `
  -Body "username=radiologist&password=radio123"

$token = $response.access_token
```

### 2. Upload un fichier DICOM
```powershell
$headers = @{
    "Authorization" = "Bearer $token"
}

$form = @{
    file = Get-Item "data\test_brain.dcm"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/dicom/upload" `
  -Method POST `
  -Headers $headers `
  -Form $form
```

### 3. Analyser une image
```powershell
$body = @{
    image_id = "votre-image-id"
    modality = "MRI"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/ai/analyze/votre-image-id" `
  -Method POST `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

## 🐛 Dépannage

### Erreur : "SECRET_KEY not set"
- Vérifiez que le fichier `.env` existe
- Vérifiez que `SECRET_KEY` est défini dans `.env`

### Erreur : "ENCRYPTION_KEY not set"
- Vérifiez que `ENCRYPTION_KEY` est défini dans `.env`
- La clé doit faire 64 caractères hex (32 bytes)

### Erreur : "Module not found"
- Installez les dépendances : `pip install -r backend/requirements.txt`

### Erreur : "Port already in use"
- Changez le port dans `docker-compose.yml` ou arrêtez le processus utilisant le port 8000

## 📚 Documentation complète

- `README.md` - Documentation principale
- `ARCHITECTURE_FINALE.md` - Vue d'ensemble de l'architecture
- `SETUP_ENV.md` - Guide de configuration détaillé

---

**Prêt à démarrer ! 🎉**

