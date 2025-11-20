"""
Service de gestion DICOM
Upload, dé-identification, conversion PNG, chiffrement
"""

import os
import uuid
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import logging
import pydicom
from pydicom.dataset import Dataset
from pydicom.sequence import Sequence
import numpy as np
from PIL import Image
import io

from backend.core.config import settings
from backend.core.security import security_manager
from backend.models.dto import DICOMMetadata

logger = logging.getLogger(__name__)


class DICOMService:
    """Service de gestion des fichiers DICOM"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.png_dir = Path(settings.PNG_DIR)
        self.encrypted_dir = Path(settings.ENCRYPTED_DIR)
        
        # Créer les répertoires
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.png_dir.mkdir(parents=True, exist_ok=True)
        self.encrypted_dir.mkdir(parents=True, exist_ok=True)
    
    def upload_dicom(
        self,
        file_content: bytes,
        filename: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Upload et traitement d'un fichier DICOM
        
        Returns:
            Tuple[image_id, metadata]
        """
        image_id = str(uuid.uuid4())
        
        try:
            # 1. Sauvegarder le fichier DICOM original
            dicom_path = self.upload_dir / f"{image_id}.dcm"
            with open(dicom_path, "wb") as f:
                f.write(file_content)
            
            # 2. Charger et dé-identifier
            dataset = pydicom.dcmread(dicom_path)
            deidentified_dataset = self.deidentify_dicom(dataset)
            
            # 3. Convertir en PNG
            png_path = self.png_dir / f"{image_id}.png"
            self.convert_to_png(deidentified_dataset, png_path)
            
            # 4. Chiffrer le PNG
            encrypted_path = self.encrypted_dir / f"{image_id}.enc"
            security_manager.encrypt_file(str(png_path), str(encrypted_path))
            
            # 5. Calculer le hash
            file_hash = security_manager.compute_file_hash(str(encrypted_path))
            
            # 6. Extraire les métadonnées (dé-identifiées)
            metadata = self.extract_metadata(deidentified_dataset)
            
            # Nettoyer le PNG non chiffré (optionnel, pour sécurité)
            if os.path.exists(png_path):
                os.remove(png_path)
            
            return image_id, {
                "hash": file_hash,
                "metadata": metadata,
                "encrypted_path": str(encrypted_path),
                "original_size": len(file_content),
                "encrypted_size": os.path.getsize(encrypted_path)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement DICOM: {e}")
            # Nettoyer en cas d'erreur
            for path in [dicom_path, png_path, encrypted_path]:
                if path and path.exists():
                    path.unlink()
            raise
    
    def deidentify_dicom(self, dataset: Dataset) -> Dataset:
        """
        Dé-identifie un dataset DICOM
        Supprime toutes les informations patient
        """
        # Créer une copie
        deidentified = Dataset()
        deidentified.file_meta = dataset.file_meta
        
        # Tags à supprimer (informations patient)
        tags_to_remove = [
            (0x0010, 0x0010),  # Patient Name
            (0x0010, 0x0020),  # Patient ID
            (0x0010, 0x0021),  # Issuer of Patient ID
            (0x0010, 0x0030),  # Patient Birth Date
            (0x0010, 0x0032),  # Patient Birth Time
            (0x0010, 0x0040),  # Patient Sex
            (0x0010, 0x1000),  # Other Patient IDs
            (0x0010, 0x1001),  # Other Patient Names
            (0x0010, 0x1005),  # Patient Birth Name
            (0x0010, 0x1010),  # Patient Age
            (0x0010, 0x1040),  # Patient Address
            (0x0010, 0x2150),  # Country of Residence
            (0x0010, 0x2152),  # Region of Residence
            (0x0010, 0x2154),  # Patient Telephone Numbers
            (0x0010, 0x2160),  # Ethnic Group
            (0x0010, 0x4000),  # Patient Comments
        ]
        
        # Copier tous les éléments sauf ceux à supprimer
        for element in dataset:
            tag = element.tag
            if tag not in tags_to_remove:
                # Gérer les séquences récursivement
                if element.VR == "SQ":
                    new_sequence = Sequence()
                    for item in element.value:
                        new_item = self.deidentify_dicom(item)
                        new_sequence.append(new_item)
                    deidentified.add_new(tag.group, tag.elem, element.VR, new_sequence)
                else:
                    deidentified.add(element)
        
        # Ajouter un identifiant anonyme
        deidentified.PatientID = f"ANON_{uuid.uuid4().hex[:8]}"
        deidentified.PatientName = "ANONYMOUS"
        
        return deidentified
    
    def convert_to_png(self, dataset: Dataset, output_path: Path) -> None:
        """
        Convertit un dataset DICOM en PNG
        """
        try:
            # Extraire le pixel array
            pixel_array = dataset.pixel_array
            
            # Normaliser les valeurs
            if pixel_array.dtype != np.uint8:
                # Normaliser entre 0 et 255
                pixel_array = pixel_array.astype(np.float32)
                pixel_array = (pixel_array - pixel_array.min()) / (pixel_array.max() - pixel_array.min() + 1e-10)
                pixel_array = (pixel_array * 255).astype(np.uint8)
            
            # Gérer les images multi-couches (prendre la couche du milieu)
            if len(pixel_array.shape) == 3:
                slice_idx = pixel_array.shape[0] // 2
                pixel_array = pixel_array[slice_idx]
            
            # Convertir en PIL Image
            if len(pixel_array.shape) == 2:
                # Image en niveaux de gris
                img = Image.fromarray(pixel_array, mode='L')
            elif len(pixel_array.shape) == 3:
                # Image RGB
                img = Image.fromarray(pixel_array, mode='RGB')
            else:
                raise ValueError(f"Format d'image non supporté: {pixel_array.shape}")
            
            # Sauvegarder en PNG
            img.save(output_path, "PNG")
            logger.info(f"Image convertie en PNG: {output_path}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la conversion PNG: {e}")
            raise
    
    def extract_metadata(self, dataset: Dataset) -> Dict[str, Any]:
        """Extrait les métadonnées DICOM (dé-identifiées)"""
        metadata = {}
        
        try:
            if hasattr(dataset, "Modality"):
                metadata["modality"] = str(dataset.Modality)
            
            if hasattr(dataset, "StudyDate"):
                metadata["study_date"] = str(dataset.StudyDate)
            
            if hasattr(dataset, "StudyTime"):
                metadata["study_time"] = str(dataset.StudyTime)
            
            if hasattr(dataset, "SeriesDescription"):
                metadata["series_description"] = str(dataset.SeriesDescription)
            
            if hasattr(dataset, "ImageType"):
                metadata["image_type"] = str(dataset.ImageType)
            
            if hasattr(dataset, "PixelSpacing"):
                metadata["pixel_spacing"] = [float(x) for x in dataset.PixelSpacing]
            
            if hasattr(dataset, "SliceThickness"):
                metadata["slice_thickness"] = float(dataset.SliceThickness)
            
            if hasattr(dataset, "Rows"):
                metadata["rows"] = int(dataset.Rows)
            
            if hasattr(dataset, "Columns"):
                metadata["columns"] = int(dataset.Columns)
            
        except Exception as e:
            logger.warning(f"Erreur lors de l'extraction des métadonnées: {e}")
        
        return metadata
    
    def get_decrypted_image_path(self, image_id: str) -> Optional[Path]:
        """
        Déchiffre temporairement une image pour analyse
        Retourne le chemin du fichier déchiffré
        """
        encrypted_path = self.encrypted_dir / f"{image_id}.enc"
        
        if not encrypted_path.exists():
            return None
        
        # Créer un fichier temporaire déchiffré
        temp_dir = Path(settings.PNG_DIR) / "temp"
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / f"{image_id}_temp.png"
        
        try:
            security_manager.decrypt_file(str(encrypted_path), str(temp_path))
            return temp_path
        except Exception as e:
            logger.error(f"Erreur lors du déchiffrement: {e}")
            return None
    
    def cleanup_temp_file(self, image_id: str) -> None:
        """Nettoie le fichier temporaire déchiffré"""
        temp_path = Path(settings.PNG_DIR) / "temp" / f"{image_id}_temp.png"
        if temp_path.exists():
            temp_path.unlink()


# Instance globale
dicom_service = DICOMService()

