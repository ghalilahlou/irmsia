"""
TCIA (The Cancer Imaging Archive) Data Collector
Télécharge des datasets DICOM depuis TCIA - Plus grande archive publique d'imagerie médicale
"""

import requests
import json
from pathlib import Path
from typing import List, Dict, Optional
import logging
from tqdm import tqdm
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TCIACollector:
    """
    Collecteur de données depuis TCIA (The Cancer Imaging Archive)
    
    Datasets disponibles:
    - LIDC-IDRI: 1010 patients, nodules pulmonaires annotés
    - BraTS: Tumeurs cérébrales avec segmentations
    - COVID-19: Images thoraciques COVID
    - NSCLC: Cancer du poumon non à petites cellules
    - Et 100+ autres datasets
    """
    
    BASE_URL = "https://services.cancerimagingarchive.net/services/v4/TCIA/query"
    
    def __init__(self, output_dir: str = "datasets/tcia"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        
        logger.info(f"TCIA Collector initialized: {self.output_dir}")
    
    def list_available_collections(self) -> List[Dict]:
        """
        Lister toutes les collections disponibles sur TCIA
        
        Returns:
            List of collections with metadata
        """
        logger.info("Fetching available TCIA collections...")
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/getCollectionValues",
                params={"format": "json"}
            )
            response.raise_for_status()
            
            collections = response.json()
            
            logger.info(f"Found {len(collections)} collections")
            
            return collections
        
        except Exception as e:
            logger.error(f"Failed to fetch collections: {e}")
            return []
    
    def get_collection_info(self, collection_name: str) -> Dict:
        """
        Obtenir les informations détaillées d'une collection
        
        Args:
            collection_name: Nom de la collection
        
        Returns:
            Dict with collection metadata
        """
        logger.info(f"Fetching info for collection: {collection_name}")
        
        try:
            # Get patients
            response = self.session.get(
                f"{self.BASE_URL}/getPatient",
                params={
                    "Collection": collection_name,
                    "format": "json"
                }
            )
            response.raise_for_status()
            patients = response.json()
            
            # Get series count
            response = self.session.get(
                f"{self.BASE_URL}/getSeries",
                params={
                    "Collection": collection_name,
                    "format": "json"
                }
            )
            response.raise_for_status()
            series = response.json()
            
            info = {
                "collection": collection_name,
                "num_patients": len(patients),
                "num_series": len(series),
                "modalities": list(set(s.get("Modality", "UNKNOWN") for s in series)),
                "body_parts": list(set(s.get("BodyPartExamined", "UNKNOWN") for s in series))
            }
            
            logger.info(f"Collection {collection_name}:")
            logger.info(f"  Patients: {info['num_patients']}")
            logger.info(f"  Series: {info['num_series']}")
            logger.info(f"  Modalities: {info['modalities']}")
            
            return info
        
        except Exception as e:
            logger.error(f"Failed to fetch collection info: {e}")
            return {}
    
    def download_collection(
        self,
        collection_name: str,
        max_patients: Optional[int] = None,
        modality: Optional[str] = None
    ):
        """
        Télécharger une collection complète
        
        Args:
            collection_name: Nom de la collection
            max_patients: Nombre max de patients (None = tous)
            modality: Filtrer par modalité (CT, MR, etc.)
        """
        logger.info(f"Downloading collection: {collection_name}")
        
        # Get patients
        response = self.session.get(
            f"{self.BASE_URL}/getPatient",
            params={
                "Collection": collection_name,
                "format": "json"
            }
        )
        patients = response.json()
        
        if max_patients:
            patients = patients[:max_patients]
        
        logger.info(f"Downloading {len(patients)} patients...")
        
        collection_dir = self.output_dir / collection_name
        collection_dir.mkdir(parents=True, exist_ok=True)
        
        for patient in tqdm(patients, desc="Patients"):
            patient_id = patient["PatientID"]
            
            try:
                self._download_patient(
                    collection_name,
                    patient_id,
                    collection_dir,
                    modality
                )
            except Exception as e:
                logger.error(f"Failed to download patient {patient_id}: {e}")
                continue
            
            # Rate limiting
            time.sleep(0.5)
        
        logger.info(f"✅ Download complete: {collection_dir}")
    
    def _download_patient(
        self,
        collection_name: str,
        patient_id: str,
        output_dir: Path,
        modality: Optional[str]
    ):
        """Télécharger tous les scans d'un patient"""
        
        # Get series for patient
        params = {
            "Collection": collection_name,
            "PatientID": patient_id,
            "format": "json"
        }
        
        if modality:
            params["Modality"] = modality
        
        response = self.session.get(
            f"{self.BASE_URL}/getSeries",
            params=params
        )
        series_list = response.json()
        
        patient_dir = output_dir / patient_id
        patient_dir.mkdir(parents=True, exist_ok=True)
        
        for series in series_list:
            series_uid = series["SeriesInstanceUID"]
            
            # Download series as ZIP
            response = self.session.get(
                f"{self.BASE_URL}/getImage",
                params={
                    "SeriesInstanceUID": series_uid
                },
                stream=True
            )
            
            if response.status_code == 200:
                zip_file = patient_dir / f"{series_uid}.zip"
                
                with open(zip_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Extract ZIP
                import zipfile
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    series_dir = patient_dir / series_uid
                    zip_ref.extractall(series_dir)
                
                # Remove ZIP
                zip_file.unlink()


# ============================================
# Collections Recommandées pour IRMSIA
# ============================================

RECOMMENDED_COLLECTIONS = {
    "brain": [
        {
            "name": "TCGA-GBM",
            "description": "Glioblastome (tumeurs cérébrales)",
            "patients": 262,
            "modality": "MR",
            "size_gb": 50
        },
        {
            "name": "TCGA-LGG",
            "description": "Gliome de bas grade",
            "patients": 199,
            "modality": "MR",
            "size_gb": 40
        }
    ],
    "lung": [
        {
            "name": "LIDC-IDRI",
            "description": "Nodules pulmonaires annotés",
            "patients": 1010,
            "modality": "CT",
            "size_gb": 124,
            "annotations": True
        },
        {
            "name": "NSCLC-Radiomics",
            "description": "Cancer du poumon non à petites cellules",
            "patients": 422,
            "modality": "CT",
            "size_gb": 60
        }
    ],
    "covid": [
        {
            "name": "COVID-19-AR",
            "description": "Images thoraciques COVID-19",
            "patients": 201,
            "modality": "CT",
            "size_gb": 15
        }
    ]
}


def print_recommended_collections():
    """Afficher les collections recommandées"""
    print("\n" + "="*70)
    print("RECOMMENDED TCIA COLLECTIONS FOR IRMSIA")
    print("="*70)
    
    for category, collections in RECOMMENDED_COLLECTIONS.items():
        print(f"\n📂 {category.upper()}:")
        for col in collections:
            print(f"\n   🔹 {col['name']}")
            print(f"      {col['description']}")
            print(f"      Patients: {col['patients']}")
            print(f"      Modality: {col['modality']}")
            print(f"      Size: ~{col['size_gb']}GB")
            if col.get('annotations'):
                print(f"      ✅ Includes annotations")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='TCIA Data Collector')
    parser.add_argument('--list', action='store_true', help='List available collections')
    parser.add_argument('--info', type=str, help='Get info for a collection')
    parser.add_argument('--download', type=str, help='Download a collection')
    parser.add_argument('--max-patients', type=int, help='Max patients to download')
    parser.add_argument('--modality', type=str, help='Filter by modality (CT, MR, etc.)')
    parser.add_argument('--recommended', action='store_true', help='Show recommended collections')
    parser.add_argument('--output', type=str, default='datasets/tcia', help='Output directory')
    
    args = parser.parse_args()
    
    collector = TCIACollector(output_dir=args.output)
    
    if args.recommended:
        print_recommended_collections()
    
    elif args.list:
        collections = collector.list_available_collections()
        print(f"\n📊 Available TCIA Collections: {len(collections)}")
        for col in collections[:20]:  # Show first 20
            print(f"   - {col['Collection']}")
    
    elif args.info:
        info = collector.get_collection_info(args.info)
    
    elif args.download:
        collector.download_collection(
            collection_name=args.download,
            max_patients=args.max_patients,
            modality=args.modality
        )
    
    else:
        parser.print_help()

