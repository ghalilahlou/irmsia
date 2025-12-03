# Quick Start Guide - Data Pipeline 🚀

**Démarrez avec le pipeline de données en 10 minutes!**

---

## ⚡ Installation Ultra-Rapide (2 min)

```powershell
# 1. Aller dans le répertoire
cd C:\Users\ghali\irmsia\grpc-deeplearning\data_pipeline

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. (Optionnel) Configurer Kaggle
pip install kaggle
# Placer votre kaggle.json dans: C:\Users\ghali\.kaggle\kaggle.json
```

---

## 🎯 Scénario 1: Test Rapide avec Menu Interactif

### Temps estimé: 10 minutes

```powershell
# Lancer le menu interactif
python data_pipeline_orchestrator.py
```

**Workflow suggéré:**

1. **Menu Principal → 4. Documentation**
   - Voir les datasets recommandés
   - Choisir un petit dataset (~1-2 GB)

2. **Menu Principal → 1. Télécharger des datasets**
   - Sélectionner Kaggle
   - Télécharger "Brain MRI Segmentation" (1.5 GB)

3. **Menu Principal → 2. Gérer les datasets**
   - Scanner le répertoire téléchargé
   - Créer un split train/val/test

4. **Menu Principal → 3. Entraîner un modèle**
   - Fournir les CSV générés
   - Lancer l'entraînement

---

## 🧪 Scénario 2: Test avec un Mini-Dataset (5 min)

**Utilisons le dataset COVID-19 de Kaggle (1.2 GB, 21k images)**

```powershell
# 1. Télécharger
python collectors/kaggle_collector.py --download tawsifurrahman/covid19-radiography-database

# 2. Scanner
python processors/dataset_manager.py --scan "datasets/kaggle/tawsifurrahman_covid19-radiography-database" --dataset-name covid19

# 3. Créer split
python processors/dataset_manager.py --create-split covid19

# 4. Voir le résumé
python processors/dataset_manager.py --summary
```

**Résultat:**
```
📊 Total Images: 21,165
📁 Datasets: covid19
   - Train: 70% (14,815 images)
   - Val: 15% (3,174 images)
   - Test: 15% (3,176 images)
```

---

## 🏥 Scénario 3: Projet Réel - Détection de Pneumonie

### Temps estimé: 1-2 heures (selon connexion)

**Dataset:** Chest X-Ray Pneumonia (5,863 images, 2.2 GB)

### Étape 1: Téléchargement (10-30 min)

```powershell
python collectors/kaggle_collector.py --download paultimothymooney/chest-xray-pneumonia
```

### Étape 2: Organisation (5 min)

```powershell
# Scanner le dataset
python processors/dataset_manager.py \
    --scan "datasets/kaggle/paultimothymooney_chest-xray-pneumonia" \
    --dataset-name pneumonia_xray

# Créer les splits
python processors/dataset_manager.py --create-split pneumonia_xray

# Vérifier
python processors/dataset_manager.py --summary
```

### Étape 3: Entraînement (30-60 min selon GPU)

```powershell
python training/training_pipeline.py \
    --train-csv "datasets/pneumonia_xray/splits/train.csv" \
    --val-csv "datasets/pneumonia_xray/splits/val.csv" \
    --num-classes 2 \
    --epochs 30
```

**Résultats attendus:**
- Accuracy: ~85-90%
- Modèle sauvegardé: `training_outputs/run_YYYYMMDD_HHMMSS/best_model.pth`
- Courbes: `training_curves.png`

### Étape 4: Évaluation

```python
# Charger le modèle
import torch
model = torch.load("training_outputs/run_*/best_model.pth")

# Inférence (voir training_pipeline.py)
```

---

## 🧠 Scénario 4: Projet Neurologie - Brain MRI

### Temps estimé: 30 min - 1h

**Dataset:** LGG MRI Segmentation (3,929 images, 1.5 GB)

