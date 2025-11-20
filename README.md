# IRMSIA Medical AI - Backend

Application d'analyse d'imagerie médicale avec IA et blockchain pour la sécurité et la traçabilité.

## 🎯 Fonctionnalités

- **Upload DICOM** : Upload, dé-identification automatique, conversion PNG
- **Chiffrement AES-256** : Stockage sécurisé des images médicales
- **Analyse IA** : Vision + LLM multimodal (Mock, Hugging Face, OpenAI)
- **Blockchain** : Enregistrement des hash et logs d'accès (IPFS, Hyperledger Fabric)
- **API REST sécurisée** : JWT authentication, audit logs complets
- **Stockage flexible** : Local (POC) ou S3 (production)

## 🏗️ Architecture

```
backend/
├── api/              # Routes API
│   ├── auth_router.py
│   ├── dicom_router.py
│   ├── ai_router.py
│   └── blockchain_router.py
├── core/             # Configuration centrale
│   ├── config.py
│   ├── security.py
│   └── database.py
├── services/         # Services métier
│   ├── dicom_service.py
│   ├── ai_service.py
│   ├── blockchain_service.py
│   └── storage_service.py
├── models/           # DTOs Pydantic
│   └── dto.py
└── main.py           # Application FastAPI
```

## 🚀 Installation

### Prérequis

- Python 3.11+
- Docker & Docker Compose (recommandé)
- IPFS (optionnel, pour blockchain)

### Installation locale

1. **Cloner le repository**
```bash
git clone <repository-url>
cd irmsia
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Installer les dépendances**
```bash
cd backend
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
cp .env.example .env
```

Éditer `.env` :
```env
# Sécurité
SECRET_KEY=your-secret-key-min-32-chars
ENCRYPTION_KEY=your-encryption-key-64-hex-chars-for-32-bytes

# AI
AI_PROVIDER=mock  # mock, huggingface, openai
OPENAI_API_KEY=your-openai-key  # Si AI_PROVIDER=openai

# Blockchain
BLOCKCHAIN_TYPE=mock  # mock, ipfs, fabric
IPFS_HOST=127.0.0.1
IPFS_PORT=5001

# Database
DATABASE_URL=sqlite:///./medical_audit.db
```

5. **Lancer l'application**
```bash
cd backend
python main.py
```

L'API sera disponible sur `http://localhost:8000`

### Installation avec Docker

1. **Créer le fichier `.env`** (voir ci-dessus)

2. **Lancer avec Docker Compose**
```bash
docker-compose up -d
```

3. **Vérifier les logs**
```bash
docker-compose logs -f backend
```

## 📖 Utilisation de l'API

### Documentation interactive

Une fois l'application lancée, accédez à :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

### Authentification

1. **Créer un compte** (ou utiliser les comptes par défaut)
```bash
POST /api/v1/auth/register
{
  "username": "radiologist",
  "email": "radio@example.com",
  "password": "secure_password",
  "role": "radiologist"
}
```

2. **Se connecter**
```bash
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=radiologist&password=secure_password
```

Réponse :
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

3. **Utiliser le token** dans les requêtes suivantes
```bash
Authorization: Bearer <access_token>
```

### Upload DICOM

```bash
POST /api/v1/dicom/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <fichier.dcm>
```

Réponse :
```json
{
  "image_id": "uuid-here",
  "message": "Fichier DICOM traité avec succès",
  "deidentified": true,
  "converted": true,
  "encrypted": true,
  "hash_registered": true,
  "timestamp": "2024-01-01T12:00:00"
}
```

### Analyse IA

```bash
POST /api/v1/ai/analyze/{image_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "image_id": "uuid-here",
  "modality": "MRI",
  "additional_context": "Patient avec maux de tête"
}
```

Réponse :
```json
{
  "image_id": "uuid-here",
  "findings": [
    {
      "description": "Aucune anomalie significative",
      "location": "Global",
      "confidence": 0.85,
      "severity": "normal"
    }
  ],
  "risk_score": 15,
  "suggested_diagnosis": "Examen normal",
  "confidence": 0.75,
  "model_used": "mock",
  "processing_time": 0.5,
  "timestamp": "2024-01-01T12:00:00",
  "recommendations": ["Suivi standard"]
}
```

## 🔧 Configuration

### Providers IA

#### Mode Mock (par défaut)
```env
AI_PROVIDER=mock
```
- Aucune dépendance externe
- Résultats simulés pour tests

#### Hugging Face
```env
AI_PROVIDER=huggingface
HUGGINGFACE_MODEL=microsoft/git-base
```
- Modèles locaux
- Nécessite GPU pour de meilleures performances

#### OpenAI
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-vision-preview
```
- API payante
- Meilleure qualité d'analyse

### Blockchain

#### Mode Mock (par défaut)
```env
BLOCKCHAIN_TYPE=mock
```
- Stockage en mémoire
- Pour développement

#### IPFS
```env
BLOCKCHAIN_TYPE=ipfs
IPFS_HOST=127.0.0.1
IPFS_PORT=5001
```
- Stockage décentralisé
- Lancer IPFS : `docker-compose up ipfs`

#### Hyperledger Fabric
```env
BLOCKCHAIN_TYPE=fabric
FABRIC_NETWORK_CONFIG=/path/to/config
```
- Pour environnements d'entreprise
- Nécessite configuration réseau Fabric

## 🔒 Sécurité

- **Chiffrement AES-256-GCM** : Toutes les images sont chiffrées
- **JWT Authentication** : Tokens avec expiration
- **Dé-identification DICOM** : Suppression automatique des données patient
- **Audit logs** : Tous les accès sont enregistrés
- **Hash blockchain** : Intégrité des données vérifiable

## 📊 Structure des données

### Flux de traitement DICOM

1. **Upload** → Fichier DICOM original
2. **Dé-identification** → Suppression des tags patient
3. **Conversion** → DICOM → PNG
4. **Chiffrement** → PNG → AES-256-GCM
5. **Hash** → SHA-256 du fichier chiffré
6. **Blockchain** → Enregistrement du hash

### Stockage

```
storage/
├── uploads/          # DICOM originaux (temporaires)
├── encrypted/        # Images chiffrées (.enc)
└── png/             # PNG temporaires (nettoyés après chiffrement)
```

## 🧪 Tests

```bash
# Tests unitaires (à créer)
pytest tests/

# Tests d'intégration
pytest tests/integration/
```

## 🐛 Dépannage

### Erreur de chiffrement
- Vérifier que `ENCRYPTION_KEY` fait 64 caractères hex (32 bytes)

### Erreur IPFS
- Vérifier que IPFS est lancé : `docker-compose up ipfs`
- Vérifier la connexion : `curl http://localhost:5001/api/v0/version`

### Erreur OpenAI
- Vérifier la clé API dans `.env`
- Vérifier les quotas de l'API

## 📝 TODO

- [ ] Implémentation complète Hyperledger Fabric
- [ ] Tests unitaires et d'intégration
- [ ] Support S3 pour production
- [ ] Interface web frontend
- [ ] Dashboard d'administration
- [ ] Export de rapports PDF

## 📄 Licence

[À définir]

## 👥 Auteurs

IRMSIA Medical AI Team

## 🙏 Remerciements

- FastAPI
- pydicom
- MONAI
- Hugging Face
- IPFS
