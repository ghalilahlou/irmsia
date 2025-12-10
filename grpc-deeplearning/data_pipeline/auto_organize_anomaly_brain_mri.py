"""
Organisation Automatique pour Détection d'Anomalies - Brain MRI
Utilise le dataset Brain MRI existant pour créer un système de détection d'anomalies
"""

import sys
import io
from pathlib import Path
import pandas as pd
import json

# Fix Windows encoding
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

print("\n" + "="*70)
print("ORGANISATION AUTO POUR DÉTECTION D'ANOMALIES")
print("Dataset: Brain MRI")
print("="*70)

# Vérifier l'existence du dataset structuré
structured_csv = Path("datasets/organized/brain_mri_structured.csv")

if not structured_csv.exists():
    print(f"\n❌ Dataset structuré non trouvé: {structured_csv}")
    print(f"\n💡 Exécutez d'abord:")
    print(f"   python auto_restructure_brain_mri.py")
    sys.exit(1)

print(f"\n✅ Dataset trouvé: {structured_csv}")

# Charger les données
df = pd.read_csv(structured_csv)

print(f"\n📊 Dataset:")
print(f"   Total images: {len(df)}")

# ÉTAPE 1: Classification étiqueté/non-étiqueté
print(f"\n" + "="*70)
print("ÉTAPE 1: CLASSIFICATION ÉTIQUETÉ/NON-ÉTIQUETÉ")
print("="*70)

# Dans Brain MRI, toutes les images avec mask_path sont étiquetées
labeled_df = df[df['mask_path'].notna()].copy()
unlabeled_df = df[df['mask_path'].isna()].copy()

print(f"\n📈 Classification:")
print(f"   Étiquetées (avec mask): {len(labeled_df)}")
print(f"   Non-étiquetées (sans mask): {len(unlabeled_df)}")

# Ajouter métadonnées
labeled_df['is_labeled'] = 1
labeled_df['anatomical_region'] = 'brain'
labeled_df['modality'] = 'mri'
labeled_df['anomaly_type'] = 'tumor'
labeled_df['is_normal'] = 0  # Toutes ont des tumeurs

unlabeled_df['is_labeled'] = 0
unlabeled_df['anatomical_region'] = 'brain'
unlabeled_df['modality'] = 'mri'
unlabeled_df['anomaly_type'] = 'unknown'
unlabeled_df['is_normal'] = 1  # Assumé normal

# ÉTAPE 2: Organisation pour anomaly detection
print(f"\n" + "="*70)
print("ÉTAPE 2: ORGANISATION POUR DÉTECTION D'ANOMALIES")
print("="*70)

anomaly_dir = Path("datasets/anomaly_detection")
anomaly_dir.mkdir(parents=True, exist_ok=True)

# Créer structure
brain_dir = anomaly_dir / "brain_mri"
brain_dir.mkdir(parents=True, exist_ok=True)

# Sauvegarder les datasets organisés
labeled_df.to_csv(brain_dir / "labeled.csv", index=False)
unlabeled_df.to_csv(brain_dir / "unlabeled.csv", index=False)

print(f"\n✅ Datasets sauvegardés:")
print(f"   Étiquetées: {brain_dir / 'labeled.csv'}")
print(f"   Non-étiquetées: {brain_dir / 'unlabeled.csv'}")

# ÉTAPE 3: Créer splits pour training
print(f"\n" + "="*70)
print("ÉTAPE 3: CRÉATION DES SPLITS POUR TRAINING")
print("="*70)

from sklearn.model_selection import train_test_split

# Combiner les deux pour avoir un dataset complet
all_data = pd.concat([labeled_df, unlabeled_df], ignore_index=True)

# Split par patient pour éviter data leakage
patients = all_data['patient_id'].unique()
train_patients, temp_patients = train_test_split(patients, test_size=0.3, random_state=42)
val_patients, test_patients = train_test_split(temp_patients, test_size=0.5, random_state=42)

train_df = all_data[all_data['patient_id'].isin(train_patients)]
val_df = all_data[all_data['patient_id'].isin(val_patients)]
test_df = all_data[all_data['patient_id'].isin(test_patients)]

print(f"\n✂️  Splits créés:")
print(f"   Train: {len(train_df)} images")
print(f"      - Étiquetées: {(train_df['is_labeled'] == 1).sum()}")
print(f"      - Non-étiquetées: {(train_df['is_labeled'] == 0).sum()}")
print(f"   Val: {len(val_df)} images")
print(f"   Test: {len(test_df)} images")

# Sauvegarder splits
splits_dir = brain_dir / "splits"
splits_dir.mkdir(parents=True, exist_ok=True)

train_df.to_csv(splits_dir / "train.csv", index=False)
val_df.to_csv(splits_dir / "val.csv", index=False)
test_df.to_csv(splits_dir / "test.csv", index=False)

print(f"\n✅ Splits sauvegardés: {splits_dir}")

# ÉTAPE 4: Metadata et Configuration
print(f"\n" + "="*70)
print("ÉTAPE 4: METADATA ET CONFIGURATION")
print("="*70)

