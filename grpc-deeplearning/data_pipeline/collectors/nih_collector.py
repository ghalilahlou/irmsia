"""
NIH (National Institutes of Health) Dataset Collector
Télécharge les datasets publics du NIH
"""

import requests
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
import logging
from tqdm import tqdm
import zipfile
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NIHCollector:
    """
    Collecteur pour NIH ChestX-ray14
    Dataset de 112,120 radiographies thoraciques avec 14 pathologies
    """
    
    DATASET_INFO = {
        "name": "NIH ChestX-ray14",
        "url": "https://nihcc.app.box.com/v/ChestXray-NIHCC",
        "images": 112120,
        "pathologies": 14,
        "size_gb": 42,
        "patients": 30805
    }
    
    # URLs des fichiers (Box.com)
    IMAGE_URLS = [
        f"https://nihcc.app.box.com/shared/static/vfk49d74nhbxq3nqjg0900w5nvkorp5c.gz",  # Part 1
        # ... (14 parts au total)
    ]
    
    LABELS_URL = "https://nihcc.app.box.com/shared/static/i28rlmbvmfjbl8p2n3ril0pptcmcu9d1.csv"
    
    PATHOLOGY_CLASSES = [
        "Atelectasis",
        "Cardiomegaly",
        "Effusion",
        "Infiltration",
        "Mass",
        "Nodule",
        "Pneumonia",
        "Pneumothorax",
        "Consolidation",
        "Edema",
        "Emphysema",
        "Fibrosis",
        "Pleural_Thickening",
        "Hernia"
    ]
    
    def __init__(self, output_dir: str = "datasets/nih"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.images_dir = self.output_dir / "images"
        self.images_dir.mkdir(exist_ok=True)
        
        self.labels_dir = self.output_dir / "labels"
        self.labels_dir.mkdir(exist_ok=True)
        
        logger.info(f"NIH Collector initialized: {self.output_dir}")
    
    def download_labels(self):
        """Télécharger les fichiers de labels"""
        logger.info("Downloading NIH ChestX-ray14 labels...")
        
        labels_file = self.labels_dir / "Data_Entry_2017.csv"
        
        if labels_file.exists():
            logger.info(f"Labels already downloaded: {labels_file}")
            return labels_file
        
        try:
            import gzip
            
            response = requests.get(self.LABELS_URL, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            # Download to temporary gzip file
            temp_file = self.labels_dir / "Data_Entry_2017.csv.gz"
            
            with open(temp_file, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc='Labels') as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        pbar.update(len(chunk))
            
            # Check if file is gzipped
            with open(temp_file, 'rb') as f:
                magic = f.read(2)
            
            if magic == b'\x1f\x8b':  # Gzip magic number
                logger.info("Decompressing gzip file...")
                with gzip.open(temp_file, 'rb') as f_in:
                    with open(labels_file, 'wb') as f_out:
                        f_out.write(f_in.read())
                temp_file.unlink()  # Remove gz file
            else:
                # Not gzipped, just rename
                temp_file.rename(labels_file)
            
            logger.info(f"✅ Labels downloaded: {labels_file}")
            
            return labels_file
        
        except Exception as e:
            logger.error(f"Failed to download labels: {e}")
            return None
    
    def parse_labels(self) -> pd.DataFrame:
        """
        Parser les labels
        
        Returns:
            DataFrame with image names and labels
        """
        labels_file = self.labels_dir / "Data_Entry_2017.csv"
        
        if not labels_file.exists():
            logger.warning("Labels file not found. Downloading...")
            self.download_labels()
        
        try:
            df = pd.read_csv(labels_file)
            
            logger.info(f"Labels loaded: {len(df)} images")
            logger.info(f"Columns: {df.columns.tolist()}")
            
            # Parse finding labels (multi-label)
            df['labels'] = df['Finding Labels'].apply(
                lambda x: x.split('|') if x != 'No Finding' else []
            )
            
            # Create binary columns for each pathology
            for pathology in self.PATHOLOGY_CLASSES:
                df[pathology] = df['labels'].apply(lambda x: 1 if pathology in x else 0)
            
            logger.info(f"Pathology distribution:")
            for pathology in self.PATHOLOGY_CLASSES:
                count = df[pathology].sum()
                percentage = count / len(df) * 100
                logger.info(f"   {pathology}: {count} ({percentage:.1f}%)")
            
            return df
        
        except Exception as e:
            logger.error(f"Failed to parse labels: {e}")
            return None
    
    def download_images_subset(
        self,
        num_images: int = 1000,
        pathologies: Optional[List[str]] = None,
        download_method: str = "manual"
    ):
        """
        Télécharger un subset d'images
        
        Args:
            num_images: Nombre d'images à télécharger
            pathologies: Filtrer par pathologies (None = toutes)
            download_method: "manual" (instructions) ou "auto" (non implémenté - dataset trop gros)
        
        Note:
            Le dataset complet fait 42GB. Pour le télécharger:
            1. Aller sur https://nihcc.app.box.com/v/ChestXray-NIHCC
            2. Télécharger les parties souhaitées
            3. Extraire dans {output_dir}/images/
        """
        logger.info(f"NIH ChestX-ray14 download instructions:")
        logger.info(f"")
        logger.info(f"Le dataset complet fait 42GB (14 parties).")
        logger.info(f"")
        logger.info(f"Pour télécharger:")
        logger.info(f"1. Visitez: https://nihcc.app.box.com/v/ChestXray-NIHCC")
        logger.info(f"2. Téléchargez les fichiers images_001.tar.gz à images_014.tar.gz")
        logger.info(f"3. Extrayez dans: {self.images_dir}")
        logger.info(f"")
        logger.info(f"Ou utilisez les scripts de téléchargement automatique:")
        logger.info(f"   wget https://nihcc.app.box.com/shared/static/vfk49d74nhbxq3nqjg0900w5nvkorp5c.gz -O images_001.tar.gz")
        logger.info(f"   tar -xzf images_001.tar.gz -C {self.images_dir}")
        
        return self.images_dir
    
    def create_training_split(
        self,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        stratify_by: str = "Finding Labels"
    ):
        """
        Créer un split train/val/test
        
        Args:
            train_ratio: Proportion training
            val_ratio: Proportion validation
            test_ratio: Proportion test
            stratify_by: Colonne pour stratification
        
        Returns:
            Dict with train/val/test DataFrames
        """
        df = self.parse_labels()
        
        if df is None:
            return None
        
        from sklearn.model_selection import train_test_split
        
        # Split train / temp
        train_df, temp_df = train_test_split(
            df,
            test_size=(1 - train_ratio),
            random_state=42,
            stratify=df[stratify_by] if stratify_by in df.columns else None
        )
        
        # Split val / test
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
        
        # Save splits
        train_df.to_csv(self.labels_dir / "train.csv", index=False)
        val_df.to_csv(self.labels_dir / "val.csv", index=False)
        test_df.to_csv(self.labels_dir / "test.csv", index=False)
        
        logger.info(f"✅ Splits saved to: {self.labels_dir}")
        
        return {
            'train': train_df,
            'val': val_df,
            'test': test_df
        }


def print_recommended_datasets():
    """Afficher les datasets NIH recommandés"""
    print("\n" + "="*70)
    print("RECOMMENDED NIH DATASETS FOR IRMSIA")
    print("="*70)
    
    print(f"\n🏥 NIH ChestX-ray14:")
    print(f"   Description: Radiographies thoraciques avec 14 pathologies")
    print(f"   Images: 112,120")
    print(f"   Patients: 30,805")
    print(f"   Size: ~42GB")
    print(f"   Format: PNG")
    print(f"   URL: https://nihcc.app.box.com/v/ChestXray-NIHCC")
    print(f"\n   Pathologies:")
    for i, pathology in enumerate(NIHCollector.PATHOLOGY_CLASSES, 1):
        print(f"      {i}. {pathology}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='NIH Dataset Collector')
    parser.add_argument('--download-labels', action='store_true', help='Download labels only')
    parser.add_argument('--parse-labels', action='store_true', help='Parse labels')
    parser.add_argument('--create-split', action='store_true', help='Create train/val/test split')
    parser.add_argument('--recommended', action='store_true', help='Show recommended datasets')
    parser.add_argument('--output', type=str, default='datasets/nih', help='Output directory')
    
    args = parser.parse_args()
    
    collector = NIHCollector(output_dir=args.output)
    
    if args.recommended:
        print_recommended_datasets()
    
    elif args.download_labels:
        collector.download_labels()
    
    elif args.parse_labels:
        df = collector.parse_labels()
        if df is not None:
            print(f"\n{df.head()}")
    
    elif args.create_split:
        splits = collector.create_training_split()
    
    else:
        parser.print_help()

