"""
Service de conversion DICOM → PNG
Utilise pydicom et Pillow pour la conversion
"""

import os
import logging
from pathlib import Path
from typing import Tuple, Optional
import pydicom
import numpy as np
from PIL import Image, ImageEnhance

from backend.core.config import settings

logger = logging.getLogger(__name__)


class DICOMConverter:
    """Service de conversion DICOM vers PNG"""
    
    def __init__(self):
        self.dicom_dir = Path(settings.UPLOAD_DIR) / "dicom"
        self.png_dir = Path(settings.PNG_DIR)
        
        # Créer les répertoires
        self.dicom_dir.mkdir(parents=True, exist_ok=True)
        self.png_dir.mkdir(parents=True, exist_ok=True)
    
    def is_valid_dicom(self, file_path: Path) -> bool:
        """Vérifie si le fichier est un DICOM valide"""
        try:
            pydicom.dcmread(str(file_path), stop_before_pixels=True)
            return True
        except Exception as e:
            logger.error(f"Fichier DICOM invalide: {e}")
            return False
    
    def convert_to_png(
        self,
        dicom_path: Path,
        output_filename: Optional[str] = None
    ) -> Tuple[str, Path]:
        """
        Convertit un fichier DICOM en PNG
        
        Args:
            dicom_path: Chemin vers le fichier DICOM
            output_filename: Nom du fichier PNG de sortie (optionnel)
            
        Returns:
            Tuple[nom_fichier_png, chemin_complet]
            
        Raises:
            ValueError: Si le fichier n'est pas un DICOM valide
        """
        # Vérifier que le fichier existe
        if not dicom_path.exists():
            raise FileNotFoundError(f"Fichier DICOM non trouvé: {dicom_path}")
        
        # Vérifier que c'est un DICOM valide
        if not self.is_valid_dicom(dicom_path):
            raise ValueError(f"Le fichier {dicom_path.name} n'est pas un DICOM valide")
        
        try:
            # Lire le fichier DICOM
            ds = pydicom.dcmread(str(dicom_path))
            
            # Extraire les pixels
            pixel_array = ds.pixel_array
            
            # Convertir en float32 pour les calculs de précision
            pixel_array = pixel_array.astype(np.float32)
            
            # Appliquer Rescale Slope et Intercept si présents (correction des valeurs)
            if hasattr(ds, 'RescaleSlope') and hasattr(ds, 'RescaleIntercept'):
                try:
                    slope = float(ds.RescaleSlope) if hasattr(ds.RescaleSlope, '__iter__') else float(ds.RescaleSlope)
                    intercept = float(ds.RescaleIntercept) if hasattr(ds.RescaleIntercept, '__iter__') else float(ds.RescaleIntercept)
                    pixel_array = pixel_array * slope + intercept
                    logger.debug(f"Appliqué Rescale: slope={slope}, intercept={intercept}")
                except (ValueError, TypeError):
                    pass
            
            # Appliquer le windowing DICOM si disponible (améliore le contraste)
            windowing_applied = False
            if hasattr(ds, 'WindowCenter') and hasattr(ds, 'WindowWidth'):
                try:
                    window_center = float(ds.WindowCenter) if hasattr(ds.WindowCenter, '__iter__') else float(ds.WindowCenter)
                    window_width = float(ds.WindowWidth) if hasattr(ds.WindowWidth, '__iter__') else float(ds.WindowWidth)
                    
                    window_min = window_center - window_width / 2
                    window_max = window_center + window_width / 2
                    
                    # Appliquer le windowing avec préservation des valeurs
                    pixel_array = np.clip(pixel_array, window_min, window_max)
                    pixel_array = ((pixel_array - window_min) / (window_max - window_min + 1e-10) * 255.0)
                    windowing_applied = True
                    logger.debug(f"Windowing appliqué: center={window_center}, width={window_width}")
                except (ValueError, TypeError):
                    pass
            
            # Normalisation améliorée si windowing non appliqué
            if not windowing_applied:
                pixel_min = float(pixel_array.min())
                pixel_max = float(pixel_array.max())
                
                if pixel_max > pixel_min:
                    # Normalisation min-max avec préservation des détails
                    # Utiliser une normalisation adaptative pour améliorer le contraste
                    pixel_range = pixel_max - pixel_min
                    
                    # Normalisation standard
                    pixel_array = ((pixel_array - pixel_min) / pixel_range * 255.0)
                    
                    # Amélioration du contraste avec étirement adaptatif
                    # Utiliser les percentiles pour éviter l'impact des valeurs extrêmes
                    p2 = np.percentile(pixel_array, 2)
                    p98 = np.percentile(pixel_array, 98)
                    
                    if p98 > p2:
                        # Étirer les valeurs entre p2 et p98 pour améliorer le contraste
                        pixel_array = np.clip((pixel_array - p2) / (p98 - p2) * 255.0, 0, 255)
                    else:
                        pixel_array = np.clip(pixel_array, 0, 255)
                        
                elif pixel_max == pixel_min:
                    # Image uniforme, mettre à une valeur moyenne
                    pixel_array = np.full_like(pixel_array, 128.0)
                else:
                    pixel_array = np.clip(pixel_array, 0, 255)
            
            # Amélioration des détails avec un filtre de netteté léger
            # Utiliser un filtre unsharp mask pour améliorer la netteté
            try:
                from scipy import ndimage
                # Créer un filtre de netteté (unsharp mask)
                blurred = ndimage.gaussian_filter(pixel_array, sigma=1.0)
                sharpened = pixel_array + (pixel_array - blurred) * 0.3  # Facteur de netteté
                pixel_array = np.clip(sharpened, 0, 255)
                logger.debug("Filtre de netteté appliqué")
            except ImportError:
                # Si scipy n'est pas disponible, continuer sans amélioration
                logger.debug("scipy non disponible, netteté non appliquée")
            except Exception as e:
                logger.warning(f"Erreur lors de l'application du filtre de netteté: {e}")
            
            # Convertir en uint8
            pixel_array = pixel_array.astype(np.uint8)
            
            # Gérer les images multi-couches (prendre la première couche)
            if len(pixel_array.shape) == 3:
                pixel_array = pixel_array[0]
            elif len(pixel_array.shape) > 3:
                pixel_array = pixel_array[0, 0]
            
            # Convertir en image PIL
            if len(pixel_array.shape) == 2:
                # Image en niveaux de gris
                image = Image.fromarray(pixel_array, mode='L')
            else:
                # Image couleur
                image = Image.fromarray(pixel_array)
            
            # Amélioration supplémentaire avec PIL (si disponible)
            try:
                # Améliorer le contraste avec ImageEnhance
                from PIL import ImageEnhance
                
                # Améliorer le contraste (facteur 1.2 pour un léger boost)
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.2)
                
                # Améliorer légèrement la netteté
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(1.1)
                
                logger.debug("Améliorations PIL appliquées (contraste + netteté)")
            except Exception as e:
                logger.debug(f"Améliorations PIL non appliquées: {e}")
            
            # Générer le nom du fichier PNG
            if output_filename is None:
                png_filename = dicom_path.stem + ".png"
            else:
                png_filename = output_filename if output_filename.endswith('.png') else output_filename + ".png"
            
            png_path = self.png_dir / png_filename
            
            # Sauvegarder l'image PNG avec qualité optimale
            # Utiliser optimize=False pour une conversion plus rapide mais qualité maximale
            image.save(png_path, "PNG", optimize=False)
            
            logger.info(f"Conversion réussie: {dicom_path.name} → {png_filename}")
            
            return png_filename, png_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la conversion DICOM → PNG: {e}")
            raise ValueError(f"Erreur de conversion: {str(e)}")
    
    def save_uploaded_dicom(self, file_content: bytes, filename: str) -> Path:
        """
        Sauvegarde un fichier DICOM uploadé
        
        Args:
            file_content: Contenu du fichier en bytes
            filename: Nom du fichier original
            
        Returns:
            Chemin vers le fichier sauvegardé
        """
        # Assurer que le nom de fichier a l'extension .dcm
        if not filename.lower().endswith(('.dcm', '.dicom')):
            filename = filename + ".dcm"
        
        dicom_path = self.dicom_dir / filename
        
        # Sauvegarder le fichier
        with open(dicom_path, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"Fichier DICOM sauvegardé: {dicom_path}")
        
        return dicom_path
    
    def list_dicom_files(self) -> list:
        """Liste tous les fichiers DICOM disponibles"""
        dicom_files = []
        for file_path in self.dicom_dir.glob("*.dcm"):
            dicom_files.append({
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "path": str(file_path)
            })
        return dicom_files
    
    def list_png_files(self) -> list:
        """Liste tous les fichiers PNG disponibles"""
        png_files = []
        for file_path in self.png_dir.glob("*.png"):
            png_files.append({
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "path": str(file_path)
            })
        return png_files


# Instance globale
dicom_converter = DICOMConverter()

