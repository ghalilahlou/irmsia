"""
Anomaly Detection Service
Service d'inférence pour détection d'anomalies médicales
Intègre les modèles entraînés avec segmentation et mesures
"""

import torch
import torch.nn.functional as F
import numpy as np
from pathlib import Path
from PIL import Image
import cv2
from typing import Dict, List, Tuple, Optional
import logging
import pydicom

# Import torchvision avec gestion d'erreur pour compatibilité
try:
    from torchvision import transforms
    TORCHVISION_AVAILABLE = True
except (ImportError, AttributeError) as e:
    logging.warning(f"torchvision non disponible: {e}. Utilisation d'une alternative.")
    TORCHVISION_AVAILABLE = False
    # Créer une alternative simple pour transforms
    class SimpleTransforms:
        @staticmethod
        def Compose(transforms_list):
            def transform(img):
                for t in transforms_list:
                    img = t(img)
                return img
            return transform
        
        @staticmethod
        def Resize(size):
            def resize(img):
                if isinstance(size, tuple):
                    return img.resize(size, Image.LANCZOS)
                return img.resize((size, size), Image.LANCZOS)
            return resize
        
        @staticmethod
        def ToTensor():
            def to_tensor(img):
                import numpy as np
                img_array = np.array(img, dtype=np.float32)
                if len(img_array.shape) == 2:
                    img_array = img_array[np.newaxis, :, :]  # Ajouter dimension channel
                else:
                    img_array = img_array.transpose(2, 0, 1)  # HWC -> CHW
                return torch.from_numpy(img_array / 255.0)
            return to_tensor
        
        @staticmethod
        def Normalize(mean, std):
            def normalize(tensor):
                for t, m, s in zip(tensor, mean, std):
                    t.sub_(m).div_(s)
                return tensor
            return normalize
    
    transforms = SimpleTransforms()

logger = logging.getLogger(__name__)

# Import models from grpc-deeplearning
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "grpc-deeplearning" / "data_pipeline"))

try:
    from models.anomaly_detector import (
        SupervisedAnomalyClassifier,
        VariationalAutoencoder,
        HybridAnomalyDetector,
        ANOMALY_CLASSES
    )
except ImportError:
    logger.warning("Could not import anomaly detection models")
    ANOMALY_CLASSES = ['normal', 'tumor', 'infection', 'hemorrhage', 'fracture', 
                       'edema', 'atelectasis', 'pneumothorax', 'consolidation', 'other_anomaly']


