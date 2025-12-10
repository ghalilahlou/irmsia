# 🔍 Guide Complet - Détecteur d'Anomalies Généraliste

**Système de détection d'anomalies multi-organes avec apprentissage semi-supervisé**

---

## 🎯 Objectif

Développer un **détecteur d'anomalies généraliste** capable de:
- ✅ Détecter des anomalies sur **tout le corps humain**
- ✅ Fonctionner avec **données étiquetées ET non-étiquetées**
- ✅ Combiner approches **supervisée + non-supervisée**
- ✅ Supporter multiple **modalités** (MRI, CT, X-Ray, etc.)
- ✅ Détecter **anomalies connues** (tumeur, infection) ET **inconnues**

---

## 📊 Architecture du Système

### 1. **Organisation des Données**

```
datasets/anomaly_detection/
├── brain_mri/                    # Dataset cerveau
│   ├── labeled.csv               # Images avec tumeurs (étiquetées)
│   ├── unlabeled.csv             # Images normales (non-étiquetées)
│   ├── metadata.json             # Métadonnées
│   ├── training_config.json      # Configuration
│   └── splits/
│       ├── train.csv             # 70%
│       ├── val.csv               # 15%
│       └── test.csv              # 15%
│
├── chest_xray/                   # Dataset thorax (à ajouter)
│   └── ...
│
└── abdomen/                      # Dataset abdomen (à ajouter)
    └── ...
```

### 2. **Modèles d'IA**

#### **A. Supervisé (Anomalies Connues)**
```python
SupervisedAnomalyClassifier
- Backbone: EfficientNet-B0
- Input: Images étiquetées
- Output: Classification multi-classes
- Classes: [normal, tumor, infection, hemorrhage, ...]
```

#### **B. Non-Supervisé (Anomalies Inconnues)**
```python
VariationalAutoencoder (VAE)
- Encoder: CNN -> Latent space (512-dim)
- Decoder: Latent -> Image reconstruction
- Input: Images normales (non-étiquetées)
- Output: Anomaly score (reconstruction error)
```

#### **C. Hybride (Ensemble)**
```python
HybridAnomalyDetector
- Combine Supervisé + VAE
- Score final = (supervised_prob + anomaly_score) / 2
- Détecte anomalies connues ET inconnues
```

---

## 🚀 Workflow Complet

### Étape 1: Organisation des Données Existantes

#### **Brain MRI (Déjà fait!)**
```powershell
python auto_organize_anomaly_brain_mri.py
```

**Résultat:**
- 3,929 images organisées
- Splits train/val/test créés
- Metadata et config générés

#### **Ajouter d'Autres Datasets (Multi-Organes)**

```powershell
# Télécharger COVID-19 (Poumons)
python collectors/kaggle_collector.py --download tawsifurrahman/covid19-radiography-database

# Organiser pour anomaly detection
python organize_for_anomaly_detection.py
# Menu → 5 (Workflow complet)
# Spécifier le CSV du COVID-19
```

---

### Étape 2: Training du Détecteur

#### **Option A: Training Supervisé Uniquement**

Pour anomalies connues (si vous avez beaucoup de données étiquetées):

```powershell
python train_anomaly_detector.py --phase supervised --epochs 30
```

**Avantages:**
- ✅ Haute précision sur anomalies connues
- ✅ Plus rapide à entraîner

**Limitations:**
- ❌ Ne détecte que les anomalies vues pendant training
- ❌ Requiert beaucoup de données étiquetées

---

#### **Option B: Training Non-Supervisé (VAE)**

Pour apprendre la "normalité" et détecter toute déviation:

```powershell
python train_anomaly_detector.py --phase unsupervised --epochs 50
```

**Avantages:**
- ✅ Détecte anomalies inconnues/nouvelles
- ✅ Fonctionne avec données non-étiquetées

**Limitations:**
- ❌ Peut avoir des faux positifs
- ❌ Moins précis sur type d'anomalie

---