```powershell
# 1. Télécharger
python collectors/kaggle_collector.py --download mateuszbuda/lgg-mri-segmentation

# 2. Préparer
python processors/dataset_manager.py \
    --scan "datasets/kaggle/mateuszbuda_lgg-mri-segmentation" \
    --dataset-name brain_mri_lgg

python processors/dataset_manager.py --create-split brain_mri_lgg

# 3. Entraîner
python training/training_pipeline.py \
    --train-csv "datasets/brain_mri_lgg/splits/train.csv" \
    --val-csv "datasets/brain_mri_lgg/splits/val.csv" \
    --num-classes 2 \
    --epochs 40
```

---

## 📊 Scénario 5: Grand Dataset - TCIA

### Temps estimé: Plusieurs heures (dataset lourd)

**⚠️ Recommandé uniquement si vous avez:**
- Beaucoup d'espace disque (50+ GB)
- Bonne connexion internet
- GPU puissant pour training

```powershell
# 1. Voir les collections disponibles
python collectors/tcia_collector.py --recommended

# 2. Télécharger COVID-19-AR (15 GB, 201 patients)
python collectors/tcia_collector.py --download COVID-19-AR --max-patients 50

# 3. Préparer
python processors/dataset_manager.py \
    --scan "datasets/tcia/COVID-19-AR" \
    --dataset-name covid_ct_tcia

python processors/dataset_manager.py --create-split covid_ct_tcia

# 4. Entraîner
python training/training_pipeline.py \
    --train-csv "datasets/covid_ct_tcia/splits/train.csv" \
    --val-csv "datasets/covid_ct_tcia/splits/val.csv" \
    --num-classes 2 \
    --epochs 50
```

---

## 🐍 Utilisation Programmatique (Python)

### Exemple Complet en Python

```python
# complete_workflow.py
from collectors.kaggle_collector import KaggleCollector
from processors.dataset_manager import DatasetManager
from training.training_pipeline import TrainingPipeline, create_default_model

# 1. Télécharger
print("📥 Téléchargement...")
kaggle = KaggleCollector()
kaggle.download_dataset("tawsifurrahman/covid19-radiography-database")

# 2. Organiser
print("🗂️ Organisation...")
manager = DatasetManager()
manager.scan_directory(
    directory="datasets/kaggle/tawsifurrahman_covid19-radiography-database",
    dataset_name="covid19"
)

# 3. Créer splits
print("✂️ Création des splits...")
splits = manager.create_train_val_test_split("covid19")

# 4. Entraîner
print("🧠 Entraînement...")
model = create_default_model(num_classes=3)  # COVID, Normal, Viral Pneumonia

pipeline = TrainingPipeline(
    model=model,
    train_csv="datasets/covid19/splits/train.csv",
    val_csv="datasets/covid19/splits/val.csv"
)

pipeline.train(num_epochs=30)

print("✅ Terminé!")
```

**Lancer:**
```powershell
python complete_workflow.py
```

---

## 📋 Checklist de Démarrage

### Avant de Commencer

- [ ] Python 3.9+ installé
- [ ] pip à jour (`python -m pip install --upgrade pip`)
- [ ] CUDA installé (si GPU disponible)
- [ ] Espace disque suffisant (min 10 GB)

### Installation

- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Kaggle API configurée (si utilisation Kaggle)
- [ ] Tests des imports (`python -c "import torch; import monai"`)

### Premier Test

- [ ] Menu interactif lance sans erreur
- [ ] Un petit dataset téléchargé avec succès
- [ ] Dataset indexé correctement
- [ ] Split créé avec succès
- [ ] Entraînement démarre (même 1 epoch)

---

## 🎯 Datasets Recommandés par Niveau

### 👶 Débutant (Test rapide)

| Dataset | Size | Time | Complexité |
|---------|------|------|-----------|
| COVID-19 Radiography (Kaggle) | 1.2 GB | 10 min | ⭐ |
| Brain MRI Segmentation (Kaggle) | 1.5 GB | 15 min | ⭐⭐ |

