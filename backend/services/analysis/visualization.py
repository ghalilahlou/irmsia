"""
Visualization Service
Generates visual explanations for medical image analysis
- GradCAM heatmaps
- Annotated images with bounding boxes
- Segmentation overlays
- Charts and graphs
"""

import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image, ImageDraw, ImageFont
import cv2
import base64
import io
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class VisualizationConfig:
    """Configuration for visualizations"""
    heatmap_colormap: str = "jet"
    heatmap_alpha: float = 0.4
    box_thickness: int = 2
    font_size: int = 12
    annotation_color: Tuple[int, int, int] = (255, 0, 0)
    highlight_color: Tuple[int, int, int] = (0, 255, 0)


class VisualizationService:
    """
    Service for generating visual explanations
    """
    
    PATHOLOGY_COLORS = {
        'tumor': (255, 0, 0),      # Red
        'infection': (255, 165, 0), # Orange
        'hemorrhage': (128, 0, 128), # Purple
        'fracture': (255, 255, 0),  # Yellow
        'edema': (0, 255, 255),     # Cyan
        'normal': (0, 255, 0),      # Green
        'default': (255, 0, 0),     # Red
    }
    
    def __init__(self, config: Optional[VisualizationConfig] = None):
        self.config = config or VisualizationConfig()
    
    def create_annotated_image(
        self,
        image: np.ndarray,
        bounding_boxes: List[Dict],
        anomaly_class: str = "default",
        show_labels: bool = True,
        show_confidence: bool = True
    ) -> np.ndarray:
        """
        Create an annotated image with bounding boxes
        
        Args:
            image: Input image (grayscale or RGB)
            bounding_boxes: List of bounding box dictionaries
            anomaly_class: Type of anomaly for color selection
            show_labels: Whether to show labels
            show_confidence: Whether to show confidence scores
            
        Returns:
            Annotated image as numpy array
        """
        # Convert to RGB if grayscale
        if len(image.shape) == 2:
            image_rgb = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_GRAY2RGB)
        else:
            image_rgb = (image * 255).astype(np.uint8) if image.max() <= 1 else image.copy()
        
        # Draw bounding boxes
        for box in bounding_boxes:
            x, y, w, h = int(box['x']), int(box['y']), int(box['width']), int(box['height'])
            color = self.PATHOLOGY_COLORS.get(anomaly_class, self.PATHOLOGY_COLORS['default'])
            
            # Draw rectangle
            cv2.rectangle(image_rgb, (x, y), (x + w, y + h), color, self.config.box_thickness)
            
            # Draw label
            if show_labels or show_confidence:
                label_parts = []
                if show_labels and 'label' in box:
                    label_parts.append(box['label'])
                if show_confidence and 'confidence' in box:
                    label_parts.append(f"{box['confidence']*100:.1f}%")
                
                label = " ".join(label_parts)
                if label:
                    # Background for text
                    (text_width, text_height), baseline = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
                    )
                    cv2.rectangle(
                        image_rgb,
                        (x, y - text_height - 5),
                        (x + text_width + 5, y),
                        color, -1
                    )
                    # Text
                    cv2.putText(
                        image_rgb, label,
                        (x + 2, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 1
                    )
        
        return image_rgb
    
    def create_heatmap_overlay(
        self,
        image: np.ndarray,
        heatmap: np.ndarray,
        alpha: Optional[float] = None
    ) -> np.ndarray:
        """
        Create a heatmap overlay on the original image
        
        Args:
            image: Original image
            heatmap: Attention/activation heatmap
            alpha: Transparency of overlay
            
        Returns:
            Image with heatmap overlay
        """
        alpha = alpha or self.config.heatmap_alpha
        
        # Convert image to RGB
        if len(image.shape) == 2:
            image_rgb = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_GRAY2RGB)
        else:
            image_rgb = (image * 255).astype(np.uint8) if image.max() <= 1 else image.copy()
        
        # Resize heatmap to match image
        heatmap_resized = cv2.resize(heatmap, (image_rgb.shape[1], image_rgb.shape[0]))
        
        # Normalize heatmap
        heatmap_normalized = (heatmap_resized - heatmap_resized.min()) / (
            heatmap_resized.max() - heatmap_resized.min() + 1e-8
        )
        
        # Apply colormap
        heatmap_colored = cv2.applyColorMap(
            (heatmap_normalized * 255).astype(np.uint8),
            cv2.COLORMAP_JET
        )
        
        # Blend
        overlay = cv2.addWeighted(image_rgb, 1 - alpha, heatmap_colored, alpha, 0)
        
        return overlay
    
    def create_segmentation_overlay(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        alpha: float = 0.5,
        color: Tuple[int, int, int] = (255, 0, 0)
    ) -> np.ndarray:
        """
        Create a segmentation mask overlay
        
        Args:
            image: Original image
            mask: Binary segmentation mask
            alpha: Transparency
            color: Color for the mask
            
        Returns:
            Image with segmentation overlay
        """
        # Convert image to RGB
        if len(image.shape) == 2:
            image_rgb = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_GRAY2RGB)
        else:
            image_rgb = (image * 255).astype(np.uint8) if image.max() <= 1 else image.copy()
        
        # Resize mask
        mask_resized = cv2.resize(mask.astype(np.uint8), (image_rgb.shape[1], image_rgb.shape[0]))
        
        # Create colored overlay
        overlay = image_rgb.copy()
        overlay[mask_resized > 0] = color
        
        # Blend
        result = cv2.addWeighted(image_rgb, 1 - alpha, overlay, alpha, 0)
        
        # Draw contours
        contours, _ = cv2.findContours(mask_resized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(result, contours, -1, color, 2)
        
        return result
    
    def create_comparison_view(
        self,
        original: np.ndarray,
        annotated: np.ndarray,
        title_original: str = "Original",
        title_annotated: str = "Analysis"
    ) -> np.ndarray:
        """
        Create a side-by-side comparison view
        """
        # Ensure same size
        h, w = original.shape[:2]
        
        # Convert to RGB if needed
        if len(original.shape) == 2:
            original_rgb = cv2.cvtColor((original * 255).astype(np.uint8), cv2.COLOR_GRAY2RGB)
        else:
            original_rgb = original.copy()
        
        # Resize annotated to match
        annotated_resized = cv2.resize(annotated, (w, h))
        
        # Create combined image
        combined = np.hstack([original_rgb, annotated_resized])
        
        # Add titles
        cv2.putText(combined, title_original, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(combined, title_annotated, (w + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        return combined
    
    def create_zoom_view(
        self,
        image: np.ndarray,
        box: Dict,
        zoom_factor: float = 2.0,
        padding: int = 20
    ) -> np.ndarray:
        """
        Create a zoomed view of a specific region
        
        Args:
            image: Original image
            box: Bounding box dictionary with x, y, width, height
            zoom_factor: Zoom multiplier
            padding: Extra padding around the region
            
        Returns:
            Zoomed image of the region
        """
        x, y, w, h = int(box['x']), int(box['y']), int(box['width']), int(box['height'])
        
        # Add padding
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(image.shape[1], x + w + padding)
        y2 = min(image.shape[0], y + h + padding)
        
        # Extract region
        region = image[y1:y2, x1:x2]
        
        # Zoom
        new_size = (int(region.shape[1] * zoom_factor), int(region.shape[0] * zoom_factor))
        zoomed = cv2.resize(region, new_size, interpolation=cv2.INTER_LINEAR)
        
        return zoomed
    
    def image_to_base64(self, image: np.ndarray, format: str = "PNG") -> str:
        """Convert numpy array to base64 string"""
        if len(image.shape) == 2:
            pil_image = Image.fromarray((image * 255).astype(np.uint8) if image.max() <= 1 else image.astype(np.uint8))
        else:
            pil_image = Image.fromarray(image.astype(np.uint8))
        
        buffer = io.BytesIO()
        pil_image.save(buffer, format=format)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    def generate_analysis_report_visuals(
        self,
        image: np.ndarray,
        detection_result: Any,
    ) -> Dict[str, str]:
        """
        Generate all visualization for an analysis report
        
        Returns:
            Dictionary of base64-encoded images
        """
        visuals = {}
        
        # Original image
        visuals['original'] = self.image_to_base64(image)
        
        # Annotated image with bounding boxes
        if detection_result.bounding_boxes:
            annotated = self.create_annotated_image(
                image,
                detection_result.bounding_boxes,
                detection_result.anomaly_class
            )
            visuals['annotated'] = self.image_to_base64(annotated)
        
        # Heatmap overlay
        if detection_result.heatmap is not None:
            heatmap_overlay = self.create_heatmap_overlay(image, detection_result.heatmap)
            visuals['heatmap'] = self.image_to_base64(heatmap_overlay)
        
        # Segmentation overlay
        if detection_result.segmentation_mask is not None:
            seg_overlay = self.create_segmentation_overlay(image, detection_result.segmentation_mask)
            visuals['segmentation'] = self.image_to_base64(seg_overlay)
        
        # Zoomed views of regions
        if detection_result.bounding_boxes:
            zoomed_regions = []
            for i, box in enumerate(detection_result.bounding_boxes[:3]):  # Max 3 zoomed regions
                zoomed = self.create_zoom_view(image, box)
                zoomed_regions.append(self.image_to_base64(zoomed))
            visuals['zoomed_regions'] = zoomed_regions
        
        return visuals


# Singleton instance
_viz_instance: Optional[VisualizationService] = None


def get_visualization_service() -> VisualizationService:
    """Get singleton instance"""
    global _viz_instance
    if _viz_instance is None:
        _viz_instance = VisualizationService()
    return _viz_instance

