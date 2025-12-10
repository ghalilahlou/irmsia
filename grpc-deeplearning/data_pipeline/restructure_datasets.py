"""
Restructure Datasets - Organisation intelligente pour training efficace
Trie, organise et prépare les datasets pour un training optimal
"""

import sys
import io
from pathlib import Path
import pandas as pd
import shutil
from typing import Dict, List, Tuple
import logging
from tqdm import tqdm
import json

# Fix Windows encoding
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class DatasetRestructurer:
    """
    Restructure et organise les datasets pour training efficace
    """
    
    def __init__(self, base_dir: str = "datasets"):
        self.base_dir = Path(base_dir)
        self.organized_dir = self.base_dir / "organized"
        self.organized_dir.mkdir(parents=True, exist_ok=True)
        
    def analyze_brain_mri_dataset(self):
        """
        Analyser le dataset Brain MRI et créer des classes à partir des masques
        """
        print("\n" + "="*70)
        print("ANALYSE DU DATASET BRAIN MRI")
        print("="*70)
        
        brain_mri_dir = self.base_dir / "kaggle" / "mateuszbuda_lgg-mri-segmentation" / "lgg-mri-segmentation" / "kaggle_3m"
        
        if not brain_mri_dir.exists():
            print(f"❌ Dataset Brain MRI non trouvé: {brain_mri_dir}")
            return None
        
        print(f"\n📂 Répertoire: {brain_mri_dir}")
        
        # Lister tous les patients
        patient_dirs = [d for d in brain_mri_dir.iterdir() if d.is_dir() and d.name.startswith('TCGA')]
        
        print(f"📊 Patients trouvés: {len(patient_dirs)}")
        
        # Analyser chaque patient
        images_with_mask = 0
        images_without_mask = 0
        
        structured_data = []
        
        for patient_dir in tqdm(patient_dirs, desc="Analyse patients"):
            patient_id = patient_dir.name
            
            # Trouver toutes les images
            images = list(patient_dir.glob("*.tif"))
            
            for img_path in images:
                img_name = img_path.name
                
                # Vérifier si c'est un mask (contient "_mask")
                if "_mask" in img_name:
                    continue
                
                # Chercher le mask correspondant
                mask_name = img_name.replace(".tif", "_mask.tif")
                mask_path = patient_dir / mask_name
                
                has_tumor = mask_path.exists()
                
                structured_data.append({
                    'patient_id': patient_id,
                    'image_path': str(img_path.relative_to(self.base_dir)),
                    'mask_path': str(mask_path.relative_to(self.base_dir)) if has_tumor else None,
                    'has_tumor': 1 if has_tumor else 0,
                    'label': 'tumor' if has_tumor else 'normal'
                })
                
                if has_tumor:
                    images_with_mask += 1
                else:
                    images_without_mask += 1
        
        print(f"\n📈 Statistiques:")
        print(f"   Images avec tumeur (mask): {images_with_mask}")
        print(f"   Images sans tumeur: {images_without_mask}")
        print(f"   Total: {images_with_mask + images_without_mask}")
        
        # Créer DataFrame
        df = pd.DataFrame(structured_data)
        
        # Sauvegarder
        output_file = self.organized_dir / "brain_mri_structured.csv"
        df.to_csv(output_file, index=False)
        
        print(f"\n✅ Dataset structuré sauvegardé: {output_file}")
        
        return df
    
    def organize_by_class(self, csv_file: str, output_name: str):
        """
        Organiser un dataset par classes dans des dossiers séparés
        Structure: organized/dataset_name/train/class_0/, train/class_1/, val/, test/
        """
        print(f"\n" + "="*70)
        print(f"ORGANISATION PAR CLASSES: {output_name}")
        print("="*70)
        
        # Charger le CSV
        df = pd.read_csv(csv_file)
        
        print(f"\n📊 Dataset:")
        print(f"   Total images: {len(df)}")
        
        # Compter les classes
        if 'label' in df.columns:
            class_counts = df['label'].value_counts()
            print(f"\n📈 Distribution des classes:")
            for label, count in class_counts.items():
                print(f"   {label}: {count} ({count/len(df)*100:.1f}%)")
        elif 'has_tumor' in df.columns:
            class_counts = df['has_tumor'].value_counts()
            print(f"\n📈 Distribution:")
            print(f"   Avec tumeur: {class_counts.get(1, 0)}")
            print(f"   Sans tumeur: {class_counts.get(0, 0)}")
        
        # Créer les splits
        from sklearn.model_selection import train_test_split
        
        # Stratify by label
        stratify_col = df['label'] if 'label' in df.columns else df['has_tumor']
        
        # Train (70%), Temp (30%)
        train_df, temp_df = train_test_split(
            df, 
            test_size=0.3, 
            random_state=42,
            stratify=stratify_col
        )
        
        # Val (15%), Test (15%)
        val_df, test_df = train_test_split(
            temp_df,
            test_size=0.5,
            random_state=42,
            stratify=temp_df[stratify_col.name]
        )
        
        print(f"\n✂️  Splits créés:")
        print(f"   Train: {len(train_df)} ({len(train_df)/len(df)*100:.1f}%)")
        print(f"   Val: {len(val_df)} ({len(val_df)/len(df)*100:.1f}%)")
        print(f"   Test: {len(test_df)} ({len(test_df)/len(df)*100:.1f}%)")
        
        # Créer la structure de dossiers
        organized_dataset_dir = self.organized_dir / output_name
        
        for split_name, split_df in [('train', train_df), ('val', val_df), ('test', test_df)]:
            split_dir = organized_dataset_dir / split_name
            
            # Créer dossiers par classe
            classes = split_df[stratify_col.name].unique()
            for class_name in classes:
                class_dir = split_dir / str(class_name)
                class_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📁 Structure créée: {organized_dataset_dir}")
        
        # Copier ou créer des liens symboliques
        print(f"\n📋 Création de manifestes CSV (sans copie de fichiers)...")
        
        # Sauvegarder les splits
        splits_dir = organized_dataset_dir / "splits"
        splits_dir.mkdir(parents=True, exist_ok=True)
        
        train_df.to_csv(splits_dir / "train.csv", index=False)
        val_df.to_csv(splits_dir / "val.csv", index=False)
        test_df.to_csv(splits_dir / "test.csv", index=False)
        
        print(f"   ✅ train.csv: {len(train_df)} images")
        print(f"   ✅ val.csv: {len(val_df)} images")
        print(f"   ✅ test.csv: {len(test_df)} images")
        
        # Créer un fichier de metadata
        metadata = {
            'dataset_name': output_name,
            'total_images': len(df),
            'num_classes': len(classes),
            'classes': list(map(str, classes)),
            'splits': {
                'train': len(train_df),
                'val': len(val_df),
                'test': len(test_df)
            },
            'class_distribution': class_counts.to_dict() if hasattr(class_counts, 'to_dict') else {}
        }
        
        with open(organized_dataset_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✅ Dataset organisé: {organized_dataset_dir}")
        
        return organized_dataset_dir
    
    def create_balanced_subset(self, csv_file: str, output_name: str, samples_per_class: int = 1000):
        """
        Créer un subset équilibré d'un dataset
        """
        print(f"\n" + "="*70)
        print(f"CRÉATION SUBSET ÉQUILIBRÉ: {output_name}")
        print(f"Échantillons par classe: {samples_per_class}")
        print("="*70)
        
        df = pd.read_csv(csv_file)
        
        # Identifier la colonne de classe
        class_col = 'label' if 'label' in df.columns else 'has_tumor'
        
        # Échantillonner par classe
        balanced_dfs = []
        
        for class_value in df[class_col].unique():
            class_df = df[df[class_col] == class_value]
            
            # Prendre au maximum samples_per_class
            n_samples = min(len(class_df), samples_per_class)
            sampled = class_df.sample(n=n_samples, random_state=42)
            balanced_dfs.append(sampled)
            
            print(f"   Classe {class_value}: {n_samples} échantillons")
        
        # Combiner
        balanced_df = pd.concat(balanced_dfs, ignore_index=True)
        
        # Mélanger
        balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        print(f"\n📊 Subset équilibré:")
        print(f"   Total: {len(balanced_df)} images")
        
        # Sauvegarder
        output_file = self.organized_dir / f"{output_name}_balanced.csv"
        balanced_df.to_csv(output_file, index=False)
        
        print(f"\n✅ Subset sauvegardé: {output_file}")
        
        return balanced_df
    
    def list_organized_datasets(self):
        """
        Lister tous les datasets organisés
        """
        print("\n" + "="*70)
        print("DATASETS ORGANISÉS")
        print("="*70)
        
        if not self.organized_dir.exists():
            print("\n❌ Aucun dataset organisé trouvé")
            return
        
        datasets = [d for d in self.organized_dir.iterdir() if d.is_dir()]
        
        if not datasets:
            print("\n❌ Aucun dataset organisé trouvé")
            return
        
        print(f"\n📂 {len(datasets)} dataset(s) organisé(s):\n")
        
        for dataset_dir in datasets:
            metadata_file = dataset_dir / "metadata.json"
            
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                print(f"   🔹 {dataset_dir.name}")
                print(f"      Images: {metadata['total_images']}")
                print(f"      Classes: {metadata['num_classes']} ({', '.join(metadata['classes'])})")
                print(f"      Splits: Train={metadata['splits']['train']}, Val={metadata['splits']['val']}, Test={metadata['splits']['test']}")
                print()
            else:
                print(f"   🔹 {dataset_dir.name} (pas de metadata)")
                print()


def main():
    """
    Menu interactif pour restructuration de datasets
    """
    
    print("\n" + "="*70)
    print("RESTRUCTURATION DE DATASETS POUR TRAINING EFFICACE")
    print("="*70)
    
    restructurer = DatasetRestructurer()
    
    while True:
        print("\n" + "="*70)
        print("MENU PRINCIPAL")
        print("="*70)
        print("\n1. Analyser et structurer Brain MRI (avec détection tumeurs)")
        print("2. Organiser un dataset par classes")
        print("3. Créer un subset équilibré")
        print("4. Lister les datasets organisés")
        print("5. Quitter")
        
        choice = input("\nVotre choix (1-5): ").strip()
        
        if choice == '1':
            # Brain MRI
            df = restructurer.analyze_brain_mri_dataset()
            
            if df is not None:
                # Organiser automatiquement
                proceed = input("\n➡️  Organiser ce dataset maintenant? (y/n): ").strip().lower()
                if proceed == 'y':
                    restructurer.organize_by_class(
                        "datasets/organized/brain_mri_structured.csv",
                        "brain_mri"
                    )
        
        elif choice == '2':
            # Organiser un dataset
            csv_file = input("\nChemin du fichier CSV: ").strip()
            output_name = input("Nom du dataset organisé: ").strip()
            
            if Path(csv_file).exists():
                restructurer.organize_by_class(csv_file, output_name)
            else:
                print(f"❌ Fichier non trouvé: {csv_file}")
        
        elif choice == '3':
            # Subset équilibré
            csv_file = input("\nChemin du fichier CSV: ").strip()
            output_name = input("Nom du subset: ").strip()
            samples = input("Échantillons par classe (défaut: 1000): ").strip()
            
            samples_per_class = int(samples) if samples else 1000
            
            if Path(csv_file).exists():
                restructurer.create_balanced_subset(csv_file, output_name, samples_per_class)
            else:
                print(f"❌ Fichier non trouvé: {csv_file}")
        
        elif choice == '4':
            # Lister
            restructurer.list_organized_datasets()
        
        elif choice == '5':
            print("\n👋 Au revoir!")
            break
        
        else:
            print("❌ Choix invalide")


if __name__ == "__main__":
    main()

