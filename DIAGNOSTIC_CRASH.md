# 🔍 Diagnostic des Crashes au Démarrage

## Scripts de Diagnostic

### 1. Diagnostic Complet
```powershell
.\scripts\diagnostic.ps1
```
Vérifie :
- Fichier `.env` et variables requises
- Environnement virtuel Python
- Dépendances Python installées
- Répertoires de stockage
- Imports Python critiques
- Configuration frontend
- Ports disponibles
- Test d'import de l'application

### 2. Test de Démarrage
```powershell
.\scripts\test-startup.ps1
```
Teste le démarrage réel de l'application avec capture d'erreurs.

## Causes Courantes de Crash

### 1. Variables d'Environnement Manquantes

**Symptôme :**
```
pydantic_core._pydantic_core.ValidationError: Field required
SECRET_KEY Field required
ENCRYPTION_KEY Field required
```

**Solution :**
Vérifiez que le fichier `.env` existe à la racine et contient :
```env
SECRET_KEY=votre-secret-key-ici
ENCRYPTION_KEY=votre-encryption-key-32-bytes-hex
```

### 2. Erreur d'Import

**Symptôme :**
```
ModuleNotFoundError: No module named 'backend'
ImportError: cannot import name 'settings' from 'backend.core.config'
```

**Solution :**
- Vérifiez que vous êtes à la racine du projet
- Activez l'environnement virtuel : `backend\venv\Scripts\activate.ps1`
- Réinstallez les dépendances : `pip install -r backend/requirements.txt`

### 3. Erreur de Sécurité

**Symptôme :**
```
AttributeError: module 'bcrypt' has no attribute '__about__'
```

**Solution :**
```powershell
pip install bcrypt==4.0.1
```

### 4. Erreur de Base de Données

**Symptôme :**
```
sqlalchemy.exc.OperationalError: unable to open database file
```

**Solution :**
- Vérifiez que le répertoire parent de la base de données existe
- Vérifiez les permissions d'écriture

### 5. Port Déjà Utilisé

**Symptôme :**
```
OSError: [WinError 10048] Only one usage of each socket address is normally permitted
```

**Solution :**
- Arrêtez l'application qui utilise le port 8000
- Ou changez le port dans `.env` : `PORT=8001`

## Logs Détaillés

Pour voir les logs détaillés au démarrage :

```powershell
# Backend avec logs détaillés
cd backend
python -m backend.main

# Ou avec uvicorn directement
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --log-level debug
```

## Vérification Manuelle

### 1. Test d'Import Python
```powershell
python -c "from backend.core.config import settings; print('OK')"
```

### 2. Test de SecurityManager
```powershell
python -c "from backend.core.security import security_manager; print('OK')"
```

### 3. Test de l'Application
```powershell
python -c "from backend.main import app; print('OK')"
```

## Fichiers à Vérifier

1. **`.env`** - Variables d'environnement
2. **`backend/core/config.py`** - Configuration
3. **`backend/core/security.py`** - Gestionnaire de sécurité
4. **`backend/main.py`** - Point d'entrée
5. **`backend/requirements.txt`** - Dépendances

## Prochaines Étapes

Si le diagnostic ne trouve pas d'erreur mais que l'application crash toujours :

1. **Capturez les logs complets** :
   ```powershell
   python -m backend.main 2>&1 | Tee-Object -FilePath crash.log
   ```

2. **Vérifiez les logs** dans `logs/irmsia.log`

3. **Testez chaque module individuellement** :
   ```powershell
   python -c "import backend.core.config"
   python -c "import backend.core.security"
   python -c "import backend.core.database"
   python -c "import backend.api.auth_router"
   ```

4. **Contactez le support** avec :
   - Le fichier `crash.log`
   - Le résultat de `.\scripts\diagnostic.ps1`
   - Les logs de `logs/irmsia.log`

