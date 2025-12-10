"""
Organisation de Datasets pour Détection d'Anomalies Généraliste
Système complet pour organiser données étiquetées et non-étiquetées
Objectif: Détecteur d'anomalies sur tout le corps humain
"""

import sys
import io
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from tqdm import tqdm
import json
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from collections import defaultdict
import shutil

# Fix Windows encoding
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class AnomalyDetectionOrganizer:
    """
    Organisateur de datasets pour détection d'anomalies
    
    Fonctionnalités:
    - Classification automatique: étiqueté vs non-étiqueté
    - Organisation par région anatomique (cerveau, poumons, abdomen, etc.)
    - Organisation par modalité (CT, MRI, X-Ray)
    - Détection d'anomalies dans images non-étiquetées
    - Création de datasets équilibrés (normal/anomalie)
    """
    
    # Régions anatomiques détectables
    ANATOMICAL_REGIONS = {
        'brain': ['brain', 'cerebral', 'cranial', 'head', 'skull', 'tcga'],
        'chest': ['chest', 'lung', 'pulmonary', 'thoracic', 'pneumonia', 'covid'],
        'abdomen': ['abdomen', 'liver', 'kidney', 'stomach', 'pancreas'],
        'bone': ['bone', 'fracture', 'skeletal', 'spine', 'vertebral'],
        'cardiac': ['heart', 'cardiac', 'cardio', 'coronary'],
        'other': []  # Catch-all
    }
    
    # Modalités d'imagerie
    MODALITIES = {
        'xray': ['xray', 'x-ray', 'radiograph', 'radiography'],
        'ct': ['ct', 'computed', 'tomography'],
        'mri': ['mri', 'magnetic', 'resonance'],
        'ultrasound': ['ultrasound', 'echo', 'sonography'],
        'other': []
    }
    
    # Types d'anomalies connues
    ANOMALY_TYPES = {
        'tumor': ['tumor', 'tumour', 'cancer', 'malignant', 'mass', 'lesion', 'glioma'],
        'infection': ['pneumonia', 'covid', 'infection', 'inflammatory'],
        'fracture': ['fracture', 'break', 'crack'],
        'hemorrhage': ['hemorrhage', 'bleeding', 'blood'],
        'other_anomaly': ['anomaly', 'abnormal', 'pathology']
    }
    
    def __init__(self, base_dir: str = "datasets"):
        self.base_dir = Path(base_dir)
        self.anomaly_dir = self.base_dir / "anomaly_detection"
        self.anomaly_dir.mkdir(parents=True, exist_ok=True)
        
        # Créer la structure
        self.labeled_dir = self.anomaly_dir / "labeled"
        self.unlabeled_dir = self.anomaly_dir / "unlabeled"
        self.organized_dir = self.anomaly_dir / "organized"
        
        for d in [self.labeled_dir, self.unlabeled_dir, self.organized_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def detect_anatomical_region(self, text: str) -> str:
        """
        Détecter la région anatomique depuis le texte
        """
        text_lower = text.lower()
        
        for region, keywords in self.ANATOMICAL_REGIONS.items():
            if region == 'other':
                continue
            for keyword in keywords:
                if keyword in text_lower:
                    return region
        
        return 'other'
    
    def detect_modality(self, text: str) -> str:
        """
        Détecter la modalité d'imagerie
        """
        text_lower = text.lower()
        
        for modality, keywords in self.MODALITIES.items():
            if modality == 'other':
                continue
            for keyword in keywords:
                if keyword in text_lower:
                    return modality
        
        return 'other'
    
    def detect_anomaly_type(self, text: str) -> Optional[str]:
        """
        Détecter le type d'anomalie
        """
        text_lower = text.lower()
        
        for anomaly_type, keywords in self.ANOMALY_TYPES.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return anomaly_type
        
        return None
    
    def classify_labeled_vs_unlabeled(self, csv_file: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Séparer données étiquetées et non-étiquetées
        
        Critères:
        - Étiqueté: a une colonne 'label' ou 'has_tumor' ou 'mask_path' non-null
        - Non-étiqueté: pas de label clair
        """
        df = pd.read_csv(csv_file)
        
        print(f"\n📊 Classification Étiqueté/Non-étiqueté:")
        print(f"   Total: {len(df)} images")
        
        # Détecter les colonnes de labels
        label_columns = [col for col in df.columns if 'label' in col.lower() or 'class' in col.lower()]
        
        if label_columns:
            labeled_df = df[df[label_columns[0]].notna()].copy()
            unlabeled_df = df[df[label_columns[0]].isna()].copy()
        elif 'mask_path' in df.columns:
            labeled_df = df[df['mask_path'].notna()].copy()
            unlabeled_df = df[df['mask_path'].isna()].copy()
        elif 'has_tumor' in df.columns:
            labeled_df = df.copy()  # Tout est étiqueté
            unlabeled_df = pd.DataFrame()
        else:
            # Tout est considéré non-étiqueté
            labeled_df = pd.DataFrame()
            unlabeled_df = df.copy()
        
        print(f"   ✅ Étiquetées: {len(labeled_df)}")
        print(f"   ⚠️  Non-étiquetées: {len(unlabeled_df)}")
        
        return labeled_df, unlabeled_df
    
    def organize_by_anatomy_and_modality(self, df: pd.DataFrame, is_labeled: bool = True) -> pd.DataFrame:
        """
        Organiser par région anatomique et modalité
        """
        print(f"\n🔍 Organisation par anatomie et modalité...")
        
        organized_data = []
        
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Classification"):
            # Extraire info du chemin et autres colonnes
            path = row.get('image_path', row.get('path', ''))
            patient_id = row.get('patient_id', 'unknown')
            
            # Combiner toutes les infos textuelles
            text_info = f"{path} {patient_id}"
            if 'label' in row:
                text_info += f" {row['label']}"
            
            # Détecter région et modalité
            region = self.detect_anatomical_region(text_info)
            modality = self.detect_modality(text_info)
            
            # Détecter type d'anomalie (si étiqueté)
            anomaly_type = None
            if is_labeled:
                anomaly_type = self.detect_anomaly_type(text_info)
            
            # Ajouter à la liste
            organized_row = row.to_dict()
            organized_row.update({
                'anatomical_region': region,
                'modality': modality,
                'anomaly_type': anomaly_type if is_labeled else 'unknown',
                'is_labeled': 1 if is_labeled else 0,
                'is_normal': 0 if anomaly_type else 1  # Assume normal si pas d'anomalie détectée
            })
            
            organized_data.append(organized_row)
        
        organized_df = pd.DataFrame(organized_data)
        
        # Statistiques
        print(f"\n📈 Statistiques d'organisation:")
        print(f"\n   Régions anatomiques:")
        for region, count in organized_df['anatomical_region'].value_counts().items():
            print(f"      {region}: {count}")
        
        print(f"\n   Modalités:")
        for modality, count in organized_df['modality'].value_counts().items():
            print(f"      {modality}: {count}")
        
        if is_labeled:
            print(f"\n   Types d'anomalies:")
            for anom_type, count in organized_df['anomaly_type'].value_counts().items():
                if anom_type:
                    print(f"      {anom_type}: {count}")
        
        return organized_df
    
    def create_balanced_anomaly_dataset(
        self,
        labeled_df: pd.DataFrame,
        unlabeled_df: pd.DataFrame,
        samples_per_region: int = 500
    ) -> Dict[str, pd.DataFrame]:
        """
        Créer des datasets équilibrés pour chaque région anatomique
        
        Stratégie:
        - Données étiquetées: pour training supervisé
        - Données non-étiquetées: pour training semi-supervisé / anomaly detection
        """
        print(f"\n" + "="*70)
        print(f"CRÉATION DE DATASETS ÉQUILIBRÉS PAR RÉGION")
        print(f"Échantillons par région: {samples_per_region}")
        print("="*70)
        
        datasets = {}
        
        # Pour chaque région anatomique
        for region in self.ANATOMICAL_REGIONS.keys():
            if region == 'other':
                continue
            
            print(f"\n🔹 Région: {region.upper()}")
            
            # Filtrer par région
            labeled_region = labeled_df[labeled_df['anatomical_region'] == region]
            unlabeled_region = unlabeled_df[unlabeled_df['anatomical_region'] == region]
            
            if len(labeled_region) == 0 and len(unlabeled_region) == 0:
                print(f"   ⚠️  Aucune donnée pour cette région")
                continue
            
            print(f"   Étiquetées: {len(labeled_region)}")
            print(f"   Non-étiquetées: {len(unlabeled_region)}")
            
            # Échantillonner
            if len(labeled_region) > 0:
                n_labeled = min(len(labeled_region), samples_per_region)
                sampled_labeled = labeled_region.sample(n=n_labeled, random_state=42)
            else:
                sampled_labeled = pd.DataFrame()
            
            if len(unlabeled_region) > 0:
                n_unlabeled = min(len(unlabeled_region), samples_per_region)
                sampled_unlabeled = unlabeled_region.sample(n=n_unlabeled, random_state=42)
            else:
                sampled_unlabeled = pd.DataFrame()
            
            # Combiner
            combined = pd.concat([sampled_labeled, sampled_unlabeled], ignore_index=True)
            
            # Créer splits (70/15/15)
            train_df, temp_df = train_test_split(combined, test_size=0.3, random_state=42)
            val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42)
            
            datasets[region] = {
                'train': train_df,
                'val': val_df,
                'test': test_df,
                'all': combined
            }
            
            print(f"   ✅ Dataset créé:")
            print(f"      Train: {len(train_df)} ({len(train_df[train_df['is_labeled']==1])} étiquetées)")
            print(f"      Val: {len(val_df)}")
            print(f"      Test: {len(test_df)}")
        
        return datasets
    
    def save_organized_datasets(
        self,
        datasets: Dict[str, Dict[str, pd.DataFrame]],
        output_name: str = "anomaly_detection_organized"
    ):
        """
        Sauvegarder les datasets organisés
        """
        print(f"\n💾 Sauvegarde des datasets organisés...")
        
        output_dir = self.organized_dir / output_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            'dataset_name': output_name,
            'description': 'Multi-organ anomaly detection dataset',
            'regions': {},
            'total_images': 0,
            'labeled_images': 0,
            'unlabeled_images': 0
        }
        
        for region, splits in datasets.items():
            region_dir = output_dir / region
            region_dir.mkdir(parents=True, exist_ok=True)
            
            # Sauvegarder chaque split
            splits['train'].to_csv(region_dir / 'train.csv', index=False)
            splits['val'].to_csv(region_dir / 'val.csv', index=False)
            splits['test'].to_csv(region_dir / 'test.csv', index=False)
            splits['all'].to_csv(region_dir / 'full_dataset.csv', index=False)
            
            # Metadata par région
            region_metadata = {
                'total': len(splits['all']),
                'train': len(splits['train']),
                'val': len(splits['val']),
                'test': len(splits['test']),
                'labeled': int(splits['all']['is_labeled'].sum()),
                'unlabeled': int((splits['all']['is_labeled'] == 0).sum())
            }
            
            metadata['regions'][region] = region_metadata
            metadata['total_images'] += region_metadata['total']
            metadata['labeled_images'] += region_metadata['labeled']
            metadata['unlabeled_images'] += region_metadata['unlabeled']
            
            print(f"   ✅ {region}: {len(splits['all'])} images")
        
        # Sauvegarder metadata global
        with open(output_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✅ Datasets sauvegardés: {output_dir}")
        print(f"\n📊 Résumé global:")
        print(f"   Total images: {metadata['total_images']}")
        print(f"   Étiquetées: {metadata['labeled_images']}")
        print(f"   Non-étiquetées: {metadata['unlabeled_images']}")
        
        return output_dir
    
    def generate_training_config(self, datasets_dir: Path):
        """
        Générer configuration pour training
        """
        config = {
            'approach': 'semi-supervised_anomaly_detection',
            'architecture': {
                'supervised': {
                    'model': 'EfficientNet-B4',
                    'task': 'multi-class classification',
                    'classes': list(self.ANOMALY_TYPES.keys())
                },
                'unsupervised': {
                    'model': 'Autoencoder',
                    'task': 'reconstruction',
                    'anomaly_threshold': 'adaptive'
                },
                'hybrid': {
                    'model': 'Feature Extractor + Anomaly Detector',
                    'strategy': 'use labeled for features, unlabeled for normality baseline'
                }
            },
            'training_strategy': {
                'phase_1': 'Train on labeled data (supervised)',
                'phase_2': 'Train autoencoder on normal images',
                'phase_3': 'Fine-tune on semi-supervised approach',
                'phase_4': 'Ensemble supervised + unsupervised'
            },
            'regions': {},
            'datasets_path': str(datasets_dir)
        }
        
        # Ajouter config par région
        for region_dir in datasets_dir.iterdir():
            if region_dir.is_dir():
                config['regions'][region_dir.name] = {
                    'train_csv': str(region_dir / 'train.csv'),
                    'val_csv': str(region_dir / 'val.csv'),
                    'test_csv': str(region_dir / 'test.csv')
                }
        
        config_file = datasets_dir / 'training_config.json'
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✅ Configuration de training: {config_file}")
        
        return config


def main():
    """
    Menu interactif pour organisation de datasets pour anomaly detection
    """
    
    print("\n" + "="*70)
    print("ORGANISATION POUR DÉTECTION D'ANOMALIES GÉNÉRALISTE")
    print("Objectif: Détecteur d'anomalies multi-organes")
    print("="*70)
    
    organizer = AnomalyDetectionOrganizer()
    
    while True:
        print("\n" + "="*70)
        print("MENU PRINCIPAL")
        print("="*70)
        print("\n1. Organiser un dataset (classification auto étiqueté/non-étiqueté)")
        print("2. Créer datasets équilibrés par région anatomique")
        print("3. Voir les datasets organisés")
        print("4. Générer configuration de training")
        print("5. Workflow complet (auto)")
        print("6. Quitter")
        
        choice = input("\nVotre choix (1-6): ").strip()
        
        if choice == '1':
            csv_file = input("\nChemin du CSV structuré: ").strip()
            
            if not Path(csv_file).exists():
                print(f"❌ Fichier non trouvé: {csv_file}")
                continue
            
            # Classifier
            labeled_df, unlabeled_df = organizer.classify_labeled_vs_unlabeled(csv_file)
            
            # Organiser chaque partie
            if len(labeled_df) > 0:
                labeled_org = organizer.organize_by_anatomy_and_modality(labeled_df, is_labeled=True)
                labeled_org.to_csv(organizer.labeled_dir / 'labeled_organized.csv', index=False)
                print(f"\n✅ Étiquetées: {organizer.labeled_dir / 'labeled_organized.csv'}")
            
            if len(unlabeled_df) > 0:
                unlabeled_org = organizer.organize_by_anatomy_and_modality(unlabeled_df, is_labeled=False)
                unlabeled_org.to_csv(organizer.unlabeled_dir / 'unlabeled_organized.csv', index=False)
                print(f"✅ Non-étiquetées: {organizer.unlabeled_dir / 'unlabeled_organized.csv'}")
        
        elif choice == '2':
            labeled_file = organizer.labeled_dir / 'labeled_organized.csv'
            unlabeled_file = organizer.unlabeled_dir / 'unlabeled_organized.csv'
            
            if not labeled_file.exists() and not unlabeled_file.exists():
                print(f"❌ Organisez d'abord les données (option 1)")
                continue
            
            labeled_df = pd.read_csv(labeled_file) if labeled_file.exists() else pd.DataFrame()
            unlabeled_df = pd.read_csv(unlabeled_file) if unlabeled_file.exists() else pd.DataFrame()
            
            samples = input("\nÉchantillons par région (défaut: 500): ").strip()
            samples_per_region = int(samples) if samples.isdigit() else 500
            
            datasets = organizer.create_balanced_anomaly_dataset(
                labeled_df,
                unlabeled_df,
                samples_per_region=samples_per_region
            )
            
            output_dir = organizer.save_organized_datasets(datasets)
            organizer.generate_training_config(output_dir)
        
        elif choice == '3':
            print(f"\n📂 Datasets organisés:")
            
            if list(organizer.organized_dir.glob('*')):
                for dataset_dir in organizer.organized_dir.iterdir():
                    if dataset_dir.is_dir():
                        metadata_file = dataset_dir / 'metadata.json'
                        if metadata_file.exists():
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                            
                            print(f"\n   🔹 {dataset_dir.name}")
                            print(f"      Total: {metadata['total_images']}")
                            print(f"      Étiquetées: {metadata['labeled_images']}")
                            print(f"      Non-étiquetées: {metadata['unlabeled_images']}")
                            print(f"      Régions: {', '.join(metadata['regions'].keys())}")
            else:
                print(f"\n   ❌ Aucun dataset organisé")
        
        elif choice == '4':
            dataset_name = input("\nNom du dataset: ").strip()
            dataset_dir = organizer.organized_dir / dataset_name
            
            if dataset_dir.exists():
                config = organizer.generate_training_config(dataset_dir)
            else:
                print(f"❌ Dataset non trouvé: {dataset_dir}")
        
        elif choice == '5':
            # Workflow complet
            print(f"\n🚀 WORKFLOW COMPLET")
            
            csv_file = input("\nChemin du CSV de base: ").strip()
            
            if not Path(csv_file).exists():
                print(f"❌ Fichier non trouvé")
                continue
            
            # Étape 1: Classification
            labeled_df, unlabeled_df = organizer.classify_labeled_vs_unlabeled(csv_file)
            
            # Étape 2: Organisation
            labeled_org = organizer.organize_by_anatomy_and_modality(labeled_df, True) if len(labeled_df) > 0 else pd.DataFrame()
            unlabeled_org = organizer.organize_by_anatomy_and_modality(unlabeled_df, False) if len(unlabeled_df) > 0 else pd.DataFrame()
            
            # Étape 3: Datasets équilibrés
            if len(labeled_org) > 0 or len(unlabeled_org) > 0:
                datasets = organizer.create_balanced_anomaly_dataset(labeled_org, unlabeled_org, 500)
                output_dir = organizer.save_organized_datasets(datasets)
                organizer.generate_training_config(output_dir)
                
                print(f"\n✅ Workflow terminé!")
                print(f"   Datasets: {output_dir}")
        
        elif choice == '6':
            print("\n👋 Au revoir!")
            break
        
        else:
            print("❌ Choix invalide")


if __name__ == "__main__":
    main()

