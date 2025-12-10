# 📊 Guide de Structuration et Organisation des Datasets

**Système complet pour organiser vos datasets médicaux pour un training efficace**

---

## 🎯 Vue d'Ensemble

Ce système vous permet de:
- ✅ Analyser et restructurer automatiquement vos datasets
- ✅ Détecter automatiquement les classes (ex: tumeur/normal via masques)
- ✅ Créer des splits équilibrés train/val/test
- ✅ Gérer plusieurs datasets simultanément
- ✅ Entraîner facilement avec les datasets organisés

---

## 🚀 Workflow Complet

### Étape 1: Restructurer un Dataset

**Pour Brain MRI (Automatique):**

```powershell
python auto_restructure_brain_mri.py
```

**Résultat:**
```
datasets/organized/brain_mri/
├── metadata.json                    # Informations du dataset
└── splits/
    ├── train.csv                    # 70% des données
    ├── val.csv                      # 15% des données
    └── test.csv                     # 15% des données
```

---

### Étape 2: Entraîner avec Dataset Organisé

```powershell
python train_with_organized_dataset.py
```

Le script va:
1. Lister les datasets disponibles
2. Vous laisser choisir
3. Configurer automatiquement le training
4. Afficher les statistiques
5. Lancer l'entraînement

---

## 📂 Structure des Fichiers CSV

### Format du CSV Structuré

```csv
image_path,mask_path,patient_id,has_tumor,label
kaggle/.../TCGA_CS_4941/.../image.tif,kaggle/.../TCGA_CS_4941/.../image_mask.tif,TCGA_CS_4941,1,tumor
kaggle/.../TCGA_CS_4942/.../image.tif,,TCGA_CS_4942,0,no_tumor
```

**Colonnes:**
- `image_path`: Chemin relatif vers l'image
- `mask_path`: Chemin vers le mask (optionnel)
- `patient_id`: ID du patient
- `has_tumor`: 1 ou 0 (pour classification binaire)
- `label`: Nom de la classe (ex: "tumor", "no_tumor", "covid", "normal")

---

## 🔧 Scripts Disponibles

### 1. **auto_restructure_brain_mri.py** (Automatique)

**Usage:**
```powershell
python auto_restructure_brain_mri.py
```

**Fonctions:**
- Scan automatique de tous les patients
- Détection des tumeurs via masques
- Création de splits équilibrés par patient
- Génération de metadata
- Prêt en 1 clic

**Temps:** ~2-5 minutes

---

### 2. **restructure_datasets.py** (Menu Interactif)

**Usage:**
```powershell
python restructure_datasets.py
```

**Menu:**
```
1. Analyser et structurer Brain MRI
2. Organiser un dataset par classes
3. Créer un subset équilibré
4. Lister les datasets organisés
5. Quitter
```

**Fonctions:**
- Analyse personnalisée
- Création de subsets équilibrés
- Gestion multi-datasets

---

### 3. **train_with_organized_dataset.py** (Training)

**Usage:**
```powershell
python train_with_organized_dataset.py
```

**Workflow:**
1. Sélection du dataset
2. Configuration (epochs)
3. Vérifications automatiques
4. Training avec statistiques
5. Résultats et analyse

---

## 📊 Metadata (metadata.json)

Chaque dataset organisé contient un fichier `metadata.json`:

```json
{
  "dataset_name": "brain_mri",
  "description": "Brain MRI Low Grade Glioma Segmentation",
  "source": "Kaggle - mateuszbuda/lgg-mri-segmentation",
  "total_images": 7858,
  "total_patients": 110,
  "num_classes": 2,
  "classes": ["no_tumor", "tumor"],
  "class_distribution": {
    "no_tumor": 3929,
    "tumor": 3929
  },
  "splits": {
    "train": {
      "total": 5500,
      "tumor": 2750,
      "no_tumor": 2750
    },
    "val": {
      "total": 1179,
      "tumor": 590,
      "no_tumor": 589
    },
    "test": {
      "total": 1179,
      "tumor": 589,
      "no_tumor": 590
    }
  },
  "image_format": "TIFF",
  "modality": "MRI",
  "files": {
    "train_csv": "organized/brain_mri/splits/train.csv",
    "val_csv": "organized/brain_mri/splits/val.csv",
    "test_csv": "organized/brain_mri/splits/test.csv"
  }
}
```

