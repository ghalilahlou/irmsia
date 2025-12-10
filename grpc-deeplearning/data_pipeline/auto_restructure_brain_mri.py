"""
Auto-Restructure Brain MRI Dataset
Restructure automatiquement le dataset Brain MRI pour training efficace
"""

import sys
import io
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import json

# Fix Windows encoding
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

print("\n" + "="*70)
print("AUTO-RESTRUCTURATION BRAIN MRI DATASET")
print("="*70)

# Chemins
base_dir = Path("datasets")
brain_mri_dir = base_dir / "kaggle" / "mateuszbuda_lgg-mri-segmentation" / "lgg-mri-segmentation" / "kaggle_3m"
organized_dir = base_dir / "organized"
organized_dir.mkdir(parents=True, exist_ok=True)

# Vérifier existence
if not brain_mri_dir.exists():
    print(f"\n❌ Dataset Brain MRI non trouvé: {brain_mri_dir}")
    print(f"   Téléchargez-le d'abord avec:")
    print(f"   python collectors/kaggle_collector.py --download mateuszbuda/lgg-mri-segmentation")
    sys.exit(1)

print(f"\n✅ Dataset trouvé: {brain_mri_dir}")

# Étape 1: Analyser et structurer
print(f"\n" + "="*70)
print("ÉTAPE 1: ANALYSE DES IMAGES ET MASQUES")
print("="*70)

patient_dirs = [d for d in brain_mri_dir.iterdir() if d.is_dir() and d.name.startswith('TCGA')]

print(f"\n📊 Patients: {len(patient_dirs)}")
print(f"🔍 Analyse en cours...")

structured_data = []
images_with_tumor = 0
images_without_tumor = 0

for patient_dir in tqdm(patient_dirs, desc="Scan patients"):
    patient_id = patient_dir.name
    
    # Toutes les images (sauf les masks)
    images = [img for img in patient_dir.glob("*.tif") if "_mask" not in img.name]
    
    for img_path in images:
        # Chercher le mask
        mask_name = img_path.name.replace(".tif", "_mask.tif")
        mask_path = patient_dir / mask_name
        
        has_tumor = mask_path.exists()
        
        structured_data.append({
            'image_path': str(img_path.relative_to(base_dir)),
            'mask_path': str(mask_path.relative_to(base_dir)) if has_tumor else None,
            'patient_id': patient_id,
            'has_tumor': 1 if has_tumor else 0,
            'label': 'tumor' if has_tumor else 'no_tumor'
        })
        
        if has_tumor:
            images_with_tumor += 1
        else:
            images_without_tumor += 1

# Créer DataFrame
df = pd.DataFrame(structured_data)

print(f"\n📈 Résultats:")
print(f"   Total images: {len(df)}")
print(f"   Avec tumeur: {images_with_tumor} ({images_with_tumor/len(df)*100:.1f}%)")
print(f"   Sans tumeur: {images_without_tumor} ({images_without_tumor/len(df)*100:.1f}%)")

# Sauvegarder
structured_csv = organized_dir / "brain_mri_structured.csv"
df.to_csv(structured_csv, index=False)
print(f"\n✅ Structuré: {structured_csv}")

# Étape 2: Créer splits équilibrés
print(f"\n" + "="*70)
print("ÉTAPE 2: CRÉATION DES SPLITS ÉQUILIBRÉS")
print("="*70)

# Vérifier l'équilibre
if images_without_tumor == 0:
    print(f"\n⚠️  ATTENTION: Aucune image sans tumeur détectée!")
    print(f"   Le dataset ne contient que des cas avec tumeurs.")
    print(f"   Création de splits basés sur patients...")
    
    # Split par patient pour éviter data leakage
    patients = df['patient_id'].unique()
    train_patients, temp_patients = train_test_split(
        patients, test_size=0.3, random_state=42
    )
    val_patients, test_patients = train_test_split(
        temp_patients, test_size=0.5, random_state=42
    )
    
    train_df = df[df['patient_id'].isin(train_patients)]
    val_df = df[df['patient_id'].isin(val_patients)]
    test_df = df[df['patient_id'].isin(test_patients)]
    
else:
    # Split stratifié par label
    train_df, temp_df = train_test_split(
        df, test_size=0.3, random_state=42, stratify=df['has_tumor']
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.5, random_state=42, stratify=temp_df['has_tumor']
    )

