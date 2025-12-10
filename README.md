# 🏥 IRMSIA - Intelligent Radiology Medical System with AI

**Système d'analyse d'imagerie médicale avec Deep Learning et Blockchain**

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12+-green)
![Next.js](https://img.shields.io/badge/next.js-15+-black)
![License](https://img.shields.io/badge/license-MIT-yellow)

## 🎯 Fonctionnalités

### 📊 Analyse d'Images Médicales
- **Détection d'anomalies** : Tumeurs, infections, hémorragies, fractures, œdèmes
- **Segmentation** : Délimitation précise des régions d'intérêt
- **Visualisations** : Heatmaps GradCAM, annotations, vues zoomées
- **Rapports automatisés** : Génération de rapports médicaux détaillés

### 🔒 Sécurité & Conformité
- **Chiffrement AES-256** des données médicales
- **Dé-identification DICOM** automatique
- **Audit blockchain** de tous les accès
- **Authentification JWT**

### 🖥️ Interface Moderne
- **Visualiseur DICOM** professionnel avec outils de mesure
- **Dashboard interactif** avec suivi des analyses
- **Export de rapports** PDF et texte

---

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.12+
- Node.js 20+
- Git

### Installation

```bash
# 1. Cloner le projet
git clone https://github.com/ghalilahlou/irmsia.git
cd irmsia

# 2. Configuration Backend
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. Configuration Frontend
cd ../frontend-next
npm install

# 4. Variables d'environnement
cp backend/env.example backend/.env
# Éditer .env avec vos clés
```

### Démarrage

```bash
# Terminal 1 - Backend
cd backend
.\venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend-next
npm run dev
```

**Accès :**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## 📁 Structure du Projet

```
irmsia/
├── backend/                 # API FastAPI
│   ├── api/                # Routes API
│   │   ├── analysis.py     # Routes d'analyse unifiées
│   │   ├── dicom_router.py # Routes DICOM
│   │   └── auth_router.py  # Authentification
│   ├── services/           # Services métier
│   │   ├── analysis/       # Détection, segmentation, visualisation
│   │   └── reports/        # Génération de rapports
│   ├── core/               # Configuration, sécurité, DB
│   └── main.py             # Point d'entrée
│
├── frontend-next/          # Interface Next.js
│   ├── app/                # Pages et routes
│   ├── components/         # Composants React
│   │   ├── analysis/       # Visualisation des analyses
│   │   └── dicom/          # Visualiseur DICOM
│   ├── lib/                # Utilitaires et API clients
│   └── hooks/              # Hooks React personnalisés
│
├── grpc-deeplearning/      # Serveur Deep Learning (optionnel)
│   ├── server/             # Serveur gRPC
│   └── models/             # Modèles DL
│
└── docker-compose.yml      # Déploiement Docker
```

---

## 🔧 API Reference

### Analyse d'Images

```http
POST /api/v1/analysis/detect
Content-Type: multipart/form-data

file: <image_file>
include_segmentation: true
include_visualization: true
```

**Réponse :**
```json
{
  "status": "success",
  "has_anomaly": true,
  "anomaly_class": "tumor",
  "confidence": 0.89,
  "bounding_boxes": [...],
  "measurements": {...},
  "visualizations": {
    "annotated": "<base64>",
    "heatmap": "<base64>"
  }
}
```

### Génération de Rapport

```http
POST /api/v1/analysis/report
Content-Type: multipart/form-data

file: <image_file>
modality: MRI
format: json
```

---

## 🧠 Deep Learning

### Backends Supportés
1. **MONAI** - Framework médical spécialisé (recommandé)
2. **PyTorch** - Modèles génériques
3. **Simple** - Traitement d'image basique (fallback)

### Modèles
- **Détection** : DenseNet121, ResNet50
- **Segmentation** : U-Net
- **Visualisation** : GradCAM

### Entraînement Personnalisé
```python
from backend.services.analysis import AnomalyDetector

detector = AnomalyDetector(backend='monai')
result = detector.detect('path/to/image.dcm')
```

---

## 📊 Rapports Médicaux

Les rapports générés incluent :
- ✅ Synthèse globale (normal/anormal/critique)
- ✅ Trouvailles détaillées avec localisation
- ✅ Mesures quantitatives (surface, périmètre)
- ✅ Visualisations annotées
- ✅ Recommandations cliniques

---

## 🐳 Déploiement Docker

Déployez l'application complète avec Docker Compose en une seule commande !

### Démarrage Rapide

```bash
# Windows PowerShell
.\scripts\deploy-docker.ps1

# Linux/Mac
./scripts/deploy-docker.sh
```

Ou manuellement :
```bash
docker-compose up -d
```

### Services Déployés

- **Frontend** : Next.js (http://localhost:3000)
- **Backend** : API FastAPI (http://localhost:8000)
- **gRPC Server** : Service Deep Learning (localhost:50051)
- **PostgreSQL** : Base de données (optionnel, port 5432)
- **IPFS** : Blockchain storage (optionnel, port 5001)

### Documentation Complète

Consultez le [Guide de Déploiement Docker](DOCKER_DEPLOYMENT.md) pour :
- Configuration détaillée
- Dépannage
- Déploiement en production
- Bonnes pratiques de sécurité

---

## 🔐 Configuration

### Variables d'Environnement

```env
# Backend (.env)
SECRET_KEY=your-secret-key-32-chars
ENCRYPTION_KEY=your-encryption-key-32-chars
DEBUG=true
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./medical_audit.db

# AI Configuration
OPENAI_API_KEY=sk-...  # Optionnel
ANTHROPIC_API_KEY=...   # Optionnel
```

---

## 📝 Licence

MIT License - Voir [LICENSE](LICENSE)

---

## 👥 Contributeurs

- **IRMSIA Team** - Développement principal

---

## 🚀 Déploiement sur GitHub

Pour déployer ce projet sur GitHub, consultez le [Guide de Déploiement](DEPLOYMENT.md).

**Déploiement rapide :**
```bash
# Windows PowerShell
.\scripts\deploy-github.ps1
```

## 📞 Support

- 📧 Email: support@irmsia.com
- 📖 Documentation: [Wiki](https://github.com/your-org/irmsia/wiki)
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/irmsia/issues)