---

## 🎯 Cas d'Usage

### Cas 1: Dataset avec Masques (Segmentation)

**Exemple:** Brain MRI

**Workflow:**
```powershell
# 1. Télécharger
python collectors/kaggle_collector.py --download mateuszbuda/lgg-mri-segmentation

# 2. Restructurer (détecte les tumeurs automatiquement)
python auto_restructure_brain_mri.py

# 3. Entraîner
python train_with_organized_dataset.py
```

**Résultat:** Classification tumeur/normal basée sur présence de masque

---

### Cas 2: Dataset Multi-Classes

**Exemple:** COVID-19 Radiography (4 classes)

**Workflow:**
```powershell
# 1. Télécharger
python collectors/kaggle_collector.py --download tawsifurrahman/covid19-radiography-database

# 2. Organiser manuellement
python restructure_datasets.py
# Menu → 2. Organiser un dataset

# 3. Entraîner
python train_with_organized_dataset.py
```

---

### Cas 3: Créer un Subset Équilibré

Si votre dataset est déséquilibré (ex: 10,000 normaux, 100 tumeurs):

```powershell
python restructure_datasets.py
# Menu → 3. Créer un subset équilibré
# Spécifier: 100 échantillons par classe
```

**Résultat:** Dataset équilibré (100 normaux, 100 tumeurs)

---

## 💡 Bonnes Pratiques

### 1. **Split par Patient (Medical Data)**

✅ **BON:**
```python
# Split par patient (évite data leakage)
patients = df['patient_id'].unique()
train_patients, test_patients = train_test_split(patients, ...)
train_df = df[df['patient_id'].isin(train_patients)]
```

❌ **MAUVAIS:**
```python
# Split direct (images du même patient dans train ET test)
train_df, test_df = train_test_split(df, ...)
```

### 2. **Équilibrage des Classes**

✅ **Important pour:**
- Classification binaire (tumeur/normal)
- Détection de pathologies rares
- Éviter le biais du modèle

**Solution:** Utiliser l'option "subset équilibré"

### 3. **Validation du Dataset**

Vérifiez toujours:
```python
# Distribution des classes
print(df['label'].value_counts())

# Images par patient
print(df.groupby('patient_id').size().describe())

# Vérifier que les fichiers existent
for path in df['image_path']:
    assert Path(path).exists()
```

---

## 📈 Statistiques Typiques

### Dataset Bien Structuré

```
✅ BON Dataset:
   Total: 10,000 images
   Classes: Équilibrées (49-51%)
   Patients: 200
   Images/patient: 50 ± 20
   Split: 70/15/15
   Validation: Tous les fichiers existent
```

### Dataset Problématique

```
⚠️ PROBLÈME:
   Total: 10,000 images
   Classes: Déséquilibrées (95% normal, 5% tumeur)  👈 Problème!
   Patients: Non pris en compte  👈 Data leakage!
   Split: 80/20 (pas de validation)  👈 Problème!
```

**Solution:** Restructurer avec les scripts fournis

---

## 🔍 Debugging

### Problème: "Aucune image trouvée"

**Cause:** Mauvais chemin ou extensions

**Solution:**
```python
# Vérifier le chemin
print(f"Base dir: {Path('datasets/kaggle/...').exists()}")

# Lister les fichiers
for file in Path('datasets/...').rglob('*.tif'):
    print(file)
```

### Problème: "Classes déséquilibrées"

**Solution:**
```powershell
# Créer un subset équilibré
python restructure_datasets.py
# Menu → 3
```