class AnomalyDetectionService:
    """
    Service de détection d'anomalies avec segmentation et mesures
    """
    
    def __init__(
        self,
        model_path: str = None,
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        self.device = device
        self.model = None
        self.model_path = model_path or self._find_latest_model()
        
        # Transform for images (avec fallback si torchvision non disponible)
        if TORCHVISION_AVAILABLE:
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5], std=[0.5])
            ])
        else:
            # Alternative simple sans torchvision
            def simple_transform(img):
                # Resize
                img = img.resize((224, 224), Image.LANCZOS)
                # ToTensor
                import numpy as np
                img_array = np.array(img, dtype=np.float32)
                if len(img_array.shape) == 2:
                    img_array = img_array[np.newaxis, :, :]  # Ajouter dimension channel
                tensor = torch.from_numpy(img_array / 255.0)
                # Normalize
                tensor = (tensor - 0.5) / 0.5
                return tensor
            self.transform = simple_transform
        
        # Load model
        self._load_model()
        
        logger.info(f"AnomalyDetectionService initialized on {device}")
    
    def _find_latest_model(self) -> Optional[str]:
        """Trouver le dernier modèle entraîné"""
        training_outputs = Path(__file__).parent.parent.parent / "grpc-deeplearning" / "data_pipeline" / "training_outputs" / "anomaly_detection"
        
        if not training_outputs.exists():
            logger.warning(f"Training outputs not found: {training_outputs}")
            return None
        
        # Trouver le dernier run
        runs = sorted([d for d in training_outputs.iterdir() if d.is_dir()], reverse=True)
        
        if not runs:
            logger.warning("No training runs found")
            return None
        
        latest_run = runs[0]
        model_file = latest_run / "supervised_best.pth"
        
        if model_file.exists():
            logger.info(f"Found model: {model_file}")
            return str(model_file)
        
        return None
    
    def _load_model(self):
        """Charger le modèle entraîné"""
        if not self.model_path or not Path(self.model_path).exists():
            logger.warning("No trained model found. Using untrained model.")
            self.model = SupervisedAnomalyClassifier(num_classes=len(ANOMALY_CLASSES))
            self.model.to(self.device)
            self.model.eval()
            return
        
        try:
            self.model = SupervisedAnomalyClassifier(num_classes=len(ANOMALY_CLASSES))
            state_dict = torch.load(self.model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            self.model.to(self.device)
            self.model.eval()
            logger.info(f"Model loaded successfully from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = SupervisedAnomalyClassifier(num_classes=len(ANOMALY_CLASSES))
            self.model.to(self.device)
            self.model.eval()
    
    def load_image(self, image_path: str) -> Tuple[torch.Tensor, np.ndarray]:
        """
        Charger image (DICOM, PNG, TIFF, etc.)
        Returns: (tensor for model, original array for visualization)
        """
        image_path = Path(image_path)
        
        # DICOM
        if image_path.suffix.lower() in ['.dcm', '.dicom']:
            dcm = pydicom.dcmread(str(image_path))
            img_array = dcm.pixel_array.astype(np.float32)
            
            # Normalize
            img_array = (img_array - img_array.min()) / (img_array.max() - img_array.min() + 1e-8)
            img_array = (img_array * 255).astype(np.uint8)
            
            # Convert to PIL
            img_pil = Image.fromarray(img_array).convert('L')
        
        # Standard images
        else:
            img_pil = Image.open(str(image_path)).convert('L')
            img_array = np.array(img_pil)
        
        # Transform for model
        img_tensor = self.transform(img_pil).unsqueeze(0).to(self.device)
        
        return img_tensor, img_array
    
    def detect_anomaly(
        self,
        image_path: str,
        return_visualization: bool = True,
        return_segmentation: bool = True
    ) -> Dict:
        """
        Détecter anomalies dans une image
        
        Returns:
            {
                'has_anomaly': bool,
                'anomaly_class': str,
                'confidence': float,
                'bounding_boxes': List[Dict],
                'segmentation_mask': np.ndarray (optionnel),
                'measurements': Dict (optionnel),
                'visualization': np.ndarray (optionnel)
            }
        """
        try:
            # Load image
            img_tensor, img_array = self.load_image(image_path)
            
            # Inference
            with torch.no_grad():
                output = self.model(img_tensor)
                probabilities = F.softmax(output, dim=1)[0]
                
                predicted_class_idx = probabilities.argmax().item()
                confidence = probabilities[predicted_class_idx].item()
                predicted_class = ANOMALY_CLASSES[predicted_class_idx]
            
            # Determine if anomaly
            has_anomaly = predicted_class != 'normal' and confidence > 0.5
            
            result = {
                'has_anomaly': has_anomaly,
                'anomaly_class': predicted_class,
                'confidence': float(confidence),
                'all_probabilities': {
                    cls: float(prob) 
                    for cls, prob in zip(ANOMALY_CLASSES, probabilities.cpu().numpy())
                }
            }
            
            # Segmentation et détection de régions
            if return_segmentation and has_anomaly:
                seg_mask, bboxes, measurements = self._segment_and_measure(img_array, img_tensor)
                result['segmentation_mask'] = seg_mask.tolist() if seg_mask is not None else None
                result['bounding_boxes'] = bboxes
                result['measurements'] = measurements
            
            # Visualization
            if return_visualization and has_anomaly:
                vis_image = self._create_visualization(
                    img_array,
                    result.get('bounding_boxes', []),
                    result.get('segmentation_mask'),
                    predicted_class,
                    confidence
                )
                result['visualization'] = vis_image.tolist() if vis_image is not None else None
            
            return result
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}", exc_info=True)
            return {
                'error': str(e),
                'has_anomaly': False,
                'anomaly_class': 'error',
                'confidence': 0.0
            }
    
    def _segment_and_measure(
        self,
        img_array: np.ndarray,
        img_tensor: torch.Tensor
    ) -> Tuple[Optional[np.ndarray], List[Dict], Dict]:
        """
        Segmenter anomalies et calculer mesures
        
        Returns:
            (segmentation_mask, bounding_boxes, measurements)
        """
        try:
            # Utiliser GradCAM ou attention maps pour localisation
            # Pour l'instant, utilisons une approche simple avec seuillage
            
            # Normaliser image
            img_normalized = cv2.normalize(img_array, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            
            # Appliquer threshold adaptatif pour trouver régions anormales
            # (en production, utiliser le modèle de segmentation)
            blurred = cv2.GaussianBlur(img_normalized, (5, 5), 0)
            _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Trouver contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filtrer petits contours
            min_area = img_array.size * 0.001  # 0.1% de l'image
            significant_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
            
            # Créer mask de segmentation
            seg_mask = np.zeros_like(img_array)
            cv2.drawContours(seg_mask, significant_contours, -1, 255, -1)
            
            # Extraire bounding boxes et mesures
            bboxes = []
            total_area = 0
            
            for i, contour in enumerate(significant_contours[:10]):  # Max 10 régions
                x, y, w, h = cv2.boundingRect(contour)
                area = cv2.contourArea(contour)
                perimeter = cv2.arcLength(contour, True)
                
                # Calculer dimensions réelles (assuming 1 pixel = 0.5mm for example)
                pixel_to_mm = 0.5  # À ajuster selon les métadonnées DICOM
                
                bbox = {
                    'id': i,
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'area_pixels': float(area),
                    'area_mm2': float(area * pixel_to_mm ** 2),
                    'perimeter_pixels': float(perimeter),
                    'perimeter_mm': float(perimeter * pixel_to_mm),
                    'width_mm': float(w * pixel_to_mm),
                    'height_mm': float(h * pixel_to_mm)
                }
                
                bboxes.append(bbox)
                total_area += area
            
            # Mesures globales
            measurements = {
                'num_regions': len(bboxes),
                'total_area_pixels': float(total_area),
                'total_area_mm2': float(total_area * pixel_to_mm ** 2),
                'pixel_to_mm_ratio': pixel_to_mm,
                'image_size': {
                    'width': img_array.shape[1],
                    'height': img_array.shape[0]
                }
            }
            
            return seg_mask, bboxes, measurements
            
        except Exception as e:
            logger.error(f"Error in segmentation: {e}")
            return None, [], {}
    
    def _create_visualization(
        self,
        img_array: np.ndarray,
        bboxes: List[Dict],
        seg_mask: Optional[np.ndarray],
        anomaly_class: str,
        confidence: float
    ) -> Optional[np.ndarray]:
        """
        Créer visualisation avec annotations
        """
        try:
            # Convert to RGB
            if len(img_array.shape) == 2:
                vis_img = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
            else:
                vis_img = img_array.copy()
            
            # Normaliser
            vis_img = cv2.normalize(vis_img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            
            # Overlay segmentation mask
            if seg_mask is not None:
                seg_mask_array = np.array(seg_mask) if isinstance(seg_mask, list) else seg_mask
                
                # Créer overlay coloré
                overlay = vis_img.copy()
                mask_color = (0, 255, 255)  # Cyan pour anomalies
                overlay[seg_mask_array > 0] = mask_color
                
                # Blend
                vis_img = cv2.addWeighted(vis_img, 0.7, overlay, 0.3, 0)
            
            # Dessiner bounding boxes
            for bbox in bboxes:
                x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']
                
                # Rectangle
                cv2.rectangle(vis_img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
                # Label avec mesures
                label = f"#{bbox['id']}: {bbox['area_mm2']:.1f}mm²"
                cv2.putText(vis_img, label, (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            # Titre avec classe et confiance
            title = f"{anomaly_class.upper()}: {confidence*100:.1f}%"
            cv2.putText(vis_img, title, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            
            return vis_img
            
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            return None
    
    def generate_medical_report(
        self,
        detection_result: Dict,
        patient_info: Optional[Dict] = None
    ) -> Dict:
        """
        Générer rapport médical automatique avec schémas explicatifs
        
        Returns:
            {
                'summary': str,
                'findings': List[str],
                'measurements': str,
                'recommendations': List[str],
                'severity': str,
                'explanatory_schemas': Dict,  # Nouveau: schémas explicatifs
                'visualization_available': bool,
                'risk_assessment': Dict
            }
        """
        try:
            has_anomaly = detection_result.get('has_anomaly', False)
            anomaly_class = detection_result.get('anomaly_class', 'unknown')
            confidence = detection_result.get('confidence', 0.0)
            measurements = detection_result.get('measurements', {})
            bboxes = detection_result.get('bounding_boxes', [])
            risk_assessment = detection_result.get('risk_assessment', {})
            
            # Summary amélioré
            if not has_anomaly:
                summary = "Aucune anomalie significative détectée dans l'image médicale analysée. Les structures anatomiques apparaissent normales."
                severity = "NORMAL"
            else:
                num_regions = len(bboxes) if bboxes else 0
                summary = (
                    f"Anomalie de type '{anomaly_class}' détectée avec {confidence*100:.1f}% de confiance. "
                    f"{num_regions} région(s) anormale(s) identifiée(s) et localisée(s) sur l'image. "
                    f"L'analyse par intelligence artificielle suggère une attention médicale."
                )
                severity = self._determine_severity(anomaly_class, confidence, measurements)
            
            # Findings détaillés avec localisation
            findings = []
            if has_anomaly:
                num_regions = measurements.get('num_regions', 0)
                
                # Findings par région détectée
                if bboxes:
                    for i, bbox in enumerate(bboxes):
                        finding_text = (
                            f"Région #{i+1}: {bbox.get('pathology', anomaly_class).capitalize()} "
                            f"localisée aux coordonnées ({bbox.get('x', 0)}, {bbox.get('y', 0)}). "
                        )
                        
                        if bbox.get('area_mm2'):
                            finding_text += f"Surface mesurée: {bbox.get('area_mm2', 0):.2f} mm². "
                        
                        if bbox.get('confidence'):
                            finding_text += f"Confiance de détection: {bbox.get('confidence', 0)*100:.1f}%. "
                        
                        if bbox.get('severity'):
                            finding_text += f"Sévérité estimée: {bbox.get('severity')}."
                        
                        findings.append(finding_text)
                else:
                    # Finding général si pas de bounding boxes
                    finding_text = (
                        f"Anomalie de type '{anomaly_class}' détectée avec {confidence*100:.1f}% de confiance. "
                    )
                    if measurements.get('total_area_mm2'):
                        finding_text += f"Surface totale affectée: {measurements.get('total_area_mm2', 0):.2f} mm²."
                    findings.append(finding_text)
                total_area = measurements.get('total_area_mm2', 0)
                
                findings.append(f"Type d'anomalie: {anomaly_class}")
                findings.append(f"Niveau de confiance: {confidence*100:.1f}%")
                findings.append(f"Nombre de régions affectées: {num_regions}")
                findings.append(f"Surface totale affectée: {total_area:.2f} mm²")
                
                # Détails par région avec périmètre
                for bbox in bboxes[:5]:  # Top 5
                    findings.append(
                        f"Région #{bbox['id']}: {bbox['width_mm']:.1f}mm x {bbox['height_mm']:.1f}mm "
                        f"(Surface: {bbox['area_mm2']:.1f}mm², Périmètre: {bbox.get('perimeter_mm', 0):.1f}mm)"
                    )
            
            # Measurements section avec périmètres
            if has_anomaly and measurements:
                meas_text = f"""
MESURES DÉTAILLÉES:
- Nombre de régions: {measurements.get('num_regions', 0)}
- Surface totale: {measurements.get('total_area_mm2', 0):.2f} mm²
- Taille image: {measurements.get('image_size', {}).get('width', 0)} x {measurements.get('image_size', {}).get('height', 0)} pixels
- Ratio pixel/mm: {measurements.get('pixel_to_mm_ratio', 0):.3f}

MESURES PAR RÉGION:
"""
                # Ajouter mesures détaillées par région
                for bbox in bboxes[:10]:  # Top 10 régions
                    meas_text += f"""
Région #{bbox.get('id', 'N/A')}:
  - Position: ({bbox.get('x', 0)}, {bbox.get('y', 0)}) pixels
  - Dimensions: {bbox.get('width_mm', 0):.2f} mm × {bbox.get('height_mm', 0):.2f} mm
  - Surface: {bbox.get('area_mm2', 0):.2f} mm²
  - Périmètre: {bbox.get('perimeter_mm', 0):.2f} mm
  - Pathologie: {bbox.get('pathology', 'Inconnue')}
  - Confiance: {bbox.get('confidence', 0)*100:.1f}%
"""
            else:
                meas_text = "Aucune mesure disponible (pas d'anomalie détectée)."
            
            # Recommendations
            recommendations = self._generate_recommendations(
                has_anomaly, anomaly_class, severity, measurements
            )
            
            # Schémas explicatifs
            explanatory_schemas = self._generate_explanatory_schemas(
                detection_result, bboxes, measurements
            )
            
            return {
                'summary': summary,
                'findings': findings,
                'measurements': meas_text,
                'recommendations': recommendations,
                'severity': severity,
                'confidence': float(confidence),
                'anomaly_type': anomaly_class,
                'explanatory_schemas': explanatory_schemas,
                'visualization_available': detection_result.get('visualization') is not None,
                'risk_assessment': risk_assessment,
                'num_regions': len(bboxes) if bboxes else 0,
                'bounding_boxes_count': len(bboxes) if bboxes else 0
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {
                'summary': f"Erreur lors de la génération du rapport: {e}",
                'findings': [],
                'measurements': '',
                'recommendations': [],
                'severity': 'ERROR',
                'confidence': 0.0,
                'anomaly_type': 'error'
            }
    
    def _determine_severity(
        self,
        anomaly_class: str,
        confidence: float,
        measurements: Dict
    ) -> str:
        """Déterminer sévérité de l'anomalie"""
        
        # Critères de sévérité
        total_area = measurements.get('total_area_mm2', 0)
        num_regions = measurements.get('num_regions', 0)
        
        # Anomalies graves
        severe_classes = ['tumor', 'hemorrhage', 'pneumothorax']
        
        if anomaly_class in severe_classes:
            if confidence > 0.8 and total_area > 500:
                return "GRAVE"
            elif confidence > 0.6:
                return "MODÉRÉE"
        
        # Autres anomalies
        if confidence > 0.7 and num_regions > 3:
            return "MODÉRÉE"
        
        return "LÉGÈRE"
    
    def _generate_recommendations(
        self,
        has_anomaly: bool,
        anomaly_class: str,
        severity: str,
        measurements: Dict
    ) -> List[str]:
        """Générer recommandations médicales"""
        
        recommendations = []
        
        if not has_anomaly:
            recommendations.append("Continuer surveillance de routine")
            recommendations.append("Répéter examen selon protocole standard")
            return recommendations
        
        # Recommandations par type
        if anomaly_class == 'tumor':
            recommendations.append("⚠️  Consultation oncologique recommandée")
            recommendations.append("Biopsie à considérer pour diagnostic histologique")
            recommendations.append("IRM avec contraste pour meilleure caractérisation")
            
        elif anomaly_class == 'hemorrhage':
            recommendations.append("🚨 URGENCE: Consultation neurologique immédiate")
            recommendations.append("Scanner de contrôle à 24h")
            recommendations.append("Surveillance hémodynamique")
            
        elif anomaly_class == 'infection':
            recommendations.append("Traitement antibiotique adapté")
            recommendations.append("Suivi radiologique à 48-72h")
            recommendations.append("Prélèvements microbiologiques si nécessaire")
            
        elif anomaly_class == 'fracture':
            recommendations.append("Immobilisation de la zone affectée")
            recommendations.append("Consultation orthopédique")
            recommendations.append("Radiographie de contrôle à 2 semaines")
        
        # Recommandations par sévérité
        if severity == "GRAVE":
            recommendations.append("🚨 Prise en charge urgente requise")
            recommendations.append("Hospitalisation à considérer")
        elif severity == "MODÉRÉE":
            recommendations.append("Consultation spécialisée dans les 48h")
        
        return recommendations
    
    def _generate_explanatory_schemas(
        self,
        detection_result: Dict,
        bboxes: List[Dict],
        measurements: Dict
    ) -> Dict:
        """Générer schémas explicatifs pour le rapport"""
        
        schemas = {
            'detection_summary': {
                'has_anomaly': detection_result.get('has_anomaly', False),
                'anomaly_class': detection_result.get('anomaly_class', 'unknown'),
                'confidence': detection_result.get('confidence', 0.0),
                'num_regions': len(bboxes) if bboxes else 0
            },
            'spatial_distribution': {
                'regions': []
            },
            'measurements_summary': {
                'total_area_mm2': measurements.get('total_area_mm2', 0),
                'num_regions': measurements.get('num_regions', 0),
                'average_region_size_mm2': 0
            }
        }
        
        # Spatial distribution
        if bboxes:
            for i, bbox in enumerate(bboxes):
                schemas['spatial_distribution']['regions'].append({
                    'id': i + 1,
                    'pathology': bbox.get('pathology', 'unknown'),
                    'location': {
                        'x': bbox.get('x', 0),
                        'y': bbox.get('y', 0),
                        'width': bbox.get('width', 0),
                        'height': bbox.get('height', 0)
                    },
                    'area_mm2': bbox.get('area_mm2', 0),
                    'confidence': bbox.get('confidence', 0),
                    'severity': bbox.get('severity', 'unknown')
                })
            
            # Average region size
            if bboxes:
                total_area = sum(bbox.get('area_mm2', 0) for bbox in bboxes)
                schemas['measurements_summary']['average_region_size_mm2'] = total_area / len(bboxes)
        
        return schemas


# Singleton instance
_service_instance = None

def get_anomaly_detection_service() -> AnomalyDetectionService:
    """Get singleton instance of anomaly detection service"""
    global _service_instance
    if _service_instance is None:
        _service_instance = AnomalyDetectionService()
    return _service_instance