metadata = {
    'dataset_name': 'brain_mri_anomaly_detection',
    'description': 'Brain MRI pour détection d\'anomalies (gliomes)',
    'anatomical_region': 'brain',
    'modality': 'MRI',
    'anomaly_types': ['tumor', 'glioma'],
    'total_images': len(all_data),
    'labeled_images': len(labeled_df),
    'unlabeled_images': len(unlabeled_df),
    'splits': {
        'train': {
            'total': len(train_df),
            'labeled': int((train_df['is_labeled'] == 1).sum()),
            'unlabeled': int((train_df['is_labeled'] == 0).sum())
        },
        'val': {
            'total': len(val_df),
            'labeled': int((val_df['is_labeled'] == 1).sum()),
            'unlabeled': int((val_df['is_labeled'] == 0).sum())
        },
        'test': {
            'total': len(test_df),
            'labeled': int((test_df['is_labeled'] == 1).sum()),
            'unlabeled': int((test_df['is_labeled'] == 0).sum())
        }
    },
    'files': {
        'train_csv': str(splits_dir / "train.csv"),
        'val_csv': str(splits_dir / "val.csv"),
        'test_csv': str(splits_dir / "test.csv"),
        'labeled_csv': str(brain_dir / "labeled.csv"),
        'unlabeled_csv': str(brain_dir / "unlabeled.csv")
    }
}

with open(brain_dir / "metadata.json", 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"\n✅ Metadata: {brain_dir / 'metadata.json'}")

# Configuration de training
training_config = {
    'approach': 'semi-supervised_anomaly_detection',
    'objective': 'Detect brain anomalies (tumors, lesions, etc.)',
    'dataset': str(brain_dir),
    'architecture': {
        'phase_1_supervised': {
            'model': 'EfficientNet-B4',
            'task': 'binary classification (normal/anomaly)',
            'data': 'labeled images only',
            'epochs': 30
        },
        'phase_2_unsupervised': {
            'model': 'Variational Autoencoder (VAE)',
            'task': 'learn normal brain patterns',
            'data': 'unlabeled images (assumed normal)',
            'epochs': 50
        },
        'phase_3_ensemble': {
            'strategy': 'Combine supervised + unsupervised scores',
            'threshold': 'adaptive based on validation set'
        }
    },
    'training_steps': [
        '1. Train supervised classifier on labeled data',
        '2. Train VAE on unlabeled data to learn normality',
        '3. Combine predictions: anomaly = (supervised_score + reconstruction_error) / 2',
        '4. Fine-tune thresholds on validation set'
    ],
    'metrics': [
        'Accuracy',
        'Precision/Recall',
        'F1-Score',
        'ROC-AUC',
        'Reconstruction Error (for VAE)'
    ]
}

with open(brain_dir / "training_config.json", 'w') as f:
    json.dump(training_config, f, indent=2)

print(f"✅ Training config: {brain_dir / 'training_config.json'}")

# ÉTAPE 5: Guide d'utilisation
print(f"\n" + "="*70)
print("✅ ORGANISATION TERMINÉE!")
print("="*70)

print(f"\n📁 Structure créée:")
print(f"   {brain_dir}/")
print(f"   ├── labeled.csv              # Images avec tumeurs (étiquetées)")
print(f"   ├── unlabeled.csv            # Images sans mask (non-étiquetées)")
print(f"   ├── metadata.json            # Métadonnées complètes")
print(f"   ├── training_config.json     # Configuration training")
print(f"   └── splits/")
print(f"       ├── train.csv            # Training set (70%)")
print(f"       ├── val.csv              # Validation set (15%)")
print(f"       └── test.csv             # Test set (15%)")

print(f"\n📊 Résumé:")
print(f"   Total: {len(all_data)} images")
print(f"   Étiquetées: {len(labeled_df)} (avec tumeurs confirmées)")
print(f"   Non-étiquetées: {len(unlabeled_df)} (pas de mask = assumé normal)")

print(f"\n🚀 Prochaines étapes:")
print(f"\n   1. Entraîner modèle supervisé:")
print(f"      python train_anomaly_detector.py --phase supervised")
print(f"\n   2. Entraîner autoencoder:")
print(f"      python train_anomaly_detector.py --phase unsupervised")
print(f"\n   3. Combiner les deux:")
print(f"      python train_anomaly_detector.py --phase ensemble")

print(f"\n💡 Note:")
print(f"   Ce dataset est organisé pour détecter des anomalies cérébrales.")
print(f"   Pour un détecteur MULTI-ORGANES, répétez ce processus avec:")
print(f"   - Dataset poumons (COVID-19, pneumonie)")
print(f"   - Dataset thorax (X-Rays)")
print(f"   - Dataset abdomen, etc.")
print(f"\n   Puis utilisez:")
print(f"   python organize_for_anomaly_detection.py")
print(f"   Pour créer un système multi-organes complet!")

print(f"\n" + "="*70)