#### **Option C: Training Hybride (Recommandé)**

Combine les deux approches:

```powershell
python train_anomaly_detector.py --phase all --epochs 30
```

**Avantages:**
- ✅ Meilleure détection (connu + inconnu)
- ✅ Utilise toutes les données (étiquetées + non-étiquetées)
- ✅ Plus robuste

**Workflow:**
1. Train supervisé sur données étiquetées (30 epochs)
2. Train VAE sur données non-étiquetées (50 epochs)
3. Combine les deux pour prédiction finale

---

### Étape 3: Utilisation du Détecteur

```python
# Charger le modèle
from models.anomaly_detector import HybridAnomalyDetector

model = HybridAnomalyDetector()
model.load_state_dict(torch.load('training_outputs/.../hybrid_model.pth'))
model.eval()

# Prédiction
import torch
from PIL import Image

img = Image.open('patient_scan.tif').convert('L')
img_tensor = transforms.ToTensor()(img).unsqueeze(0)

result = model.detect_anomaly(img_tensor, threshold=0.5)

print(f"Anomalie détectée: {result['is_anomaly']}")
print(f"Type: {ANOMALY_CLASSES[result['predicted_class']]}")
print(f"Confiance: {result['confidence']:.2f}")
print(f"Score d'anomalie: {result['anomaly_score']:.2f}")
```

---

## 📈 Datasets pour Système Multi-Organes

### **Datasets Recommandés par Région**

#### 1. **Cerveau** (✅ Déjà configuré)
- Brain MRI (LGG Segmentation) - 3,929 images
- **Anomalies:** Gliomes, tumeurs

#### 2. **Poumons/Thorax** (À ajouter)
```powershell
# COVID-19 Radiography
python collectors/kaggle_collector.py --download tawsifurrahman/covid19-radiography-database
# Classes: COVID, Normal, Lung Opacity, Viral Pneumonia

# ChestX-ray14
python collectors/nih_collector.py --download chest-xray14
# 112,000+ images, 14 pathologies
```

#### 3. **Abdomen**
- Liver Tumor Dataset
- Kidney Stones X-Rays

#### 4. **Os/Squelette**
- Bone Fracture Detection
- MURA (Musculoskeletal Radiographs)

---

## 🛠️ Scripts Disponibles

### 1. **auto_organize_anomaly_brain_mri.py**
Organisation automatique du Brain MRI pour anomaly detection

### 2. **organize_for_anomaly_detection.py**
Menu interactif pour organiser tout type de dataset

**Fonctionnalités:**
- Classification automatique étiqueté/non-étiqueté
- Détection région anatomique (cerveau, poumons, etc.)
- Détection modalité (MRI, CT, X-Ray)
- Création datasets équilibrés
- Génération de configurations

### 3. **train_anomaly_detector.py**
Training du détecteur d'anomalies

**Arguments:**
```
--phase supervised|unsupervised|hybrid|all
--epochs 30
--train-csv path/to/train.csv
--val-csv path/to/val.csv
--output training_outputs/anomaly_detection
```

### 4. **models/anomaly_detector.py**
Modèles de détection d'anomalies

**Classes:**
- `SupervisedAnomalyClassifier`: Classification d'anomalies connues
- `VariationalAutoencoder`: Détection d'anomalies par reconstruction
- `HybridAnomalyDetector`: Système ensemble

---

## 💡 Stratégies d'Apprentissage

### **A. Données Majoritairement Étiquetées**

Si vous avez >80% de données étiquetées:

```
1. Training supervisé (80% des données)
2. VAE sur 20% non-étiquetées (pour détecter inconnu)
3. Ensemble léger (poids 80/20)
```

### **B. Données Majoritairement Non-Étiquetées**

Si vous avez <20% de données étiquetées:

```
1. VAE sur données non-étiquetées (apprend normalité)
2. Fine-tune avec les données étiquetées
3. Ensemble équilibré (50/50)
```

### **C. Mix Équilibré**

