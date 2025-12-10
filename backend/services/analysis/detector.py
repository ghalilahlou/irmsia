"""
Advanced Anomaly Detector Service
Uses trained models from grpc-deeplearning pipeline
Provides detailed medical image analysis with:
- Multi-class anomaly classification
- GradCAM visualization
- Anatomical region detection
- Severity assessment
"""

import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image
import cv2
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class BoundingBox:
    """Bounding box for detected region"""
    x: int
    y: int
    width: int
    height: int
    confidence: float = 0.0
    label: str = ""
    area_pixels: int = 0
    area_mm2: Optional[float] = None


@dataclass
class DetectionResult:
    """Complete detection result with all analysis data"""
    # Detection status
    has_anomaly: bool
    anomaly_class: str
    anomaly_name: str
    confidence: float
    
    # Classification details
    severity: str  # none, low, moderate, high, critical
    urgency: str   # routine, semi-urgent, urgent, immediate
    description: str
    recommendations: List[str] = field(default_factory=list)
    
    # Localization
    bounding_boxes: List[Dict[str, Any]] = field(default_factory=list)
    attention_regions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Visualizations
    heatmap: Optional[np.ndarray] = None
    segmentation_mask: Optional[np.ndarray] = None
    
    # Measurements
    measurements: Dict[str, Any] = field(default_factory=dict)
    
    # Model info
    model_info: Dict[str, Any] = field(default_factory=dict)
    
    # Top predictions
    top_predictions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Raw metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class AnomalyDetector:
    """
    Advanced Anomaly Detector using trained models
    Combines deep learning classification with localization
    """
    
    def __init__(self):
        self.model_loader = None
        self.device = "cpu"
        self._initialize()
    
    def _initialize(self):
        """Initialize detector with trained model"""
        try:
            from .trained_model_loader import get_trained_model_loader
            self.model_loader = get_trained_model_loader()
            self.device = self.model_loader.device
            logger.info(f"AnomalyDetector initialized with trained model on {self.device}")
        except Exception as e:
            logger.warning(f"Could not load trained model: {e}")
            self.model_loader = None
    
    def detect(
        self,
        image_path: str,
        pixel_spacing: Optional[Tuple[float, float]] = None
    ) -> DetectionResult:
        """
        Perform complete anomaly detection on an image
        
        Args:
            image_path: Path to image file (DICOM, PNG, JPEG)
            pixel_spacing: Physical pixel spacing in mm (row, col)
            
        Returns:
            DetectionResult with complete analysis
        """
        try:
            # Load image
            image, metadata = self._load_image(image_path)
            
            # Update pixel spacing from metadata if available
            if pixel_spacing is None and 'pixel_spacing' in metadata:
                pixel_spacing = tuple(metadata['pixel_spacing'])
            
            # Run classification
            if self.model_loader:
                prediction = self.model_loader.predict(image)
            else:
                prediction = self._fallback_prediction(image)
            
            # Generate GradCAM heatmap
            heatmap = None
            if self.model_loader:
                heatmap = self.model_loader.generate_gradcam(image)
            
            # Detect regions of interest
            bounding_boxes, attention_regions = self._detect_regions(
                image, heatmap, pixel_spacing
            )
            
            # Generate segmentation mask
            segmentation_mask = self._generate_segmentation(image, heatmap)
            
            # Calculate measurements
            measurements = self._calculate_measurements(
                bounding_boxes, segmentation_mask, pixel_spacing
            )
            
            # Build result
            result = DetectionResult(
                has_anomaly=prediction['has_anomaly'],
                anomaly_class=prediction['anomaly_class'],
                anomaly_name=prediction['anomaly_name'],
                confidence=prediction['confidence'],
                severity=prediction['severity'],
                urgency=prediction['urgency'],
                description=prediction['description'],
                recommendations=prediction['recommendations'],
                bounding_boxes=[self._box_to_dict(box) for box in bounding_boxes],
                attention_regions=attention_regions,
                heatmap=heatmap,
                segmentation_mask=segmentation_mask,
                measurements=measurements,
                model_info={
                    'type': prediction.get('model_type', 'unknown'),
                    'device': self.device,
                    'version': '2.0.0'
                },
                top_predictions=prediction.get('top_predictions', []),
                metadata=metadata
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Detection failed: {e}", exc_info=True)
            return DetectionResult(
                has_anomaly=False,
                anomaly_class="error",
                anomaly_name="Erreur d'analyse",
                confidence=0.0,
                severity="none",
                urgency="routine",
                description=f"Erreur lors de l'analyse: {str(e)}",
                recommendations=["Veuillez reessayer ou contacter le support"],
                metadata={"error": str(e)}
            )
    
    def _load_image(self, image_path: str) -> Tuple[np.ndarray, Dict]:
        """Load image from path with metadata extraction"""
        path = Path(image_path)
        metadata = {
            "filename": path.name,
            "format": path.suffix.lower()
        }
        
        if path.suffix.lower() in ['.dcm', '.dicom']:
            # Load DICOM
            import pydicom
            ds = pydicom.dcmread(str(path))
            image = ds.pixel_array.astype(np.float32)
            
            # Extract metadata
            metadata.update({
                "modality": getattr(ds, "Modality", "UNKNOWN"),
                "rows": getattr(ds, "Rows", image.shape[0]),
                "columns": getattr(ds, "Columns", image.shape[1]),
                "patient_id": getattr(ds, "PatientID", "ANONYMOUS"),
                "study_date": str(getattr(ds, "StudyDate", "")),
                "series_description": getattr(ds, "SeriesDescription", ""),
                "body_part": getattr(ds, "BodyPartExamined", "UNKNOWN"),
            })
            
            if hasattr(ds, "PixelSpacing"):
                metadata["pixel_spacing"] = [float(x) for x in ds.PixelSpacing]
            
            if hasattr(ds, "WindowCenter") and hasattr(ds, "WindowWidth"):
                metadata["window_center"] = float(ds.WindowCenter) if not isinstance(ds.WindowCenter, list) else float(ds.WindowCenter[0])
                metadata["window_width"] = float(ds.WindowWidth) if not isinstance(ds.WindowWidth, list) else float(ds.WindowWidth[0])
        else:
            # Load standard image
            img = Image.open(str(path))
            if img.mode != 'L':
                img = img.convert('L')
            image = np.array(img, dtype=np.float32)
            
            metadata.update({
                "rows": image.shape[0],
                "columns": image.shape[1],
            })
        
        # Normalize to [0, 1]
        if image.max() > 1:
            image = (image - image.min()) / (image.max() - image.min() + 1e-8)
        
        return image, metadata
    
    def _fallback_prediction(self, image: np.ndarray) -> Dict[str, Any]:
        """Fallback prediction using image analysis heuristics"""
        # Edge detection
        edges = cv2.Canny((image * 255).astype(np.uint8), 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Intensity analysis
        mean_intensity = np.mean(image)
        std_intensity = np.std(image)
        
        # Simple heuristic
        has_anomaly = edge_density > 0.05 or std_intensity > 0.25
        
        return {
            'has_anomaly': has_anomaly,
            'anomaly_class': 'other_anomaly' if has_anomaly else 'normal',
            'anomaly_name': 'Anomalie potentielle' if has_anomaly else 'Normal',
            'confidence': 0.6 if has_anomaly else 0.8,
            'severity': 'low' if has_anomaly else 'none',
            'urgency': 'routine',
            'description': 'Analyse basee sur les caracteristiques d\'image. Correlation clinique recommandee.',
            'recommendations': [
                'Correlation clinique recommandee',
                'Examen complementaire si doute clinique'
            ],
            'model_type': 'fallback_heuristic'
        }
    
    def _detect_regions(
        self,
        image: np.ndarray,
        heatmap: Optional[np.ndarray],
        pixel_spacing: Optional[Tuple[float, float]]
    ) -> Tuple[List[BoundingBox], List[Dict]]:
        """Detect regions of interest"""
        bounding_boxes = []
        attention_regions = []
        
        # Method 1: From heatmap (if available)
        if heatmap is not None:
            heatmap_resized = cv2.resize(heatmap, (image.shape[1], image.shape[0]))
            
            # Threshold heatmap
            threshold = 0.5
            binary = (heatmap_resized > threshold).astype(np.uint8)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if area < 50:  # Skip tiny regions
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate area in mm² if spacing available
                area_mm2 = None
                if pixel_spacing:
                    area_mm2 = area * pixel_spacing[0] * pixel_spacing[1]
                
                box = BoundingBox(
                    x=x, y=y, width=w, height=h,
                    confidence=float(np.mean(heatmap_resized[y:y+h, x:x+w])),
                    label=f"attention_region_{i+1}",
                    area_pixels=int(area),
                    area_mm2=area_mm2
                )
                bounding_boxes.append(box)
                
                # Attention region with more details
                attention_regions.append({
                    "id": i + 1,
                    "center_x": int(x + w/2),
                    "center_y": int(y + h/2),
                    "attention_score": float(np.mean(heatmap_resized[y:y+h, x:x+w])),
                    "max_attention": float(np.max(heatmap_resized[y:y+h, x:x+w])),
                })
        
        # Method 2: Edge-based detection (fallback or complement)
        if len(bounding_boxes) == 0:
            edges = cv2.Canny((image * 255).astype(np.uint8), 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if area < 100:
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                
                area_mm2 = None
                if pixel_spacing:
                    area_mm2 = area * pixel_spacing[0] * pixel_spacing[1]
                
                box = BoundingBox(
                    x=x, y=y, width=w, height=h,
                    confidence=0.5,
                    label=f"detected_region_{i+1}",
                    area_pixels=int(area),
                    area_mm2=area_mm2
                )
                bounding_boxes.append(box)
        
        return bounding_boxes, attention_regions
    
    def _generate_segmentation(
        self,
        image: np.ndarray,
        heatmap: Optional[np.ndarray]
    ) -> np.ndarray:
        """Generate segmentation mask"""
        if heatmap is not None:
            # Use heatmap as base
            mask = cv2.resize(heatmap, (image.shape[1], image.shape[0]))
            mask = (mask > 0.3).astype(np.float32)
        else:
            # Adaptive thresholding
            img_uint8 = (image * 255).astype(np.uint8)
            mask = cv2.adaptiveThreshold(
                img_uint8, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            mask = mask.astype(np.float32) / 255.0
        
        # Clean up mask
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        return mask
    
    def _calculate_measurements(
        self,
        bounding_boxes: List[BoundingBox],
        segmentation_mask: np.ndarray,
        pixel_spacing: Optional[Tuple[float, float]]
    ) -> Dict[str, Any]:
        """Calculate detailed measurements"""
        measurements = {
            "num_regions": len(bounding_boxes),
            "total_area_pixels": 0,
            "max_area_pixels": 0,
            "min_area_pixels": float('inf') if bounding_boxes else 0,
        }
        
        for box in bounding_boxes:
            measurements["total_area_pixels"] += box.area_pixels
            measurements["max_area_pixels"] = max(measurements["max_area_pixels"], box.area_pixels)
            if box.area_pixels > 0:
                measurements["min_area_pixels"] = min(measurements["min_area_pixels"], box.area_pixels)
        
        if measurements["min_area_pixels"] == float('inf'):
            measurements["min_area_pixels"] = 0
        
        # Calculate average
        if bounding_boxes:
            measurements["avg_area_pixels"] = measurements["total_area_pixels"] / len(bounding_boxes)
        else:
            measurements["avg_area_pixels"] = 0
        
        # Physical measurements
        if pixel_spacing:
            px_area = pixel_spacing[0] * pixel_spacing[1]
            measurements["total_area_mm2"] = measurements["total_area_pixels"] * px_area
            measurements["max_area_mm2"] = measurements["max_area_pixels"] * px_area
            measurements["min_area_mm2"] = measurements["min_area_pixels"] * px_area
            measurements["avg_area_mm2"] = measurements["avg_area_pixels"] * px_area
            measurements["pixel_spacing_mm"] = list(pixel_spacing)
        
        # Segmentation mask stats
        if segmentation_mask is not None:
            mask_area = np.sum(segmentation_mask > 0.5)
            measurements["segmented_area_pixels"] = int(mask_area)
            measurements["segmentation_ratio"] = float(mask_area / segmentation_mask.size)
            
            if pixel_spacing:
                measurements["segmented_area_mm2"] = mask_area * px_area
        
        return measurements
    
    def _box_to_dict(self, box: BoundingBox) -> Dict[str, Any]:
        """Convert BoundingBox to dictionary"""
        result = {
            "x": box.x,
            "y": box.y,
            "width": box.width,
            "height": box.height,
            "confidence": box.confidence,
            "label": box.label,
            "area_pixels": box.area_pixels,
        }
        if box.area_mm2 is not None:
            result["area_mm2"] = box.area_mm2
        return result


# Singleton
_detector_instance: Optional[AnomalyDetector] = None


def get_anomaly_detector() -> AnomalyDetector:
    """Get singleton instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = AnomalyDetector()
    return _detector_instance
