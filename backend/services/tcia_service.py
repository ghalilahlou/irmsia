"""
Service de téléchargement depuis TCIA (The Cancer Imaging Archive)
Télécharge 10 fichiers DICOM d'exemple depuis TCIA
"""

import os
import logging
import requests
from pathlib import Path
from typing import List, Dict, Optional
import zipfile
import io
import pydicom
from pydicom.dataset import FileDataset
from pydicom.uid import generate_uid
import numpy as np
from datetime import datetime

from backend.core.config import settings
from backend.services.dicom_converter import dicom_converter

logger = logging.getLogger(__name__)


class TCIAService:
    """Service pour télécharger des fichiers DICOM depuis TCIA"""
    
    def __init__(self):
        self.dicom_dir = Path(settings.UPLOAD_DIR) / "dicom"
        self.dicom_dir.mkdir(parents=True, exist_ok=True)
    
    def download_sample_dicoms(self, count: int = 10) -> List[Dict[str, str]]:
        """
        Télécharge des fichiers DICOM d'exemple depuis TCIA
        
        Args:
            count: Nombre de fichiers à télécharger (max 10)
            
        Returns:
            Liste des fichiers téléchargés avec leurs métadonnées
        """
        downloaded_files = []
        
        # URLs d'exemple de fichiers DICOM publics (utiliser des datasets publics TCIA)
        # Note: En production, utiliser l'API TCIA officielle avec authentification
        sample_urls = [
            # Exemples de datasets publics TCIA (remplacer par de vrais URLs si disponibles)
            # Pour l'instant, on génère des fichiers de test
            "https://www.cancerimagingarchive.net/nbia-search/",
        ]
        
        logger.info(f"Téléchargement de {count} fichiers DICOM depuis TCIA...")
        
        # Pour l'instant, créer des fichiers DICOM de test valides
        # En production, utiliser l'API TCIA réelle
        try:
            import pydicom
            from pydicom.dataset import Dataset, FileDataset
            from pydicom.uid import generate_uid
            import numpy as np
            from datetime import datetime
            
            for i in range(min(count, 10)):
                # Créer un fichier DICOM de test minimal mais valide
                # En production, télécharger depuis TCIA
                test_filename = f"tcia_sample_{i+1:02d}.dcm"
                test_path = self.dicom_dir / test_filename
                
                # Note: Ceci est un placeholder avec un DICOM valide minimal
                # Pour une vraie implémentation, utiliser:
                # - L'API TCIA: https://wiki.cancerimagingarchive.net/display/Public/TCIA+Programmatic+Interface+%28REST+API%29
                # - Ou télécharger depuis des collections publiques
                
                logger.warning(f"Mode placeholder: création de fichier DICOM de test {test_filename}")
                logger.info("Pour une implémentation complète, intégrer l'API TCIA officielle")
                
                # Créer un dataset DICOM minimal mais valide
                ds = FileDataset(test_filename, {}, file_meta=None, preamble=b"\x00" * 128)
                
                # Métadonnées DICOM minimales requises
                ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.1"  # CR Image Storage
                ds.SOPInstanceUID = generate_uid()
                ds.StudyInstanceUID = generate_uid()
                ds.SeriesInstanceUID = generate_uid()
                ds.Modality = "CR"
                ds.PatientID = f"TCIA_TEST_{i+1:02d}"
                ds.PatientName = f"Test^Patient^{i+1:02d}"
                ds.StudyDate = datetime.now().strftime("%Y%m%d")
                ds.StudyTime = datetime.now().strftime("%H%M%S")
                ds.SeriesDate = datetime.now().strftime("%Y%m%d")
                ds.SeriesTime = datetime.now().strftime("%H%M%S")
                ds.InstanceNumber = i + 1
                
                # Créer une image de test réaliste avec un pattern UNIQUE pour chaque fichier
                # Utiliser un seed différent pour chaque fichier pour garantir l'unicité
                np.random.seed(42 + i * 100)  # Seed différent pour chaque fichier
                
                # Augmenter la résolution pour plus de détails
                rows, cols = 1024, 1024  # Augmenté de 512x512 à 1024x1024 pour plus de pixels
                max_value = 4095
                
                y, x = np.ogrid[:rows, :cols]
                center_x, center_y = cols // 2, rows // 2
                
                # Pattern 1: Cercles concentriques - fréquence unique par fichier
                distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                circle_freq = 10 + (i * 5)  # Fréquence très différente (10, 15, 20, 25, etc.)
                circle_pattern = (np.sin(distance / circle_freq) * 0.5 + 0.5) * max_value
                
                # Pattern 2: Gradient radial avec décalage unique
                radial_gradient = distance / distance.max() * max_value
                offset = i * 200  # Décalage différent pour chaque fichier
                radial_pattern = ((radial_gradient + offset) % max_value)
                
                # Pattern 3: Lignes horizontales/verticales alternées selon l'index
                if i % 2 == 0:
                    # Lignes horizontales
                    line_pattern = ((y // (20 + i * 3)) % 2).astype(float) * max_value * 0.5
                else:
                    # Lignes verticales
                    line_pattern = ((x // (20 + i * 3)) % 2).astype(float) * max_value * 0.5
                
                # Pattern 4: Formes géométriques différentes selon l'index
                shape_type = i % 4
                if shape_type == 0:
                    # Carré au centre
                    shape = ((np.abs(x - center_x) < (50 + i * 10)) & (np.abs(y - center_y) < (50 + i * 10))).astype(float) * max_value * 0.3
                elif shape_type == 1:
                    # Cercle
                    shape = (distance < (40 + i * 8)).astype(float) * max_value * 0.3
                elif shape_type == 2:
                    # Losange
                    shape = ((np.abs(x - center_x) + np.abs(y - center_y)) < (60 + i * 10)).astype(float) * max_value * 0.3
                else:
                    # Croix
                    shape = ((np.abs(x - center_x) < (30 + i * 5)) | (np.abs(y - center_y) < (30 + i * 5))).astype(float) * max_value * 0.3
                
                # Combiner les patterns avec des poids différents selon l'index
                weight1 = 0.3 + (i % 3) * 0.1
                weight2 = 0.2 + ((i + 1) % 3) * 0.1
                weight3 = 0.2 + ((i + 2) % 3) * 0.1
                weight4 = 0.3 - (i % 3) * 0.1
                
                pattern = (
                    circle_pattern * weight1 +
                    radial_pattern * weight2 +
                    line_pattern * weight3 +
                    shape * weight4
                )
                
                # Ajouter un peu de texture (seedé pour être reproductible mais différent)
                noise_std = max_value * (0.02 + (i % 5) * 0.01)
                noise = np.random.normal(0, noise_std, (rows, cols))
                pattern = np.clip(pattern + noise, 0, max_value)
                
                # Convertir en uint16
                pixel_array = pattern.astype(np.uint16)
                
                # Vérifier que l'image a vraiment des variations
                if pixel_array.std() < max_value * 0.05:
                    # Ajouter un pattern de secours
                    checker = ((x // (30 + i * 5) + y // (30 + i * 5)) % 2).astype(float) * max_value * 0.4
                    pixel_array = np.clip(pixel_array.astype(float) + checker, 0, max_value).astype(np.uint16)
                
                # Log pour debug
                logger.info(f"Fichier {test_filename}: shape={pixel_array.shape}, min={pixel_array.min()}, max={pixel_array.max()}, std={pixel_array.std():.2f}, unique={len(np.unique(pixel_array))}")
                
                # Encoder les pixels correctement pour pydicom
                ds.PixelData = pixel_array.tobytes()
                ds.Rows = rows
                ds.Columns = cols
                ds.BitsAllocated = 16
                ds.BitsStored = 12  # Utiliser 12 bits (plus réaliste pour DICOM médical)
                ds.HighBit = 11
                ds.PixelRepresentation = 0  # Unsigned
                ds.SamplesPerPixel = 1
                ds.PhotometricInterpretation = "MONOCHROME2"
                ds.PlanarConfiguration = 0
                
                # Ajouter des métadonnées de fenêtrage pour l'affichage
                ds.WindowCenter = max_value // 2
                ds.WindowWidth = max_value
                
                # Sauvegarder le fichier DICOM
                ds.save_as(test_path, write_like_original=False)
                
                file_size = test_path.stat().st_size
                
                downloaded_files.append({
                    "filename": test_filename,
                    "status": "created",
                    "size": file_size,
                    "message": f"Fichier DICOM de test créé ({file_size / 1024:.2f} KB). Intégrer l'API TCIA pour télécharger de vrais fichiers."
                })
            
            logger.info(f"{len(downloaded_files)} fichiers créés (mode placeholder)")
            
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement depuis TCIA: {e}")
            raise
        
        return downloaded_files
    
    def download_from_tcia_api(
        self,
        collection_id: str,
        patient_id: Optional[str] = None,
        study_id: Optional[str] = None,
        series_id: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Télécharge des fichiers depuis l'API TCIA officielle
        
        Args:
            collection_id: ID de la collection TCIA
            patient_id: ID du patient (optionnel)
            study_id: ID de l'étude (optionnel)
            series_id: ID de la série (optionnel)
            
        Returns:
            Liste des fichiers téléchargés
        """
        # TODO: Implémenter l'intégration avec l'API TCIA
        # Documentation: https://wiki.cancerimagingarchive.net/display/Public/TCIA+Programmatic+Interface+%28REST+API%29
        
        logger.info("Intégration API TCIA à implémenter")
        logger.info("Voir: https://wiki.cancerimagingarchive.net/display/Public/TCIA+Programmatic+Interface")
        
        return []


# Instance globale
tcia_service = TCIAService()