```
1. Training supervisé sur étiquetées
2. VAE sur non-étiquetées
3. Ensemble optimisé
```

---

## 📊 Métriques d'Évaluation

### **Pour Classification (Supervisé)**
- Accuracy
- Precision/Recall par classe
- F1-Score
- ROC-AUC
- Confusion Matrix

### **Pour Anomaly Detection (Non-Supervisé)**
- Reconstruction Error (MSE)
- KL Divergence
- Anomaly Score Distribution
- True Positive Rate @ Fixed False Positive Rate

### **Pour Ensemble (Hybride)**
- Detection Rate (anomalies détectées / total anomalies)
- False Alarm Rate
- F1-Score global
- Robustesse aux anomalies inconnues

---

## 🔧 Configuration Avancée

### **Ajuster le Seuil d'Anomalie**

```python
# Dans train_anomaly_detector.py ou pendant inference
anomaly_threshold = 0.5  # Default

# Plus sensible (détecte plus, mais plus de faux positifs)
anomaly_threshold = 0.3

# Plus conservateur (détecte moins, mais plus précis)
anomaly_threshold = 0.7
```

### **Optimiser la Mémoire GPU**

Si "CUDA out of memory":

```python
# Dans train_anomaly_detector.py
batch_size = 8  # Réduire
# Ou utiliser EfficientNet-B0 au lieu de B4
```

### **Multi-GPU Training**

```python
model = nn.DataParallel(model)  # Utilise plusieurs GPUs
```

---

## 🎯 Roadmap Système Multi-Organes

### Phase 1: Brain (✅ Fait)
- Brain MRI organisé
- Modèle supervisé créé
- VAE implémenté

### Phase 2: Chest/Lungs (Suivant)
```
1. Télécharger COVID-19 dataset
2. Organiser pour anomaly detection
3. Entraîner modèle spécifique poumons
4. Combiner avec modèle cerveau
```

### Phase 3: Abdomen
```
1. Collecter datasets abdominaux
2. Organiser et entraîner
3. Ajouter à l'ensemble
```

### Phase 4: Système Unifié
```
1. Router intelligent (détecte région anatomique)
2. Sélectionne modèle spécialisé approprié
3. Combine prédictions si nécessaire
```

---

## 🆘 Troubleshooting

### Problème: "CUDA out of memory"
**Solution:**
- Réduire batch_size
- Utiliser modèle plus petit (EfficientNet-B0)
- Réduire taille des images (224x224 → 192x192)

### Problème: "Val Accuracy = 0%"
**Solution:**
- Vérifier distribution des classes
- S'assurer que les labels sont corrects
- Augmenter learning rate si modèle n'apprend pas

### Problème: "High Reconstruction Error (VAE)"
**C'est normal!** VAE sur images normales devrait avoir:
- Erreur basse sur normales (~0.01-0.05)
- Erreur haute sur anomalies (>0.1)

---

## 📚 Documentation Complète

- **README.md** - Guide principal du pipeline
- **DATASET_ORGANIZATION_GUIDE.md** - Organisation datasets
- **ANOMALY_DETECTION_GUIDE.md** - Ce guide
- **QUICK_START.md** - Démarrage rapide

---

## ✅ Checklist pour Système Multi-Organes

- [x] Brain MRI organisé et prêt
- [ ] COVID-19/Chest X-Ray téléchargé
- [ ] Modèle cerveau entraîné (supervised)
- [ ] VAE entraîné sur images normales
- [ ] Modèle hybride testé
- [ ] Système étendu à poumons
- [ ] Système étendu à abdomen
- [ ] Router intelligent implémenté
- [ ] API gRPC pour inférence
- [ ] Intégration avec blockchain

---

**🎉 Votre système de détection d'anomalies est prêt à être développé!**

**Prochaines étapes:**
1. Tester training supervisé: `python train_anomaly_detector.py --phase supervised --epochs 10`
2. Ajouter dataset poumons
3. Créer router multi-organes

