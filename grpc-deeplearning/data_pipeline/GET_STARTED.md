# 🚀 GET STARTED - 5 Minutes

**Démarrez avec le Data Pipeline en moins de 5 minutes!**

---

## ⚡ Installation (2 min)

```powershell
# 1. Aller dans le répertoire
cd C:\Users\ghali\irmsia\grpc-deeplearning\data_pipeline

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Tester l'installation
python test_pipeline.py
```

**Attendez:** ✅ ALL TESTS PASSED!

---

## 🎮 Premier Lancement (1 min)

```powershell
python data_pipeline_orchestrator.py
```

**Vous verrez:**
```
====================================================================
IRMSIA DATA PIPELINE - MENU PRINCIPAL
====================================================================

📥 1. Télécharger des datasets
📊 2. Gérer les datasets
🧠 3. Entraîner un modèle
📚 4. Documentation & Datasets recommandés
❌ 5. Quitter
```

---

## 🧪 Premier Test (2 min)

### Option A: Menu Interactif

1. Choisir **4. Documentation**
2. Choisir **2. Datasets Kaggle recommandés**
3. Voir la liste des datasets
4. Retour → Choisir **1. Télécharger**
5. Choisir **2. Kaggle**
6. Choisir **3. COVID-19 Radiography**

### Option B: Ligne de Commande

```powershell
# Voir les datasets recommandés
python collectors/kaggle_collector.py --recommended

# Télécharger un petit dataset (1.2 GB)
python collectors/kaggle_collector.py --download tawsifurrahman/covid19-radiography-database
```

---

## 📚 Documentation

### Fichiers Principaux

1. **README.md** → Documentation complète (tout ce dont vous avez besoin)
2. **QUICK_START.md** → 5 scénarios prêts à l'emploi avec commandes
3. **DATASETS_SUMMARY.md** → Guide de 100+ datasets médicaux
4. **PROJET_DATA_PIPELINE.md** → Vue d'ensemble du projet

### Lecture Recommandée (5 min)

1. Lire **QUICK_START.md** → Scénario 1
2. Parcourir **DATASETS_SUMMARY.md** → Top 10 Recommandés
3. Lancer un workflow complet (30 min)

---

## 🎯 Workflows Rapides

### Workflow 1: Test avec Menu (10 min)

```powershell
python data_pipeline_orchestrator.py

# Suivre: Menu → Télécharger → Gérer → Entraîner
```

### Workflow 2: CLI Pneumonie (30-60 min)

```powershell
# 1. Télécharger (10 min)
python collectors/kaggle_collector.py --download paultimothymooney/chest-xray-pneumonia

# 2. Préparer (2 min)
python processors/dataset_manager.py --scan "datasets/kaggle/paultimothymooney_chest-xray-pneumonia" --dataset-name pneumonia
python processors/dataset_manager.py --create-split pneumonia

# 3. Entraîner (20-40 min selon GPU)
python training/training_pipeline.py --train-csv "datasets/pneumonia/splits/train.csv" --val-csv "datasets/pneumonia/splits/val.csv" --num-classes 2 --epochs 30
```

---

## ⚠️ Configuration Kaggle (Optionnel)

**Si vous voulez utiliser Kaggle:**

1. Créer compte: https://www.kaggle.com/
2. Aller sur: https://www.kaggle.com/account
3. Cliquer "Create New API Token"
4. Placer `kaggle.json` dans: `C:\Users\ghali\.kaggle\`
5. Installer: `pip install kaggle`
6. Tester: `kaggle datasets list`

---

## 🆘 Aide Rapide

### Problème: Import Error

```powershell
pip install -r requirements.txt --force-reinstall
```

### Problème: CUDA out of memory

→ Voir `training_pipeline.py` ligne ~60, réduire `batch_size=8`

### Problème: Kaggle not working

→ Voir section "Configuration Kaggle" ci-dessus

---

## 📞 Support

- 📚 **README.md** → Documentation complète
- 🚀 **QUICK_START.md** → Guides pas-à-pas
- 📊 **DATASETS_SUMMARY.md** → Tous les datasets
- 🧪 **test_pipeline.py** → Diagnostiquer problèmes

---

## ✅ Checklist

- [ ] Installation terminée (`pip install -r requirements.txt`)
- [ ] Tests passés (`python test_pipeline.py`)
- [ ] Menu lancé (`python data_pipeline_orchestrator.py`)
- [ ] Documentation lue (**QUICK_START.md**)
- [ ] Premier dataset téléchargé
- [ ] Premier modèle entraîné

---

## 🎉 Vous êtes prêt!

Choisissez un workflow ci-dessus et lancez-vous!

**Recommandation:**
→ Lisez **QUICK_START.md** pour 5 scénarios détaillés

**Bonne chance! 🚀**

