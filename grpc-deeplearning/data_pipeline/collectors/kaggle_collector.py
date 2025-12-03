"""
Kaggle Medical Imaging Dataset Collector
Télécharge des datasets DICOM depuis Kaggle
"""

import os
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KaggleCollector:
    """
    Collecteur de datasets médicaux depuis Kaggle
    
    Prérequis:
        pip install kaggle
        kaggle API key configurée (~/.kaggle/kaggle.json)
    """
    
    def __init__(self, output_dir: str = "datasets/kaggle"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Vérifier si Kaggle CLI est installé
        try:
            subprocess.run(['kaggle', '--version'], check=True, capture_output=True)
            logger.info("✅ Kaggle CLI found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("❌ Kaggle CLI not found. Install with: pip install kaggle")
            logger.error("   Then configure API key: https://www.kaggle.com/docs/api")
        
        logger.info(f"Kaggle Collector initialized: {self.output_dir}")
    
    def search_datasets(self, query: str = "medical imaging") -> List[Dict]:
        """
        Rechercher des datasets sur Kaggle
        
        Args:
            query: Search query
        
        Returns:
            List of datasets
        """
        logger.info(f"Searching Kaggle for: {query}")
        
        try:
            result = subprocess.run(
                ['kaggle', 'datasets', 'list', '-s', query, '--sort-by', 'hottest'],
                check=True,
                capture_output=True,
                text=True
            )
            
            # Parse output
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            datasets = []
            
            for line in lines[:10]:  # First 10 results
                parts = line.split()
                if len(parts) >= 2:
                    datasets.append({
                        'ref': parts[0],
                        'title': ' '.join(parts[1:])
                    })
            
            logger.info(f"Found {len(datasets)} datasets")
            
            for ds in datasets:
                print(f"   📦 {ds['ref']}")
                print(f"      {ds['title']}")
            
            return datasets
        
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def download_dataset(
        self,
        dataset_ref: str,
        unzip: bool = True
    ):
        """
        Télécharger un dataset Kaggle
        
        Args:
            dataset_ref: Dataset reference (e.g., "paultimothymooney/chest-xray-pneumonia")
            unzip: Unzip after download
        """
        logger.info(f"Downloading Kaggle dataset: {dataset_ref}")
        
        dataset_dir = self.output_dir / dataset_ref.replace('/', '_')
        dataset_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Download
            cmd = ['kaggle', 'datasets', 'download', '-d', dataset_ref, '-p', str(dataset_dir)]
            
            if unzip:
                cmd.append('--unzip')
            
            subprocess.run(cmd, check=True)
            
            logger.info(f"✅ Downloaded to: {dataset_dir}")
            
            return dataset_dir
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Download failed: {e}")
            return None
    
    def download_competition_data(
        self,
        competition_name: str
    ):
        """
        Télécharger les données d'une compétition Kaggle
        
        Args:
            competition_name: Competition name (e.g., "rsna-intracranial-hemorrhage-detection")
        """
        logger.info(f"Downloading competition data: {competition_name}")
        
        comp_dir = self.output_dir / f"competition_{competition_name}"
        comp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            subprocess.run(
                ['kaggle', 'competitions', 'download', '-c', competition_name, '-p', str(comp_dir)],
                check=True
            )
            
            logger.info(f"✅ Downloaded to: {comp_dir}")
            
            return comp_dir
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Download failed: {e}")
            return None


# ============================================
# Datasets Kaggle Recommandés pour IRMSIA
# ============================================

RECOMMENDED_KAGGLE_DATASETS = {
    "brain": [
        {
            "ref": "mateuszbuda/lgg-mri-segmentation",
            "title": "Brain MRI Segmentation (LGG)",
            "description": "IRM cérébrales avec segmentations de gliomes",
            "size_gb": 1.5,
            "images": 3929,
            "format": "DICOM + masks"
        },
        {
            "ref": "navoneel/brain-mri-images-for-brain-tumor-detection",
            "title": "Brain Tumor Detection",
            "description": "IRM cérébrales pour détection de tumeurs",
            "size_gb": 0.3,
            "images": 253,
            "format": "JPG (converti depuis DICOM)"
        }
    ],
    "chest": [
        {
            "ref": "paultimothymooney/chest-xray-pneumonia",
            "title": "Chest X-Ray Pneumonia",
            "description": "5863 X-Rays thoraciques (Pneumonie vs Normal)",
            "size_gb": 2.2,
            "images": 5863,
            "format": "JPG"
        },
        {
            "ref": "nih-chest-xrays/data",
            "title": "NIH Chest X-rays",
            "description": "112,120 X-Rays avec 14 pathologies",
            "size_gb": 42,
            "images": 112120,
            "format": "PNG"
        }
    ],
    "covid": [
        {
            "ref": "tawsifurrahman/covid19-radiography-database",
            "title": "COVID-19 Radiography",
            "description": "X-Rays COVID-19, Pneumonie virale, Normal",
            "size_gb": 1.2,
            "images": 21165,
            "format": "PNG"
        }
    ]
}


RECOMMENDED_KAGGLE_COMPETITIONS = [
    {
        "name": "rsna-intracranial-hemorrhage-detection",
        "title": "RSNA Intracranial Hemorrhage Detection",
        "description": "Détection d'hémorragie intracrânienne",
        "format": "DICOM",
        "size_gb": 70,
        "images": 752803
    },
    {
        "name": "rsna-pneumonia-detection-challenge",
        "title": "RSNA Pneumonia Detection",
        "description": "Détection de pneumonie sur X-Rays",
        "format": "DICOM",
        "size_gb": 25,
        "images": 30000
    },
    {
        "name": "rsna-breast-cancer-detection",
        "title": "RSNA Breast Cancer Detection",
        "description": "Détection cancer du sein (mammographie)",
        "format": "DICOM",
        "size_gb": 300,
        "images": 54706
    }
]


def print_recommended_datasets():
    """Afficher les datasets recommandés"""
    print("\n" + "="*70)
    print("RECOMMENDED KAGGLE DATASETS FOR IRMSIA")
    print("="*70)
    
    for category, datasets in RECOMMENDED_KAGGLE_DATASETS.items():
        print(f"\n📂 {category.upper()}:")
        for ds in datasets:
            print(f"\n   🔹 {ds['title']}")
            print(f"      Ref: {ds['ref']}")
            print(f"      {ds['description']}")
            print(f"      Images: {ds['images']:,}")
            print(f"      Size: ~{ds['size_gb']}GB")
            print(f"      Format: {ds['format']}")
    
    print(f"\n\n📊 KAGGLE COMPETITIONS (DICOM):")
    for comp in RECOMMENDED_KAGGLE_COMPETITIONS:
        print(f"\n   🏆 {comp['title']}")
        print(f"      Name: {comp['name']}")
        print(f"      {comp['description']}")
        print(f"      Images: {comp['images']:,}")
        print(f"      Size: ~{comp['size_gb']}GB")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Kaggle Medical Imaging Collector')
    parser.add_argument('--search', type=str, help='Search datasets')
    parser.add_argument('--download', type=str, help='Download dataset (ref)')
    parser.add_argument('--competition', type=str, help='Download competition data')
    parser.add_argument('--recommended', action='store_true', help='Show recommended datasets')
    parser.add_argument('--output', type=str, default='datasets/kaggle', help='Output directory')
    
    args = parser.parse_args()
    
    collector = KaggleCollector(output_dir=args.output)
    
    if args.recommended:
        print_recommended_datasets()
    
    elif args.search:
        collector.search_datasets(args.search)
    
    elif args.download:
        collector.download_dataset(args.download)
    
    elif args.competition:
        collector.download_competition_data(args.competition)
    
    else:
        parser.print_help()

