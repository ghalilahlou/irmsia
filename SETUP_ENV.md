# 🔧 Configuration de l'Environnement

## Étape 1 : Créer le fichier .env

Le fichier `.env.example` est ignoré par git. Créez votre fichier `.env` manuellement :

### Option 1 : Copier depuis env.example
```powershell
# PowerShell
Copy-Item env.example .env
```

### Option 2 : Créer manuellement
Créez un fichier `.env` à la racine du projet avec le contenu suivant :

```env
# Application
DEBUG=true
SECRET_KEY=votre-cle-secrete-min-32-caracteres
ENCRYPTION_KEY=votre-cle-chiffrement-64-caracteres-hex

# CORS
ALLOWED_HOSTS=["http://localhost:3000","http://localhost:8000"]

# Storage
UPLOAD_DIR=./storage/uploads
ENCRYPTED_DIR=./storage/encrypted
PNG_DIR=./storage/png
MAX_UPLOAD_SIZE=104857600

# AI Configuration
AI_PROVIDER=mock

# Blockchain
BLOCKCHAIN_TYPE=mock

# Database
DATABASE_URL=sqlite:///./medical_audit.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/irmsia.log
```

## Étape 2 : Générer les clés de sécurité

### Générer SECRET_KEY (min 32 caractères)
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Générer ENCRYPTION_KEY (64 caractères hex = 32 bytes)
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

### Exemple de clés générées :
```
SECRET_KEY=nJq9UfCm6oPpN90RVR-WNK17wanw7RLZolWcWmHkwT0
ENCRYPTION_KEY=53db9323f068f3421f835da68168be9326cd5635b72a6032fa779789e602aaa5
```

## Étape 3 : Éditer .env

Ouvrez le fichier `.env` et remplacez :
- `SECRET_KEY` par la clé générée
- `ENCRYPTION_KEY` par la clé générée

## ⚠️ Important

- **Ne commitez JAMAIS le fichier `.env`** dans git
- Gardez vos clés secrètes et ne les partagez pas
- En production, utilisez des variables d'environnement système ou un gestionnaire de secrets

## Configuration Optionnelle

### Pour utiliser OpenAI
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-votre-cle-api
```

### Pour utiliser IPFS
```env
BLOCKCHAIN_TYPE=ipfs
IPFS_HOST=127.0.0.1
IPFS_PORT=5001
```

### Pour utiliser PostgreSQL
```env
DATABASE_URL=postgresql://user:password@localhost/medical_audit
```

### Pour utiliser S3
```env
USE_S3=true
AWS_ACCESS_KEY_ID=votre-cle
AWS_SECRET_ACCESS_KEY=votre-secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=votre-bucket
```

