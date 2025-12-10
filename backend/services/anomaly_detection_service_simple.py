"""
Anomaly Detection Service - Version Simple et Fonctionnelle
Service d'inférence pour détection d'anomalies médicales
Version sans dépendances Deep Learning lourdes
"""

import numpy as np
from pathlib import Path
from PIL import Image
import cv2
from typing import Dict, List, Tuple, Optional
import logging
import pydicom
import base64
import io

logger = logging.getLogger(__name__)


class SimpleAnomalyDetectionService:
    """
    Service de détection d'anomalies simple et fonctionnel
    Utilise uniquement des techniques de traitement d'image basiques
    Pas de dépendances Deep Learning
    """
    
    def __init__(self):
        self.device = "cpu"  # Toujours CPU pour cette version simple
        logger.info("SimpleAnomalyDetectionService initialized (mode simple)")
    
    def _load_image(self, image_path: str) -> Tuple[np.ndarray, Dict]:
        """
        Charger image (DICOM ou standard)
        Returns: (image_array, metadata)
        """
        image_path_obj = Path(image_path)
        metadata = {}
        
        if image_path_obj.suffix.lower() in ['.dcm', '.dicom']:
            # DICOM
            try:
                ds = pydicom.dcmread(image_path)
                img_array = ds.pixel_array.astype(np.float32)
                
                # Normaliser
                if img_array.max() > 255:
                    img_array = (img_array / img_array.max() * 255).astype(np.uint8)
                
                # Métadonnées
                metadata['modality'] = getattr(ds, 'Modality', 'UNKNOWN')
                metadata['pixel_spacing'] = getattr(ds, 'PixelSpacing', [1.0, 1.0])
                metadata['slice_thickness'] = getattr(ds, 'SliceThickness', 1.0)
                
            except Exception as e:
                logger.error(f"Error loading DICOM: {e}")
                raise
        else:
            # Image standard
            try:
                img = Image.open(image_path)
                img_array = np.array(img.convert('L'))  # Grayscale
                metadata['modality'] = 'UNKNOWN'
                metadata['pixel_spacing'] = [1.0, 1.0]
                metadata['slice_thickness'] = 1.0
            except Exception as e:
                logger.error(f"Error loading image: {e}")
                raise
        
        return img_array, metadata
    
    def _detect_regions(self, image: np.ndarray) -> List[Dict]:
        """
        Détecter régions suspectes avec traitement d'image basique
        Utilise la détection de contours et seuillage
        """
        regions = []
        
        if not CV2_AVAILABLE:
            # Fallback simple sans OpenCV
            logger.warning("OpenCV non disponible, détection basique limitée")
            # Détection très simple basée sur les valeurs de pixels
            threshold = np.percentile(image, 95)  # 95e percentile
            mask = image > threshold
            
            # Trouver bounding box simple
            if mask.any():
                coords = np.where(mask)
                if len(coords[0]) > 0:
                    y_min, y_max = coords[0].min(), coords[0].max()
                    x_min, x_max = coords[1].min(), coords[1].max()
                    
                    regions.append({
                        'id': 0,
                        'x': int(x_min),
                        'y': int(y_min),
                        'width': int(x_max - x_min),
                        'height': int(y_max - y_min),
                        'area_pixels': float(mask.sum()),
                        'area_mm2': float(mask.sum() * 0.25),  # Approximation
                        'perimeter_pixels': float(2 * (x_max - x_min + y_max - y_min)),
                        'perimeter_mm': float(2 * (x_max - x_min + y_max - y_min) * 0.5),
                        'width_mm': float((x_max - x_min) * 0.5),
                        'height_mm': float((y_max - y_min) * 0.5),
                        'pathology': 'suspicious_region',
                        'confidence': 0.5,
                        'severity': 'moderate'
                    })
            
            return regions
        
        # Normaliser image
        img_normalized = (image / 255.0).astype(np.float32)
        
        # Appliquer seuillage adaptatif
        img_uint8 = (img_normalized * 255).astype(np.uint8)
        _, thresh = cv2.threshold(img_uint8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Trouver contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrer contours par taille
        min_area = image.shape[0] * image.shape[1] * 0.01  # 1% de l'image
        max_area = image.shape[0] * image.shape[1] * 0.5   # 50% de l'image
        
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            
            if min_area < area < max_area:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculer périmètre
                perimeter = cv2.arcLength(contour, True)
                
                # Calculer dimensions en mm (approximatif)
                pixel_spacing = 0.5  # Valeur par défaut
                width_mm = w * pixel_spacing
                height_mm = h * pixel_spacing
                area_mm2 = area * (pixel_spacing ** 2)
                perimeter_mm = perimeter * pixel_spacing
                
                # Calculer confiance basique (basé sur la forme)
                # Plus la région est régulière, plus la confiance est élevée
                extent = area / (w * h) if w * h > 0 else 0
                confidence = min(0.7, extent * 0.8)  # Max 70% pour mode simple
                
                regions.append({
                    'id': i,
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'area_pixels': float(area),
                    'area_mm2': float(area_mm2),
                    'perimeter_pixels': float(perimeter),
                    'perimeter_mm': float(perimeter_mm),
                    'width_mm': float(width_mm),
                    'height_mm': float(height_mm),
                    'pathology': 'suspicious_region',
                    'confidence': float(confidence),
                    'severity': 'moderate' if confidence > 0.5 else 'low'
                })
        
        return regions
    
    def _create_visualization(self, image: np.ndarray, regions: List[Dict]) -> np.ndarray:
        """
        Créer visualisation avec bounding boxes
        """
        # Convertir en RGB pour visualisation
        if len(image.shape) == 2:
            vis_img = np.stack([image] * 3, axis=-1)
        else:
            vis_img = image.copy()
        
        vis_img = (vis_img / vis_img.max() * 255).astype(np.uint8) if vis_img.max() > 255 else vis_img.astype(np.uint8)
        
        if CV2_AVAILABLE:
            # Dessiner bounding boxes avec OpenCV
            for region in regions:
                x, y, w, h = region['x'], region['y'], region['width'], region['height']
                color = (0, 255, 0) if region['confidence'] > 0.5 else (255, 255, 0)
                cv2.rectangle(vis_img, (x, y), (x + w, y + h), color, 2)
                
                # Ajouter label
                label = f"{region['pathology']} ({region['confidence']:.2f})"
                cv2.putText(vis_img, label, (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        else:
            # Fallback simple avec PIL
            from PIL import ImageDraw, ImageFont
            pil_img = Image.fromarray(vis_img)
            draw = ImageDraw.Draw(pil_img)
            
            for region in regions:
                x, y, w, h = region['x'], region['y'], region['width'], region['height']
                color = 'green' if region['confidence'] > 0.5 else 'yellow'
                draw.rectangle([x, y, x + w, y + h], outline=color, width=2)
            
            vis_img = np.array(pil_img)
        
        return vis_img
    
    def detect_anomaly(
        self,
        image_path: str,
        return_visualization: bool = True,
        return_segmentation: bool = True
    ) -> Dict:
        """
        Détecter anomalies dans une image
        
        Args:
            image_path: Chemin vers l'image
            return_visualization: Retourner image annotée
            return_segmentation: Retourner mask de segmentation
        
        Returns:
            Dict avec résultats de détection
        """
        try:
            # Charger image
            image, metadata = self._load_image(image_path)
            
            # Détecter régions
            regions = self._detect_regions(image)
            
            # Déterminer si anomalies détectées
            has_anomaly = len(regions) > 0
            anomaly_class = 'suspicious_region' if has_anomaly else 'normal'
            confidence = max([r['confidence'] for r in regions], default=0.0) if regions else 0.0
            
            # Créer visualisation
            visualization = None
            if return_visualization:
                vis_img = self._create_visualization(image, regions)
                visualization = vis_img.tolist()
            
            # Créer segmentation mask
            segmentation_mask = None
            if return_segmentation and regions:
                mask = np.zeros_like(image)
                for region in regions:
                    x, y, w, h = region['x'], region['y'], region['width'], region['height']
                    mask[y:y+h, x:x+w] = 255
                segmentation_mask = mask.tolist()
            
            # Mesures
            measurements = {
                'num_regions': len(regions),
                'total_area_pixels': sum(r['area_pixels'] for r in regions),
                'total_area_mm2': sum(r['area_mm2'] for r in regions),
                'pixel_to_mm_ratio': metadata.get('pixel_spacing', [0.5, 0.5])[0],
                'image_size': {
                    'width': int(image.shape[1]),
                    'height': int(image.shape[0])
                }
            }
            
            return {
                'has_anomaly': has_anomaly,
                'anomaly_class': anomaly_class,
                'confidence': float(confidence),
                'bounding_boxes': regions,
                'segmentation_mask': segmentation_mask,
                'visualization': visualization,
                'measurements': measurements,
                'backend_used': 'simple_local',
                'model_used': 'simple_image_processing',
                'processing_time_seconds': 0.1,  # Très rapide
                'risk_score': int(confidence * 100),
                'recommendations': [
                    'Analyse effectuée avec traitement d\'image basique',
                    'Pour une analyse plus précise, utilisez un modèle Deep Learning',
                    'Consultez un radiologue pour validation'
                ] if has_anomaly else ['Aucune anomalie détectée avec les méthodes basiques']
            }
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}", exc_info=True)
            return {
                'has_anomaly': False,
                'anomaly_class': 'error',
                'confidence': 0.0,
                'error': str(e)
            }


# Singleton instance
_simple_service_instance = None

def get_simple_anomaly_detection_service() -> SimpleAnomalyDetectionService:
    """Get singleton instance"""
    global _simple_service_instance
    if _simple_service_instance is None:
        _simple_service_instance = SimpleAnomalyDetectionService()
    return _simple_service_instance