### 👨‍💻 Intermédiaire (Projet réel)

| Dataset | Size | Time | Complexité |
|---------|------|------|-----------|
| Chest X-Ray Pneumonia (Kaggle) | 2.2 GB | 30 min | ⭐⭐⭐ |
| COVID-19-AR (TCIA) | 15 GB | 1-2h | ⭐⭐⭐ |

### 🧑‍🔬 Avancé (Research)

| Dataset | Size | Time | Complexité |
|---------|------|------|-----------|
| NIH ChestX-ray14 | 42 GB | 3-5h | ⭐⭐⭐⭐ |
| LIDC-IDRI (TCIA) | 124 GB | 1 jour | ⭐⭐⭐⭐⭐ |

---

## ⚠️ Problèmes Courants

### 1. "Kaggle API not configured"

**Solution:**
```powershell
# 1. Aller sur: https://www.kaggle.com/account
# 2. Cliquer "Create New API Token"
# 3. Placer kaggle.json dans: C:\Users\ghali\.kaggle\
# 4. Vérifier: kaggle datasets list
```

### 2. "CUDA out of memory"

**Solution:**
```python
# Réduire batch_size dans training_pipeline.py:
batch_size=8  # Au lieu de 32
```

### 3. "Dataset directory not found"

**Solution:**
```powershell
# Vérifier les chemins
python processors/dataset_manager.py --summary

# Les chemins doivent exister et contenir des fichiers DICOM/images
```

### 4. "Import Error: No module named 'monai'"

**Solution:**
```powershell
pip install monai
# Ou réinstaller toutes les dépendances:
pip install -r requirements.txt --force-reinstall
```

---

## 💡 Conseils Pro

### 1. Commencez Petit
- Testez avec 1-2 GB avant de télécharger 100+ GB
- Utilisez `--max-patients` pour limiter les téléchargements TCIA

### 2. Surveillez l'Espace Disque
```powershell
# Windows
Get-PSDrive C | Select-Object Used,Free

# Voir la taille des datasets
python processors/dataset_manager.py --summary
```

### 3. Utilisez un SSD pour Training
- Accélère le chargement des images (~2x)
- Place datasets sur SSD si possible

### 4. Checkpoints Réguliers
- Le pipeline sauvegarde automatiquement tous les 10 epochs
- Vous pouvez reprendre si interruption

### 5. Augmentation de Données
```python
# Le pipeline inclut déjà:
- Rotation aléatoire
- Flip H/V
- Zoom
- Bruit gaussien
- Ajustement contraste
```

---

## 🎓 Prochaines Étapes

### Après votre Premier Modèle

1. **Évaluation Approfondie**
   - Matrice de confusion
   - ROC curves
   - Précision par classe

2. **Optimisation**
   - Hyperparameter tuning
   - Architecture différente
   - Transfer learning

3. **Intégration IRMSIA**
   - Connecter avec gRPC server
   - Intégration Blockchain
   - Interface web

4. **Production**
   - Export ONNX
   - Optimisation inference
   - Déploiement

---

## 📚 Ressources Utiles

**Documentation:**
- PyTorch: https://pytorch.org/docs/
- MONAI: https://docs.monai.io/
- Kaggle API: https://github.com/Kaggle/kaggle-api

**Tutoriels:**
- Medical Imaging DL: https://github.com/Project-MONAI/tutorials
- PyTorch Medical: https://pytorch.org/blog/medical-imaging/

**Papers:**
- NIH ChestX-ray14: https://arxiv.org/abs/1705.02315
- COVID-19 Detection: https://arxiv.org/abs/2003.13145

---

## 🚀 Vous êtes Prêt!

Choisissez un scénario ci-dessus et lancez-vous!

**Recommandation:**
- Première fois? → **Scénario 1** (Menu interactif)
- Déjà à l'aise? → **Scénario 3** (Pneumonie)
- Projet sérieux? → **Scénario 4** ou **5**

**Bonne chance! 🎉**

