"""
DICOM Preprocessing pour Deep Learning
Optimisé pour performance et qualité
"""

import pydicom
import numpy as np
import torch
import cv2
from typing import Tuple, Optional, Dict
import logging
from pathlib import Path
import io

logger = logging.getLogger(__name__)


class DICOMProcessor:
    """
    Processeur DICOM optimisé pour Deep Learning
    - Préserve la qualité 16-bit
    - Windowing intelligent
    - Normalisation adaptative
    - Augmentations médicales
    """
    
    def __init__(
        self,
        target_size: Tuple[int, int] = (512, 512),
        preserve_aspect_ratio: bool = False,
        auto_windowing: bool = True
    ):
        self.target_size = target_size
        self.preserve_aspect_ratio = preserve_aspect_ratio
        self.auto_windowing = auto_windowing
        
        logger.info(f"DICOM Processor initialized (target_size={target_size})")
    
    def load_dicom(self, dicom_path_or_bytes) -> pydicom.Dataset:
        """
        Charger un fichier DICOM depuis path ou bytes
        
        Args:
            dicom_path_or_bytes: Path ou bytes
        
        Returns:
            pydicom.Dataset
        """
        if isinstance(dicom_path_or_bytes, (str, Path)):
            dcm = pydicom.dcmread(dicom_path_or_bytes)
        elif isinstance(dicom_path_or_bytes, bytes):
            dcm = pydicom.dcmread(io.BytesIO(dicom_path_or_bytes))
        else:
            raise ValueError(f"Unsupported input type: {type(dicom_path_or_bytes)}")
        
        return dcm
    
    def extract_metadata(self, dcm: pydicom.Dataset) -> Dict:
        """
        Extraire les métadonnées importantes
        
        Returns:
            Dict avec métadonnées
        """
        metadata = {
            'modality': getattr(dcm, 'Modality', 'UNKNOWN'),
            'body_part': getattr(dcm, 'BodyPartExamined', 'UNKNOWN'),
            'patient_id': getattr(dcm, 'PatientID', 'UNKNOWN'),
            'study_date': getattr(dcm, 'StudyDate', 'UNKNOWN'),
            'series_description': getattr(dcm, 'SeriesDescription', 'UNKNOWN'),
            'rows': int(dcm.Rows),
            'columns': int(dcm.Columns),
            'bits_allocated': int(dcm.BitsAllocated),
            'bits_stored': int(dcm.BitsStored),
            'pixel_spacing': getattr(dcm, 'PixelSpacing', [1.0, 1.0]),
            'slice_thickness': float(getattr(dcm, 'SliceThickness', 1.0)),
        }
        
        # Window Center/Width si disponibles
        if hasattr(dcm, 'WindowCenter'):
            wc = dcm.WindowCenter
            if isinstance(wc, (list, pydicom.multival.MultiValue)):
                wc = float(wc[0])
            metadata['window_center'] = float(wc)
        
        if hasattr(dcm, 'WindowWidth'):
            ww = dcm.WindowWidth
            if isinstance(ww, (list, pydicom.multival.MultiValue)):
                ww = float(ww[0])
            metadata['window_width'] = float(ww)
        
        # Rescale slope/intercept (pour CT)
        metadata['rescale_slope'] = float(getattr(dcm, 'RescaleSlope', 1.0))
        metadata['rescale_intercept'] = float(getattr(dcm, 'RescaleIntercept', 0.0))
        
        return metadata
    
    def get_pixel_array(self, dcm: pydicom.Dataset) -> np.ndarray:
        """
        Extraire le pixel array en préservant la qualité
        
        Returns:
            np.ndarray float32
        """
        # Get pixel array
        image = dcm.pixel_array.astype(np.float32)
        
        # Apply rescale (CT: conversion to Hounsfield Units)
        if hasattr(dcm, 'RescaleSlope') and hasattr(dcm, 'RescaleIntercept'):
            image = image * dcm.RescaleSlope + dcm.RescaleIntercept
        
        # Handle photometric interpretation
        if hasattr(dcm, 'PhotometricInterpretation'):
            if dcm.PhotometricInterpretation == "MONOCHROME1":
                # Invert if needed
                image = image.max() - image
        
        return image
    
    def apply_windowing(
        self,
        image: np.ndarray,
        window_center: Optional[float] = None,
        window_width: Optional[float] = None,
        modality: str = "UNKNOWN"
    ) -> np.ndarray:
        """
        Appliquer le windowing (contraste)
        
        Args:
            image: Pixel array
            window_center: Center (ou None pour auto)
            window_width: Width (ou None pour auto)
            modality: Modalité DICOM
        
        Returns:
            Image windowée [0, 1]
        """
        if window_center is None or window_width is None:
            # Auto windowing selon modalité
            if modality == 'CT':
                # Soft tissue window
                window_center = 40
                window_width = 400
            elif modality == 'MR':
                # Auto-window basé sur statistiques
                window_center = float(np.median(image))
                window_width = float(np.percentile(image, 95) - np.percentile(image, 5))
            else:
                # Default: full range
                window_center = float(image.mean())
                window_width = float(image.std() * 4)
        
        # Apply window
        img_min = window_center - window_width / 2
        img_max = window_center + window_width / 2
        
        image = np.clip(image, img_min, img_max)
        image = (image - img_min) / (img_max - img_min)
        
        return image
    
    def resize_image(
        self,
        image: np.ndarray,
        target_size: Optional[Tuple[int, int]] = None
    ) -> np.ndarray:
        """
        Resize avec interpolation de qualité
        
        Args:
            image: Input image
            target_size: Target size (ou None pour self.target_size)
        
        Returns:
            Resized image
        """
        if target_size is None:
            target_size = self.target_size
        
        if self.preserve_aspect_ratio:
            # Preserve aspect ratio with padding
            h, w = image.shape[:2]
            scale = min(target_size[0] / h, target_size[1] / w)
            new_h = int(h * scale)
            new_w = int(w * scale)
            
            # Resize
            resized = cv2.resize(
                image,
                (new_w, new_h),
                interpolation=cv2.INTER_CUBIC
            )
            
            # Pad to target size
            pad_h = target_size[0] - new_h
            pad_w = target_size[1] - new_w
            top = pad_h // 2
            bottom = pad_h - top
            left = pad_w // 2
            right = pad_w - left
            
            image = cv2.copyMakeBorder(
                resized,
                top, bottom, left, right,
                cv2.BORDER_CONSTANT,
                value=0
            )
        else:
            # Direct resize
            image = cv2.resize(
                image,
                target_size[::-1],  # cv2 uses (W, H)
                interpolation=cv2.INTER_CUBIC
            )
        
        return image
    
    def normalize_image(
        self,
        image: np.ndarray,
        method: str = 'minmax'
    ) -> np.ndarray:
        """
        Normalisation de l'image
        
        Args:
            image: Input image
            method: 'minmax' | 'zscore' | 'percentile'
        
        Returns:
            Normalized image
        """
        if method == 'minmax':
            # Min-max normalization [0, 1]
            image = (image - image.min()) / (image.max() - image.min() + 1e-8)
        
        elif method == 'zscore':
            # Z-score normalization
            mean = image.mean()
            std = image.std()
            image = (image - mean) / (std + 1e-8)
        
        elif method == 'percentile':
            # Percentile-based (robust to outliers)
            p1 = np.percentile(image, 1)
            p99 = np.percentile(image, 99)
            image = np.clip(image, p1, p99)
            image = (image - p1) / (p99 - p1 + 1e-8)
        
        return image
    
    def preprocess(
        self,
        dicom_path_or_bytes,
        return_metadata: bool = False
    ) -> Tuple[torch.Tensor, Optional[Dict]]:
        """
        Pipeline complet de preprocessing
        
        Args:
            dicom_path_or_bytes: DICOM file
            return_metadata: Return metadata dict
        
        Returns:
            Tuple (tensor [1, 1, H, W], metadata)
        """
        # 1. Load DICOM
        dcm = self.load_dicom(dicom_path_or_bytes)
        
        # 2. Extract metadata
        metadata = self.extract_metadata(dcm)
        
        # 3. Get pixel array
        image = self.get_pixel_array(dcm)
        
        # 4. Apply windowing
        if self.auto_windowing:
            window_center = metadata.get('window_center', None)
            window_width = metadata.get('window_width', None)
            image = self.apply_windowing(
                image,
                window_center,
                window_width,
                metadata['modality']
            )
        
        # 5. Resize
        image = self.resize_image(image)
        
        # 6. Normalize
        image = self.normalize_image(image, method='minmax')
        
        # 7. Convert to tensor [1, 1, H, W]
        tensor = torch.from_numpy(image).unsqueeze(0).unsqueeze(0).float()
        
        logger.debug(f"Preprocessed DICOM: {metadata['modality']} {metadata['rows']}x{metadata['columns']} -> {tensor.shape}")
        
        if return_metadata:
            return tensor, metadata
        else:
            return tensor, None
    
    def batch_preprocess(
        self,
        dicom_list: list,
        batch_size: int = 16
    ) -> torch.Tensor:
        """
        Preprocessing par batch (optimisé)
        
        Args:
            dicom_list: Liste de paths ou bytes
            batch_size: Batch size
        
        Returns:
            Tensor [B, 1, H, W]
        """
        tensors = []
        
        for dicom_data in dicom_list:
            tensor, _ = self.preprocess(dicom_data, return_metadata=False)
            tensors.append(tensor)
            
            # Process batch
            if len(tensors) == batch_size:
                yield torch.cat(tensors, dim=0)
                tensors = []
        
        # Remaining
        if tensors:
            yield torch.cat(tensors, dim=0)