print(f"\n✂️  Splits créés:")
print(f"   Train: {len(train_df)} images ({len(train_df)/len(df)*100:.1f}%)")
print(f"   Val: {len(val_df)} images ({len(val_df)/len(df)*100:.1f}%)")
print(f"   Test: {len(test_df)} images ({len(test_df)/len(df)*100:.1f}%)")

# Distribution par split
for split_name, split_df in [('Train', train_df), ('Val', val_df), ('Test', test_df)]:
    tumor_count = (split_df['has_tumor'] == 1).sum()
    no_tumor_count = (split_df['has_tumor'] == 0).sum()
    print(f"\n   {split_name}:")
    print(f"      Tumeur: {tumor_count}")
    print(f"      Sans tumeur: {no_tumor_count}")

# Sauvegarder les splits
dataset_dir = organized_dir / "brain_mri"
splits_dir = dataset_dir / "splits"
splits_dir.mkdir(parents=True, exist_ok=True)

train_df.to_csv(splits_dir / "train.csv", index=False)
val_df.to_csv(splits_dir / "val.csv", index=False)
test_df.to_csv(splits_dir / "test.csv", index=False)

print(f"\n✅ Splits sauvegardés: {splits_dir}")

# Étape 3: Metadata
print(f"\n" + "="*70)
print("ÉTAPE 3: CRÉATION DES METADATA")
print("="*70)

metadata = {
    'dataset_name': 'brain_mri',
    'description': 'Brain MRI Low Grade Glioma Segmentation',
    'source': 'Kaggle - mateuszbuda/lgg-mri-segmentation',
    'total_images': len(df),
    'total_patients': len(df['patient_id'].unique()),
    'num_classes': 2,
    'classes': ['no_tumor', 'tumor'],
    'class_distribution': {
        'no_tumor': images_without_tumor,
        'tumor': images_with_tumor
    },
    'splits': {
        'train': {
            'total': len(train_df),
            'tumor': int((train_df['has_tumor'] == 1).sum()),
            'no_tumor': int((train_df['has_tumor'] == 0).sum())
        },
        'val': {
            'total': len(val_df),
            'tumor': int((val_df['has_tumor'] == 1).sum()),
            'no_tumor': int((val_df['has_tumor'] == 0).sum())
        },
        'test': {
            'total': len(test_df),
            'tumor': int((test_df['has_tumor'] == 1).sum()),
            'no_tumor': int((test_df['has_tumor'] == 0).sum())
        }
    },
    'image_format': 'TIFF',
    'image_size': '[240, 240] (variable)',
    'modality': 'MRI',
    'files': {
        'structured_csv': str(structured_csv.relative_to(base_dir)),
        'train_csv': str((splits_dir / "train.csv").relative_to(base_dir)),
        'val_csv': str((splits_dir / "val.csv").relative_to(base_dir)),
        'test_csv': str((splits_dir / "test.csv").relative_to(base_dir))
    }
}

metadata_file = dataset_dir / "metadata.json"
with open(metadata_file, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"\n✅ Metadata créés: {metadata_file}")

# Résumé final
print(f"\n" + "="*70)
print("✅ RESTRUCTURATION TERMINÉE!")
print("="*70)

print(f"\n📁 Fichiers créés:")
print(f"   1. {structured_csv}")
print(f"   2. {splits_dir / 'train.csv'}")
print(f"   3. {splits_dir / 'val.csv'}")
print(f"   4. {splits_dir / 'test.csv'}")
print(f"   5. {metadata_file}")

print(f"\n🚀 Utilisation pour training:")
print(f"\n   python quick_test_training.py")
print(f"\n   Ou modifier pour utiliser les nouveaux chemins:")
print(f"   train_csv = '{splits_dir / 'train.csv'}'")
print(f"   val_csv = '{splits_dir / 'val.csv'}'")

print(f"\n💡 Note:")
if images_without_tumor == 0:
    print(f"   ⚠️  Ce dataset ne contient QUE des images avec tumeurs")
    print(f"   Pour un training binaire équilibré, vous auriez besoin:")
    print(f"   - Soit d'images cérébrales normales")
    print(f"   - Soit d'utiliser un autre dataset (COVID-19, etc.)")
    print(f"\n   Utilisez plutôt ce dataset pour:")
    print(f"   - Segmentation de tumeurs (avec les masks)")
    print(f"   - Classification du type de tumeur")
    print(f"   - Détection de la taille/sévérité")
else:
    print(f"   ✅ Dataset équilibré prêt pour training!")

print(f"\n" + "="*70)

