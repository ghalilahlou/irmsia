# IRMSIA Data Pipeline 📊

**Pipeline complet pour importer, préparer et entraîner des modèles Deep Learning sur des datasets DICOM médicaux**

---

## 🎯 Vue d'Ensemble

Ce pipeline vous permet de :
- 📥 **Télécharger** des datasets médicaux depuis plusieurs sources publiques
- 🗂️ **Organiser** et indexer vos données
- 🏷️ **Labelliser** et créer des splits train/val/test
- 🧠 **Entraîner** des modèles Deep Learning optimisés

---

## 📦 Sources de Données Disponibles

### 1. **TCIA (The Cancer Imaging Archive)**
- 🏥 Plus grande archive publique d'imagerie médicale
- 📊 100+ collections disponibles
- 🔬 Domaines: Cancer, Neurologie, Radiologie
- 💾 Datasets DICOM natifs

**Datasets Recommandés:**
```python
# Nodules pulmonaires (Cancer du poumon)
LIDC-IDRI: 1,010 patients | 124 GB | CT

# Glioblastome (Tumeurs cérébrales)
TCGA-GBM: 262 patients | 50 GB | MRI

# COVID-19 thoracique
COVID-19-AR: 201 patients | 15 GB | CT
```

### 2. **Kaggle Medical Imaging**
- 🏆 Datasets de compétitions + communauté
- 📈 Datasets avec labels haute qualité
- ⚡ Téléchargement rapide via API

**Datasets Recommandés:**
```python
# Brain MRI Segmentation
mateuszbuda/lgg-mri-segmentation
3,929 images | 1.5 GB | MRI + masks

# Chest X-Ray Pneumonia
paultimothymooney/chest-xray-pneumonia
5,863 images | 2.2 GB | X-Ray

# COVID-19 Radiography
tawsifurrahman/covid19-radiography-database
21,165 images | 1.2 GB | X-Ray
```

### 3. **NIH ChestX-ray14**
- 🫁 112,120 radiographies thoraciques
- 🏥 30,805 patients uniques
- 🏷️ 14 pathologies labelisées
- 💾 42 GB (PNG format)

**Pathologies:**
```
1. Atelectasis      8. Pneumothorax
2. Cardiomegaly     9. Consolidation
3. Effusion         10. Edema
4. Infiltration     11. Emphysema
5. Mass             12. Fibrosis
6. Nodule           13. Pleural Thickening
7. Pneumonia        14. Hernia
```

---

## 🚀 Installation

### Prérequis

```bash
Python >= 3.9
CUDA >= 11.7 (pour GPU)
```

### Installation des dépendances

```powershell
cd C:\Users\ghali\irmsia\grpc-deeplearning\data_pipeline

# Installer les dépendances
pip install -r requirements.txt

# Pour Kaggle (optionnel)
pip install kaggle
# Configurer API key: https://www.kaggle.com/docs/api
```

---

## 📖 Guide de Démarrage Rapide

### Option 1: Menu Interactif (Recommandé)

```powershell
python data_pipeline_orchestrator.py
```

**Menu complet:**
```
📥 1. Télécharger des datasets
📊 2. Gérer les datasets
🧠 3. Entraîner un modèle
📚 4. Documentation
```

### Option 2: Utilisation Programmatique

#### 1️⃣ Télécharger un Dataset

**Depuis TCIA:**
```python
from collectors.tcia_collector import TCIACollector

collector = TCIACollector(output_dir="datasets/tcia")

# Lister les collections
collections = collector.list_available_collections()

# Télécharger une collection (10 premiers patients)
collector.download_collection(
    collection_name="COVID-19-AR",
    max_patients=10,
    modality="CT"
)
```

**Depuis Kaggle:**
```python
from collectors.kaggle_collector import KaggleCollector

collector = KaggleCollector(output_dir="datasets/kaggle")

# Rechercher des datasets
datasets = collector.search_datasets("brain mri")

# Télécharger
collector.download_dataset("mateuszbuda/lgg-mri-segmentation")
```