### Problème: "Val Accuracy = 0%"

**Causes possibles:**
1. Une seule classe dans le dataset
2. Labels incorrects
3. Problème de chargement d'images

**Solution:**
```python
# Vérifier les labels
df = pd.read_csv('train.csv')
print(df['label'].value_counts())

# Vérifier une image
from PIL import Image
img = Image.open(df.iloc[0]['image_path'])
print(img.mode, img.size)
```

---

## 📁 Structure Complète d'un Projet

```
data_pipeline/
├── datasets/
│   ├── kaggle/
│   │   └── mateuszbuda_lgg-mri-segmentation/  # Dataset brut
│   ├── organized/                              # Datasets structurés
│   │   ├── brain_mri/
│   │   │   ├── metadata.json
│   │   │   └── splits/
│   │   │       ├── train.csv
│   │   │       ├── val.csv
│   │   │       └── test.csv
│   │   └── covid19/
│   │       ├── metadata.json
│   │       └── splits/...
│   └── dataset_index.json                      # Index global
│
├── training_outputs/
│   ├── training_brain_mri/
│   │   └── run_20251203_100000/
│   │       ├── best_model.pth
│   │       ├── training_curves.png
│   │       └── training_history.json
│   └── training_covid19/...
│
├── auto_restructure_brain_mri.py              # Script auto Brain MRI
├── restructure_datasets.py                     # Menu interactif
├── train_with_organized_dataset.py            # Training
└── DATASET_ORGANIZATION_GUIDE.md              # Ce guide
```

---

## 🎓 Exemples Pratiques

### Exemple 1: Workflow Complet Brain MRI

```powershell
# 1. Télécharger (une fois)
python collectors/kaggle_collector.py --download mateuszbuda/lgg-mri-segmentation

# 2. Restructurer (une fois)
python auto_restructure_brain_mri.py

# 3. Vérifier
python -c "import json; print(json.load(open('datasets/organized/brain_mri/metadata.json', 'r')))"

# 4. Entraîner (plusieurs fois avec différents paramètres)
python train_with_organized_dataset.py
# Choisir: brain_mri
# Epochs: 20

# 5. Résultats
# Voir: training_outputs/training_brain_mri/run_*/
```

### Exemple 2: Créer un Nouveau Dataset

```python
# create_custom_dataset.py
import pandas as pd
from pathlib import Path

# Vos données
data = []
for img_path in Path("my_images").glob("*.png"):
    # Votre logique pour déterminer la classe
    label = "class_a" if "a" in img_path.name else "class_b"
    
    data.append({
        'image_path': str(img_path),
        'label': label,
        'has_tumor': 1 if label == "class_a" else 0
    })

df = pd.DataFrame(data)
df.to_csv("datasets/organized/my_dataset_structured.csv", index=False)

# Puis utiliser restructure_datasets.py
```

---

## 🆘 Support

### Documentation Complète
- **README.md** - Guide principal du pipeline
- **QUICK_START.md** - Démarrage rapide
- **DATASETS_SUMMARY.md** - Liste des datasets disponibles
- **DATASET_ORGANIZATION_GUIDE.md** - Ce guide

### Scripts de Test
- `test_pipeline.py` - Test complet du pipeline
- `quick_test_training.py` - Test rapide (2 epochs)
- `test_training_workflow.py` - Test détaillé (5 epochs)

---

## ✅ Checklist avant Training

- [ ] Dataset téléchargé
- [ ] Dataset restructuré (CSV créés)
- [ ] Metadata.json présent
- [ ] Splits créés (train/val/test)
- [ ] Classes équilibrées (ou subset créé)
- [ ] Chemins vérifiés (fichiers existent)
- [ ] Format d'images supporté (TIFF/PNG/JPG/DICOM)

---

**🎉 Votre système de gestion de datasets est prêt!**

Utilisez `python auto_restructure_brain_mri.py` puis `python train_with_organized_dataset.py` pour commencer!

