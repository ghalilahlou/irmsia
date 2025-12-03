"""
Dataset Manager - Gestion centralisée des datasets médicaux
Organise, indexe et prépare les données pour l'entraînement
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
from tqdm import tqdm
import shutil
import hashlib
import sys
import io

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatasetManager:
    """
    Gestionnaire central de datasets médicaux
    - Indexation de toutes les images
    - Organisation par pathologie
    - Création de splits train/val/test
    - Export pour training
    """
    
    def __init__(self, base_dir: str = "datasets"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_file = self.base_dir / "dataset_index.json"
        self.index = self._load_index()
        
        logger.info(f"Dataset Manager initialized: {self.base_dir}")
    
    def _load_index(self) -> Dict:
        """Charger l'index existant"""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                return json.load(f)
        return {"datasets": {}, "total_images": 0, "pathologies": {}}
    
    def _save_index(self):
        """Sauvegarder l'index"""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
        logger.info(f"Index saved: {self.index_file}")
    
    def scan_directory(
        self,
        directory: str,
        dataset_name: str,
        file_extensions: List[str] = ['.dcm', '.dicom']
    ) -> int:
        """
        Scanner un répertoire et indexer toutes les images
        
        Args:
            directory: Répertoire à scanner
            dataset_name: Nom du dataset
            file_extensions: Extensions de fichiers à indexer
        
        Returns:
            Nombre d'images trouvées
        """
        logger.info(f"Scanning directory: {directory}")
        
        directory = Path(directory)
        if not directory.exists():
            logger.error(f"Directory not found: {directory}")
            return 0
        
        # Trouver tous les fichiers DICOM
        image_files = []
        for ext in file_extensions:
            image_files.extend(directory.rglob(f'*{ext}'))
        
        logger.info(f"Found {len(image_files)} images")
        
        # Indexer
        dataset_info = {
            "name": dataset_name,
            "path": str(directory),
            "num_images": len(image_files),
            "images": []
        }
        
        for img_path in tqdm(image_files, desc="Indexing"):
            # Calculer hash du fichier
            file_hash = self._calculate_hash(img_path)
            
            image_info = {
                "path": str(img_path.relative_to(self.base_dir)),
                "size_bytes": img_path.stat().st_size,
                "hash": file_hash
            }
            
            dataset_info["images"].append(image_info)
        
        # Ajouter à l'index
        self.index["datasets"][dataset_name] = dataset_info
        self.index["total_images"] = sum(
            ds["num_images"] for ds in self.index["datasets"].values()
        )
        
        self._save_index()
        
        logger.info(f"✅ Indexed {len(image_files)} images for dataset '{dataset_name}'")
        
        return len(image_files)
    
    def _calculate_hash(self, file_path: Path) -> str:
        """Calculer le hash SHA-256 d'un fichier"""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()[:16]  # Premiers 16 caractères
    
    def create_labeled_dataset(
        self,
        dataset_name: str,
        labels_csv: str,
        image_column: str = "Image Index",
        label_columns: Optional[List[str]] = None
    ):
        """
        Créer un dataset labelisé depuis un CSV
        
        Args:
            dataset_name: Nom du dataset
            labels_csv: Path vers le CSV de labels
            image_column: Colonne avec les noms d'images
            label_columns: Colonnes de labels
        """
        logger.info(f"Creating labeled dataset: {dataset_name}")
        
        # Charger le CSV
        df = pd.read_csv(labels_csv)
        logger.info(f"Loaded {len(df)} labels")
        
        # Vérifier que le dataset est indexé
        if dataset_name not in self.index["datasets"]:
            logger.error(f"Dataset not indexed: {dataset_name}")
            logger.info(f"Run scan_directory() first")
            return None
        
        dataset_info = self.index["datasets"][dataset_name]
        
        # Mapper images → labels
        labeled_images = []
        
        for img_info in dataset_info["images"]:
            img_name = Path(img_info["path"]).name
            
            # Trouver le label
            label_row = df[df[image_column] == img_name]
            
            if len(label_row) > 0:
                labels = {}
                if label_columns:
                    for col in label_columns:
                        if col in label_row.columns:
                            labels[col] = label_row[col].values[0]
                else:
                    labels = label_row.to_dict('records')[0]
                
                labeled_images.append({
                    **img_info,
                    "labels": labels
                })
        
        logger.info(f"Matched {len(labeled_images)}/{len(dataset_info['images'])} images with labels")
        
        # Sauvegarder
        labeled_dataset_file = self.base_dir / f"{dataset_name}_labeled.json"
        
        with open(labeled_dataset_file, 'w') as f:
            json.dump(labeled_images, f, indent=2)
        
        logger.info(f"✅ Labeled dataset saved: {labeled_dataset_file}")
        
        return labeled_images
    
    def create_train_val_test_split(
        self,
        dataset_name: str,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        stratify_column: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Créer un split train/val/test
        
        Args:
            dataset_name: Nom du dataset
            train_ratio: Ratio training
            val_ratio: Ratio validation
            test_ratio: Ratio test
            stratify_column: Colonne pour stratification
        
        Returns:
            Dict with train/val/test DataFrames
        """
        logger.info(f"Creating split for dataset: {dataset_name}")
        
        # Charger le labeled dataset
        labeled_file = self.base_dir / f"{dataset_name}_labeled.json"
        
        if not labeled_file.exists():
            logger.error(f"Labeled dataset not found: {labeled_file}")
            return None
        
        with open(labeled_file, 'r') as f:
            labeled_data = json.load(f)
        
        df = pd.DataFrame(labeled_data)
        
        # Split
        from sklearn.model_selection import train_test_split
        
        # Train / temp
        train_df, temp_df = train_test_split(
            df,
            test_size=(1 - train_ratio),
            random_state=42
        )
        
        # Val / test
        val_ratio_adjusted = val_ratio / (val_ratio + test_ratio)
        val_df, test_df = train_test_split(
            temp_df,
            test_size=(1 - val_ratio_adjusted),
            random_state=42
        )
        
        logger.info(f"Split created:")
        logger.info(f"   Train: {len(train_df)} ({len(train_df)/len(df)*100:.1f}%)")
        logger.info(f"   Val: {len(val_df)} ({len(val_df)/len(df)*100:.1f}%)")
        logger.info(f"   Test: {len(test_df)} ({len(test_df)/len(df)*100:.1f}%)")
        
        # Sauvegarder
        splits_dir = self.base_dir / dataset_name / "splits"
        splits_dir.mkdir(parents=True, exist_ok=True)
        
        train_df.to_csv(splits_dir / "train.csv", index=False)
        val_df.to_csv(splits_dir / "val.csv", index=False)
        test_df.to_csv(splits_dir / "test.csv", index=False)
        
        logger.info(f"✅ Splits saved to: {splits_dir}")
        
        return {
            'train': train_df,
            'val': val_df,
            'test': test_df
        }
    
    def get_dataset_statistics(self, dataset_name: str) -> Dict:
        """
        Obtenir des statistiques sur un dataset
        
        Args:
            dataset_name: Nom du dataset
        
        Returns:
            Dict avec statistiques
        """
        if dataset_name not in self.index["datasets"]:
            logger.error(f"Dataset not found: {dataset_name}")
            return {}
        
        dataset_info = self.index["datasets"][dataset_name]
        
        total_size = sum(img["size_bytes"] for img in dataset_info["images"])
        
        stats = {
            "name": dataset_name,
            "num_images": dataset_info["num_images"],
            "total_size_gb": total_size / (1024**3),
            "avg_size_mb": (total_size / dataset_info["num_images"]) / (1024**2),
            "path": dataset_info["path"]
        }
        
        logger.info(f"Dataset Statistics: {dataset_name}")
        logger.info(f"   Images: {stats['num_images']}")
        logger.info(f"   Total Size: {stats['total_size_gb']:.2f} GB")
        logger.info(f"   Avg Size: {stats['avg_size_mb']:.2f} MB")
        
        return stats
    
    def merge_datasets(
        self,
        dataset_names: List[str],
        output_name: str
    ):
        """
        Fusionner plusieurs datasets
        
        Args:
            dataset_names: Liste de noms de datasets
            output_name: Nom du dataset fusionné
        """
        logger.info(f"Merging datasets: {dataset_names} → {output_name}")
        
        merged_images = []
        
        for ds_name in dataset_names:
            if ds_name not in self.index["datasets"]:
                logger.warning(f"Dataset not found: {ds_name}")
                continue
            
            ds_info = self.index["datasets"][ds_name]
            merged_images.extend(ds_info["images"])
        
        merged_info = {
            "name": output_name,
            "path": str(self.base_dir / output_name),
            "num_images": len(merged_images),
            "images": merged_images,
            "source_datasets": dataset_names
        }
        
        self.index["datasets"][output_name] = merged_info
        self._save_index()
        
        logger.info(f"✅ Merged {len(merged_images)} images into '{output_name}'")
        
        return merged_info
    
    def export_for_training(
        self,
        dataset_name: str,
        split: str = "train",
        output_format: str = "json"
    ) -> str:
        """
        Exporter un dataset pour training
        
        Args:
            dataset_name: Nom du dataset
            split: train/val/test
            output_format: json/csv/txt
        
        Returns:
            Path vers le fichier exporté
        """
        logger.info(f"Exporting {dataset_name}/{split} for training...")
        
        splits_dir = self.base_dir / dataset_name / "splits"
        split_file = splits_dir / f"{split}.csv"
        
        if not split_file.exists():
            logger.error(f"Split file not found: {split_file}")
            return None
        
        df = pd.read_csv(split_file)
        
        # Export
        output_file = splits_dir / f"{split}.{output_format}"
        
        if output_format == "json":
            df.to_json(output_file, orient='records', indent=2)
        elif output_format == "csv":
            df.to_csv(output_file, index=False)
        elif output_format == "txt":
            # Simple list of paths
            with open(output_file, 'w') as f:
                for path in df['path']:
                    f.write(f"{path}\n")
        
        logger.info(f"✅ Exported to: {output_file}")
        
        return str(output_file)
    
    def print_summary(self):
        """Afficher un résumé de tous les datasets"""
        print("\n" + "="*70)
        print("DATASET MANAGER SUMMARY")
        print("="*70)
        
        print(f"\n📊 Total Images: {self.index['total_images']:,}")
        print(f"📁 Total Datasets: {len(self.index['datasets'])}")
        
        if self.index['datasets']:
            print(f"\n📂 Datasets:")
            for name, info in self.index['datasets'].items():
                print(f"\n   🔹 {name}")
                print(f"      Images: {info['num_images']:,}")
                print(f"      Path: {info['path']}")
        
        print("\n" + "="*70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Dataset Manager')
    parser.add_argument('--scan', type=str, help='Scan directory and index')
    parser.add_argument('--dataset-name', type=str, help='Dataset name')
    parser.add_argument('--create-split', type=str, help='Create train/val/test split')
    parser.add_argument('--export', type=str, help='Export split for training')
    parser.add_argument('--split', type=str, default='train', help='Split to export')
    parser.add_argument('--summary', action='store_true', help='Print summary')
    
    args = parser.parse_args()
    
    manager = DatasetManager()
    
    if args.summary:
        manager.print_summary()
    
    elif args.scan:
        if not args.dataset_name:
            print("Please provide --dataset-name")
        else:
            manager.scan_directory(args.scan, args.dataset_name)
    
    elif args.create_split:
        manager.create_train_val_test_split(args.create_split)
    
    elif args.export:
        manager.export_for_training(args.export, split=args.split)
    
    else:
        parser.print_help()