**Depuis NIH:**
```python
from collectors.nih_collector import NIHCollector

collector = NIHCollector(output_dir="datasets/nih")

# Télécharger les labels
collector.download_labels()

# Parser et créer splits
splits = collector.create_training_split()
```

#### 2️⃣ Organiser et Indexer

```python
from processors.dataset_manager import DatasetManager

manager = DatasetManager(base_dir="datasets")

# Scanner un répertoire
manager.scan_directory(
    directory="datasets/kaggle/brain_mri",
    dataset_name="brain_mri"
)

# Créer des splits train/val/test
splits = manager.create_train_val_test_split(
    dataset_name="brain_mri",
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15
)

# Voir les statistiques
stats = manager.get_dataset_statistics("brain_mri")
```

#### 3️⃣ Entraîner un Modèle

```python
from training.training_pipeline import TrainingPipeline, create_default_model

# Créer le modèle
model = create_default_model(num_classes=2)

# Créer le pipeline
pipeline = TrainingPipeline(
    model=model,
    train_csv="datasets/brain_mri/splits/train.csv",
    val_csv="datasets/brain_mri/splits/val.csv",
    output_dir="training_outputs"
)

# Entraîner
pipeline.train(num_epochs=50)
```

---

## 🔧 Utilisation en Ligne de Commande

### Collecter des Données

**TCIA:**
```powershell
# Voir les datasets recommandés
python collectors/tcia_collector.py --recommended

# Lister toutes les collections
python collectors/tcia_collector.py --list

# Télécharger une collection
python collectors/tcia_collector.py --download COVID-19-AR --max-patients 10
```

**Kaggle:**
```powershell
# Voir les datasets recommandés
python collectors/kaggle_collector.py --recommended

# Rechercher
python collectors/kaggle_collector.py --search "brain tumor"

# Télécharger
python collectors/kaggle_collector.py --download mateuszbuda/lgg-mri-segmentation
```

**NIH:**
```powershell
# Voir les datasets recommandés
python collectors/nih_collector.py --recommended

# Télécharger les labels
python collectors/nih_collector.py --download-labels

# Créer un split
python collectors/nih_collector.py --create-split
```

### Gérer les Datasets

```powershell
# Scanner un répertoire
python processors/dataset_manager.py --scan datasets/kaggle/brain_mri --dataset-name brain_mri

# Créer un split
python processors/dataset_manager.py --create-split brain_mri

# Voir le résumé
python processors/dataset_manager.py --summary
```

### Entraîner un Modèle

```powershell
python training/training_pipeline.py \
    --train-csv datasets/brain_mri/splits/train.csv \
    --val-csv datasets/brain_mri/splits/val.csv \
    --num-classes 2 \
    --epochs 50
```

---

## 📊 Workflow Complet: Exemple Pratique

### Scénario: Détection de Pneumonie sur X-Rays

```powershell
# 1. Télécharger le dataset Kaggle
python collectors/kaggle_collector.py --download paultimothymooney/chest-xray-pneumonia

# 2. Indexer le dataset
python processors/dataset_manager.py \
    --scan datasets/kaggle/paultimothymooney_chest-xray-pneumonia \
    --dataset-name pneumonia

# 3. Créer les splits
python processors/dataset_manager.py --create-split pneumonia

# 4. Entraîner le modèle
python training/training_pipeline.py \
    --train-csv datasets/pneumonia/splits/train.csv \
    --val-csv datasets/pneumonia/splits/val.csv \
    --num-classes 2 \
    --epochs 30

# 5. Résultats disponibles dans:
#    training_outputs/run_YYYYMMDD_HHMMSS/
#    - best_model.pth
#    - training_curves.png
#    - training_history.json
```

---

## 📁 Structure du Pipeline

