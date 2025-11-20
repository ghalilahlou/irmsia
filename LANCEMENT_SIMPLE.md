# 🚀 Lancer l'Application - Guide Simple

## ✅ Configuration Terminée !

Vos dépendances sont installées. Vous pouvez maintenant lancer l'application.

## Méthode 1 : Script Automatique (Recommandé)

```powershell
.\scripts\start.ps1
```

## Méthode 2 : Commande Directe

```powershell
cd backend
python main.py
```

## Méthode 3 : Avec Environnement Virtuel

```powershell
cd backend
.\venv\Scripts\activate
python main.py
```

## Méthode 4 : Avec Docker

```powershell
docker-compose up -d
```

---

## ✅ Vérification

Une fois lancé, ouvrez votre navigateur :

1. **Health Check** : http://localhost:8000/health
2. **Documentation API** : http://localhost:8000/docs

---

## 🔐 Se Connecter à l'API

### 1. Obtenir un token

**Avec PowerShell :**
```powershell
$body = @{
    username = "radiologist"
    password = "radio123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST `
    -ContentType "application/x-www-form-urlencoded" `
    -Body "username=radiologist&password=radio123"

$token = $response.access_token
Write-Host "Token: $token"
```

**Avec curl (si installé) :**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=radiologist&password=radio123"
```

### 2. Utiliser le token

Ajoutez dans vos requêtes :
```
Authorization: Bearer <votre-token>
```

---

## 📝 Comptes de Test

- **Admin** : `admin` / `admin123`
- **Radiologist** : `radiologist` / `radio123`

---

## 🐛 Si l'application ne démarre pas

### Erreur : "Module not found"
```powershell
cd backend
pip install -r requirements.txt
```

### Erreur : "Port already in use"
```powershell
# Trouver le processus
netstat -ano | findstr :8000

# Arrêter (remplacer PID)
taskkill /PID <PID> /F
```

### Erreur : "SECRET_KEY not set"
Vérifiez que le fichier `.env` existe et contient `SECRET_KEY` et `ENCRYPTION_KEY`.

---

**Prêt à démarrer ! 🎉**

