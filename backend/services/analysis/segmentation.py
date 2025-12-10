"""
Segmentation Service
Provides medical image segmentation functionality
Supports multiple backends: MONAI, Simple thresholding
"""

import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import cv2
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SegmentationResult:
    """Structured segmentation result"""
    mask: np.ndarray
    regions: List[Dict[str, Any]]
    measurements: Dict[str, float]
    metadata: Dict[str, Any]


class SegmentationService:
    """
    Medical Image Segmentation Service
    """
    
    def __init__(self):
        self.model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize segmentation model"""
        try:
            import torch
            from monai.networks.nets import UNet
            
            self.model = UNet(
                spatial_dims=2,
                in_channels=1,
                out_channels=2,  # Background + anomaly
                channels=(16, 32, 64, 128),
                strides=(2, 2, 2),
            )
            self.model.eval()
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = self.model.to(self.device)
            logger.info(f"MONAI UNet initialized on {self.device}")
        except Exception as e:
            logger.warning(f"MONAI not available: {e}, using simple segmentation")
            self.model = None
    
    def segment(
        self,
        image: np.ndarray,
        pixel_spacing: Optional[Tuple[float, float]] = None
    ) -> SegmentationResult:
        """
        Segment an image
        
        Args:
            image: Input image
            pixel_spacing: Physical pixel spacing (mm) for measurements
            
        Returns:
            SegmentationResult with mask and measurements
        """
        if self.model is not None:
            return self._segment_dl(image, pixel_spacing)
        else:
            return self._segment_simple(image, pixel_spacing)
    
    def _segment_simple(
        self,
        image: np.ndarray,
        pixel_spacing: Optional[Tuple[float, float]] = None
    ) -> SegmentationResult:
        """Simple segmentation using image processing"""
        # Normalize
        img_normalized = ((image - image.min()) / (image.max() - image.min() + 1e-8) * 255).astype(np.uint8)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(img_normalized, (5, 5), 0)
        
        # Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Morphological operations
        kernel = np.ones((3, 3), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Find regions
        mask = thresh.astype(np.float32) / 255.0
        regions, measurements = self._analyze_mask(mask, pixel_spacing)
        
        return SegmentationResult(
            mask=mask,
            regions=regions,
            measurements=measurements,
            metadata={"method": "adaptive_threshold"}
        )
    
    def _segment_dl(
        self,
        image: np.ndarray,
        pixel_spacing: Optional[Tuple[float, float]] = None
    ) -> SegmentationResult:
        """Deep learning segmentation"""
        import torch
        
        # Prepare input
        img_tensor = torch.from_numpy(image).float().unsqueeze(0).unsqueeze(0)
        img_tensor = torch.nn.functional.interpolate(img_tensor, size=(256, 256), mode='bilinear')
        img_tensor = img_tensor.to(self.device)
        
        # Run segmentation
        with torch.no_grad():
            output = self.model(img_tensor)
            probs = torch.softmax(output, dim=1)
            mask = (probs[:, 1] > 0.5).float()
        
        # Resize back
        mask_np = mask.cpu().numpy()[0]
        mask_resized = cv2.resize(mask_np, (image.shape[1], image.shape[0]))
        
        # Analyze
        regions, measurements = self._analyze_mask(mask_resized, pixel_spacing)
        
        return SegmentationResult(
            mask=mask_resized,
            regions=regions,
            measurements=measurements,
            metadata={"method": "monai_unet"}
        )
    
    def _analyze_mask(
        self,
        mask: np.ndarray,
        pixel_spacing: Optional[Tuple[float, float]] = None
    ) -> Tuple[List[Dict], Dict[str, float]]:
        """Analyze segmentation mask"""
        regions = []
        
        # Convert to uint8
        mask_uint8 = (mask * 255).astype(np.uint8)
        
        # Find contours
        contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        total_area_px = 0
        total_perimeter_px = 0
        
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area < 10:  # Skip tiny regions
                continue
            
            perimeter = cv2.arcLength(contour, True)
            x, y, w, h = cv2.boundingRect(contour)
            
            # Circularity
            circularity = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0
            
            region = {
                "id": i + 1,
                "area_pixels": float(area),
                "perimeter_pixels": float(perimeter),
                "bounding_box": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                "circularity": float(circularity),
                "centroid": {"x": int(x + w/2), "y": int(y + h/2)}
            }
            
            # Convert to physical units if spacing available
            if pixel_spacing:
                px_area = pixel_spacing[0] * pixel_spacing[1]
                region["area_mm2"] = float(area * px_area)
                region["perimeter_mm"] = float(perimeter * pixel_spacing[0])
            
            regions.append(region)
            total_area_px += area
            total_perimeter_px += perimeter
        
        # Summary measurements
        measurements = {
            "total_area_pixels": float(total_area_px),
            "total_perimeter_pixels": float(total_perimeter_px),
            "num_regions": len(regions),
        }
        
        if pixel_spacing:
            px_area = pixel_spacing[0] * pixel_spacing[1]
            measurements["total_area_mm2"] = float(total_area_px * px_area)
            measurements["total_perimeter_mm"] = float(total_perimeter_px * pixel_spacing[0])
        
        return regions, measurements


# Singleton
_seg_instance: Optional[SegmentationService] = None


def get_segmentation_service() -> SegmentationService:
    """Get singleton instance"""
    global _seg_instance
    if _seg_instance is None:
        _seg_instance = SegmentationService()
    return _seg_instance