```
data_pipeline/
├── collectors/               # Téléchargement de datasets
│   ├── tcia_collector.py    # The Cancer Imaging Archive
│   ├── kaggle_collector.py  # Kaggle datasets
│   └── nih_collector.py     # NIH ChestX-ray14
│
├── processors/              # Préparation des données
│   └── dataset_manager.py   # Indexation, splits, export
│
├── training/                # Entraînement
│   └── training_pipeline.py # Pipeline complet
│
├── datasets/                # Données téléchargées (créé auto)
│   ├── tcia/
│   ├── kaggle/
│   ├── nih/
│   └── dataset_index.json  # Index central
│
├── training_outputs/        # Modèles entraînés (créé auto)
│   └── run_YYYYMMDD_HHMMSS/
│       ├── best_model.pth
│       ├── training_curves.png
│       └── training_history.json
│
└── data_pipeline_orchestrator.py  # Menu interactif
```

---

## 🎓 Datasets Recommandés par Use Case

### 🧠 Neurologie (Brain Imaging)

| Dataset | Source | Images | Size | Format | Pathologie |
|---------|--------|--------|------|--------|-----------|
| TCGA-GBM | TCIA | 262 patients | 50 GB | DICOM | Glioblastome |
| TCGA-LGG | TCIA | 199 patients | 40 GB | DICOM | Gliome bas grade |
| Brain MRI Segmentation | Kaggle | 3,929 | 1.5 GB | DICOM + masks | Gliome |

### 🫁 Thoracique (Chest Imaging)

| Dataset | Source | Images | Size | Format | Pathologie |
|---------|--------|--------|------|--------|-----------|
| NIH ChestX-ray14 | NIH | 112,120 | 42 GB | PNG | 14 pathologies |
| LIDC-IDRI | TCIA | 1,010 patients | 124 GB | DICOM | Nodules pulmonaires |
| Chest X-Ray Pneumonia | Kaggle | 5,863 | 2.2 GB | JPG | Pneumonie |
| COVID-19 Radiography | Kaggle | 21,165 | 1.2 GB | PNG | COVID-19 |

### 🦴 Autres Domaines

| Dataset | Source | Images | Size | Pathologie |
|---------|--------|--------|------|-----------|
| RSNA Pneumonia | Kaggle Comp | 30,000 | 25 GB | Pneumonie |
| RSNA Hemorrhage | Kaggle Comp | 752,803 | 70 GB | Hémorragie IC |
| RSNA Breast Cancer | Kaggle Comp | 54,706 | 300 GB | Cancer du sein |

---

## 🔥 Fonctionnalités Avancées

### 1. Fusion de Datasets

```python
manager = DatasetManager()

# Fusionner plusieurs datasets
manager.merge_datasets(
    dataset_names=["brain_mri_1", "brain_mri_2", "brain_mri_3"],
    output_name="brain_mri_combined"
)
```

### 2. Filtrage par Pathologie

```python
# NIH - Filtrer uniquement les pneumonies
df = nih_collector.parse_labels()
pneumonia_df = df[df['Pneumonia'] == 1]
```

### 3. Export pour Frameworks Externes

```python
# Exporter pour PyTorch, TensorFlow, etc.
manager.export_for_training(
    dataset_name="pneumonia",
    split="train",
    output_format="json"  # ou "csv", "txt"
)
```

### 4. Augmentation de Données

Le `TrainingPipeline` inclut automatiquement:
- Rotation aléatoire
- Flip horizontal/vertical
- Zoom aléatoire
- Bruit gaussien
- Ajustement de contraste

---

## 📈 Résultats d'Entraînement

Après entraînement, vous obtenez:

```
training_outputs/run_20231202_150000/
├── best_model.pth              # Meilleur modèle (val loss minimale)
├── final_model.pth             # Modèle final
├── checkpoint_epoch_10.pth     # Checkpoints intermédiaires
├── training_curves.png         # Courbes Loss/Accuracy
└── training_history.json       # Historique complet
```

**training_history.json:**
```json
{
  "train_loss": [0.8, 0.6, 0.4, ...],
  "val_loss": [0.7, 0.5, 0.3, ...],
  "train_acc": [60, 70, 85, ...],
  "val_acc": [65, 75, 88, ...]
}
```

---

## 🔧 Configuration Avancée

### Custom Training Configuration

