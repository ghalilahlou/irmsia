"""
Script temporaire pour créer des splits pour Brain MRI dataset
"""

import json
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

# Charger l'index
index_file = Path("datasets/dataset_index.json")
with open(index_file, 'r') as f:
    index = json.load(f)

# Récupérer les images brain_mri
brain_mri_images = index["datasets"]["brain_mri"]["images"]

print(f"Total images: {len(brain_mri_images)}")

# Créer un DataFrame simple
data = []
for img in brain_mri_images:
    # Toutes les images sont des tumeurs cérébrales (gliomes)
    data.append({
        'path': img['path'],
        'size_bytes': img['size_bytes'],
        'hash': img['hash'],
        'label': 1  # 1 = tumeur (ce dataset contient uniquement des cas de gliomes)
    })

df = pd.DataFrame(data)

# Créer les splits (70/15/15)
train_df, temp_df = train_test_split(df, test_size=0.3, random_state=42)
val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42)

print(f"\nSplits créés:")
print(f"  Train: {len(train_df)} images ({len(train_df)/len(df)*100:.1f}%)")
print(f"  Val: {len(val_df)} images ({len(val_df)/len(df)*100:.1f}%)")
print(f"  Test: {len(test_df)} images ({len(test_df)/len(df)*100:.1f}%)")

# Créer le dossier splits
splits_dir = Path("datasets/brain_mri/splits")
splits_dir.mkdir(parents=True, exist_ok=True)

# Sauvegarder les splits
train_df.to_csv(splits_dir / "train.csv", index=False)
val_df.to_csv(splits_dir / "val.csv", index=False)
test_df.to_csv(splits_dir / "test.csv", index=False)

print(f"\n✅ Splits sauvegardés dans: {splits_dir}")
print(f"   - train.csv: {len(train_df)} images")
print(f"   - val.csv: {len(val_df)} images")
print(f"   - test.csv: {len(test_df)} images")