class DICOMAugmenter:
    """
    Augmentations spécifiques pour images médicales
    - Rotation limitée
    - Flip horizontal/vertical
    - Zoom
    - Brightness/Contrast
    - Gaussian noise
    """
    
    def __init__(self, p: float = 0.5):
        self.p = p
    
    def random_rotation(self, image: np.ndarray, max_angle: int = 15) -> np.ndarray:
        """Rotation aléatoire (-max_angle, +max_angle)"""
        if np.random.rand() > self.p:
            return image
        
        angle = np.random.uniform(-max_angle, max_angle)
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, matrix, (w, h), borderMode=cv2.BORDER_REFLECT)
        
        return rotated
    
    def random_flip(self, image: np.ndarray) -> np.ndarray:
        """Flip horizontal ou vertical"""
        if np.random.rand() > self.p:
            return image
        
        flip_code = np.random.choice([0, 1])  # 0: vertical, 1: horizontal
        flipped = cv2.flip(image, flip_code)
        
        return flipped
    
    def random_zoom(self, image: np.ndarray, zoom_range: Tuple[float, float] = (0.9, 1.1)) -> np.ndarray:
        """Zoom aléatoire"""
        if np.random.rand() > self.p:
            return image
        
        zoom_factor = np.random.uniform(*zoom_range)
        h, w = image.shape[:2]
        new_h, new_w = int(h * zoom_factor), int(w * zoom_factor)
        
        # Resize
        zoomed = cv2.resize(image, (new_w, new_h))
        
        # Crop or pad to original size
        if zoom_factor > 1.0:
            # Crop center
            start_h = (new_h - h) // 2
            start_w = (new_w - w) // 2
            zoomed = zoomed[start_h:start_h+h, start_w:start_w+w]
        else:
            # Pad
            pad_h = (h - new_h) // 2
            pad_w = (w - new_w) // 2
            zoomed = cv2.copyMakeBorder(
                zoomed,
                pad_h, h - new_h - pad_h,
                pad_w, w - new_w - pad_w,
                cv2.BORDER_REFLECT
            )
        
        return zoomed
    
    def random_brightness_contrast(
        self,
        image: np.ndarray,
        brightness_range: Tuple[float, float] = (0.9, 1.1),
        contrast_range: Tuple[float, float] = (0.9, 1.1)
    ) -> np.ndarray:
        """Ajustement luminosité et contraste"""
        if np.random.rand() > self.p:
            return image
        
        brightness = np.random.uniform(*brightness_range)
        contrast = np.random.uniform(*contrast_range)
        
        image = image * contrast + brightness
        image = np.clip(image, 0, 1)
        
        return image
    
    def random_gaussian_noise(self, image: np.ndarray, std: float = 0.01) -> np.ndarray:
        """Ajout de bruit gaussien"""
        if np.random.rand() > self.p:
            return image
        
        noise = np.random.normal(0, std, image.shape).astype(np.float32)
        noisy = image + noise
        noisy = np.clip(noisy, 0, 1)
        
        return noisy
    
    def augment(self, image: np.ndarray) -> np.ndarray:
        """Appliquer toutes les augmentations"""
        image = self.random_rotation(image)
        image = self.random_flip(image)
        image = self.random_zoom(image)
        image = self.random_brightness_contrast(image)
        image = self.random_gaussian_noise(image)
        
        return image


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    processor = DICOMProcessor(target_size=(512, 512))
    
    # Test avec un fichier DICOM
    # tensor, metadata = processor.preprocess("test.dcm", return_metadata=True)
    # print(f"Tensor shape: {tensor.shape}")
    # print(f"Metadata: {metadata}")