```python
# Modifier les hyperparamètres
pipeline = TrainingPipeline(
    model=model,
    train_csv="train.csv",
    val_csv="val.csv"
)

# Modifier optimizer
pipeline.optimizer = torch.optim.SGD(
    model.parameters(),
    lr=0.01,
    momentum=0.9
)

# Modifier loss
pipeline.criterion = nn.BCEWithLogitsLoss()

# Entraîner
pipeline.train(num_epochs=100)
```

---

## ❓ FAQ

### Q: Combien d'espace disque nécessaire?

**Exemples:**
- **Petit projet (test):** 5-10 GB
  - Brain MRI Segmentation (1.5 GB)
  - COVID-19 Radiography (1.2 GB)
  
- **Projet moyen:** 50-100 GB
  - TCGA-GBM (50 GB)
  - NIH ChestX-ray (42 GB)

- **Grand projet:** 200+ GB
  - LIDC-IDRI (124 GB)
  - RSNA Competitions (70-300 GB)

### Q: Quel GPU pour l'entraînement?

**Minimum:** NVIDIA GTX 1060 (6GB VRAM)  
**Recommandé:** RTX 3060+ (12GB VRAM)  
**Optimal:** RTX 4090 / A100 (24+ GB VRAM)

**Sans GPU:** CPU possible mais ~10x plus lent

### Q: Temps de téléchargement?

**Dépend de votre connexion:**
- 10 GB @ 100 Mbps: ~15 min
- 50 GB @ 100 Mbps: ~1h15
- 124 GB @ 100 Mbps: ~3h

**Conseil:** Commencez par de petits datasets pour tester!

### Q: Format DICOM vs PNG/JPG?

**DICOM (Natif):**
- ✅ Préserve 16-bit (65,536 nuances)
- ✅ Métadonnées médicales
- ✅ +5-10% précision diagnostique
- ⚠️ Fichiers plus lourds

**PNG/JPG (Converti):**
- ✅ Fichiers plus légers
- ✅ Compatible partout
- ⚠️ 8-bit seulement (256 nuances)
- ⚠️ Perte de métadonnées

**Recommandation:** DICOM pour training, PNG pour inference rapide

---

## 🆘 Support & Dépannage

### Erreur: "Kaggle API not configured"

```powershell
# 1. Créer compte Kaggle
# 2. Générer API token: https://www.kaggle.com/account
# 3. Placer kaggle.json dans:
#    Windows: C:\Users\<user>\.kaggle\kaggle.json
#    Linux: ~/.kaggle/kaggle.json

# 4. Tester
kaggle datasets list
```

### Erreur: "CUDA out of memory"

```python
# Réduire le batch size
pipeline.train_loader = DataLoader(
    pipeline.train_dataset,
    batch_size=8,  # Au lieu de 32
    ...
)
```

### Erreur: "DICOM file not found"

```python
# Vérifier les chemins dans le CSV
df = pd.read_csv("train.csv")
print(df['path'].head())

# Les chemins doivent être relatifs à base_dir
# ou absolus
```

---

## 📚 Ressources Externes

**TCIA:**
- Site: https://www.cancerimagingarchive.net/
- API: https://wiki.cancerimagingarchive.net/display/Public/TCIA+Programmatic+Interface

**Kaggle:**
- Site: https://www.kaggle.com/datasets
- API: https://github.com/Kaggle/kaggle-api

**NIH:**
- ChestX-ray14: https://nihcc.app.box.com/v/ChestXray-NIHCC
- Paper: https://arxiv.org/abs/1705.02315

**MONAI (Medical AI):**
- Docs: https://docs.monai.io/
- Tutorials: https://github.com/Project-MONAI/tutorials

---

## 📄 License

Ce pipeline est fourni pour usage éducatif et recherche.

**Note:** Chaque dataset a sa propre license. Consultez les sources pour les conditions d'utilisation.

---

## 🙏 Crédits

- **TCIA:** The Cancer Imaging Archive
- **NIH:** National Institutes of Health
- **Kaggle:** Community datasets
- **MONAI:** Medical Open Network for AI

---

## 📞 Contact

Pour questions et support:
- 📧 Email: [votre email]
- 💬 Issues: [GitHub repo]

---

**✨ Bon entraînement! 🚀**

