# 📋 Guide de Refonte - IRMSIA Medical AI

## ✅ Refonte Complète Effectuée

Votre projet a été entièrement refondu selon le cahier des charges fourni. Voici ce qui a été créé :

## 🏗️ Nouvelle Architecture

### Structure des Dossiers

```
backend/
├── api/                    # Routes API REST
│   ├── auth_router.py     # Authentification JWT
│   ├── dicom_router.py    # Upload et traitement DICOM
│   ├── ai_router.py       # Analyse IA
│   └── blockchain_router.py # Blockchain et logs
│
├── core/                   # Configuration centrale
│   ├── config.py          # Variables d'environnement (Pydantic)
│   ├── security.py        # JWT, AES-256, hash SHA-256
│   └── database.py        # Configuration SQLAlchemy
│
├── services/              # Services métier
│   ├── dicom_service.py  # DICOM: upload, dé-id, conversion, chiffrement
│   ├── ai_service.py     # IA: Mock, Hugging Face, OpenAI
│   ├── blockchain_service.py # Blockchain: IPFS, Fabric, Mock
│   └── storage_service.py # Stockage: Local, S3
│
├── models/                # DTOs Pydantic
│   └── dto.py            # Tous les modèles de données
│
├── main.py               # Application FastAPI principale
├── Dockerfile           # Image Docker
└── requirements.txt     # Dépendances Python
```

## 🎯 Fonctionnalités Implémentées

### ✅ 1. Module DICOM (`dicom_service.py`)

- ✅ Upload de fichiers DICOM
- ✅ Dé-identification automatique (suppression tags patient)
- ✅ Conversion DICOM → PNG
- ✅ Chiffrement AES-256-GCM
- ✅ Extraction de métadonnées (dé-identifiées)

### ✅ 2. Module IA (`ai_service.py`)

- ✅ Mode Mock (pour tests)
- ✅ Support Hugging Face (modèles locaux)
- ✅ Support OpenAI Vision API
- ✅ Analyse avec findings, risk_score, diagnosis
- ✅ Recommandations automatiques

### ✅ 3. Module Blockchain (`blockchain_service.py`)

- ✅ Mode Mock (pour développement)
- ✅ Support IPFS (stockage décentralisé)
- ✅ Support Hyperledger Fabric (structure prête)
- ✅ Enregistrement de hash SHA-256
- ✅ Logs d'accès traçables

### ✅ 4. Sécurité (`security.py`)

- ✅ JWT Authentication
- ✅ Chiffrement AES-256-GCM
- ✅ Hash SHA-256
- ✅ Password hashing (bcrypt)

### ✅ 5. API REST

- ✅ `/api/v1/auth/login` - Authentification
- ✅ `/api/v1/auth/register` - Inscription
- ✅ `/api/v1/dicom/upload` - Upload DICOM
- ✅ `/api/v1/ai/analyze/{image_id}` - Analyse IA
- ✅ `/api/v1/blockchain/hash/{image_id}` - Consultation blockchain
- ✅ `/api/v1/blockchain/access-logs/{image_id}` - Logs d'accès

## 🚀 Démarrage Rapide

### 1. Configuration

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer .env avec vos clés
# IMPORTANT: Générer SECRET_KEY et ENCRYPTION_KEY sécurisés
```

### 2. Générer les clés de sécurité

```python
# Générer SECRET_KEY (min 32 caractères)
import secrets
secrets.token_urlsafe(32)

# Générer ENCRYPTION_KEY (64 caractères hex = 32 bytes)
import secrets
secrets.token_hex(32)
```

### 3. Lancer avec Docker (Recommandé)

```bash
docker-compose up -d
```

### 4. Lancer localement

```bash
cd backend
pip install -r requirements.txt
python main.py
```

## 📝 Flux de Traitement

### Upload DICOM

```
1. Upload fichier DICOM
   ↓
2. Dé-identification (suppression données patient)
   ↓
3. Conversion DICOM → PNG
   ↓
4. Chiffrement AES-256-GCM
   ↓
5. Calcul hash SHA-256
   ↓
6. Enregistrement hash sur blockchain
   ↓
7. Retour image_id
```

### Analyse IA

```
1. Requête analyse avec image_id
   ↓
2. Déchiffrement temporaire de l'image
   ↓
3. Analyse avec modèle vision + LLM
   ↓
4. Génération rapport (findings, risk_score, diagnosis)
   ↓
5. Log d'accès sur blockchain
   ↓
6. Nettoyage fichier temporaire
   ↓
7. Retour résultats
```

## 🔧 Configuration des Providers

### AI Provider

```env
# Mock (par défaut, pour tests)
AI_PROVIDER=mock

# Hugging Face (modèles locaux)
AI_PROVIDER=huggingface
HUGGINGFACE_MODEL=microsoft/git-base

# OpenAI (meilleure qualité)
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-vision-preview
```

### Blockchain Provider

```env
# Mock (par défaut, pour développement)
BLOCKCHAIN_TYPE=mock

# IPFS (stockage décentralisé)
BLOCKCHAIN_TYPE=ipfs
IPFS_HOST=127.0.0.1
IPFS_PORT=5001

# Hyperledger Fabric (entreprise)
BLOCKCHAIN_TYPE=fabric
FABRIC_NETWORK_CONFIG=/path/to/config
```

## 📊 Comptes Utilisateurs par Défaut

Pour tester rapidement :

- **Admin** : `admin` / `admin123`
- **Radiologist** : `radiologist` / `radio123`

⚠️ **À changer en production !**

## 🔒 Sécurité

### Chiffrement

- **AES-256-GCM** : Chiffrement symétrique avec authentification
- **Nonce unique** : Chaque fichier a son propre nonce
- **Clé de 32 bytes** : Stockée dans `ENCRYPTION_KEY`

### Authentification

- **JWT** : Tokens avec expiration (30 min par défaut)
- **Bcrypt** : Hash des mots de passe
- **OAuth2** : Flow standard

### Dé-identification DICOM

Suppression automatique de :
- Patient Name
- Patient ID
- Date de naissance
- Adresse
- Téléphone
- Etc.

## 📦 Dépendances Principales

- **FastAPI** : Framework web moderne
- **pydicom** : Traitement DICOM
- **Pillow** : Conversion d'images
- **cryptography** : Chiffrement
- **transformers** : Modèles Hugging Face
- **ipfshttpclient** : IPFS
- **web3** : Ethereum
- **sqlalchemy** : Base de données

## 🧪 Tests

Pour tester l'API :

1. **Se connecter**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=radiologist&password=radio123"
```

2. **Upload DICOM**
```bash
curl -X POST "http://localhost:8000/api/v1/dicom/upload" \
  -H "Authorization: Bearer <token>" \
  -F "file=@test.dcm"
```

3. **Analyser**
```bash
curl -X POST "http://localhost:8000/api/v1/ai/analyze/{image_id}" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"image_id": "...", "modality": "MRI"}'
```

## 📚 Documentation API

Une fois l'application lancée :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

## 🔄 Migration depuis l'Ancienne Architecture

L'ancienne architecture (`app/`, `ai/`, `utils/`) est conservée mais non utilisée par la nouvelle API.

Pour migrer progressivement :
1. Utiliser la nouvelle API (`backend/`)
2. Migrer les fonctionnalités existantes si nécessaire
3. Supprimer l'ancien code une fois la migration complète

## 🎯 Prochaines Étapes

- [ ] Ajouter des tests unitaires
- [ ] Implémenter complètement Hyperledger Fabric
- [ ] Ajouter support S3 pour production
- [ ] Créer interface web frontend
- [ ] Dashboard d'administration
- [ ] Export PDF des rapports

## 📞 Support

Pour toute question ou problème, consulter :
- `README.md` : Documentation complète
- `/docs` : Documentation interactive de l'API
- Logs : `./logs/irmsia.log`

---

**Refonte complétée avec succès ! 🎉**

