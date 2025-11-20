"""
Routes de debug pour inspecter les fichiers DICOM
Permet de voir le contenu réel des fichiers DICOM
"""

import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import pydicom
import numpy as np

from backend.services.dicom_converter import dicom_converter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/debug", tags=["Debug"])


@router.get("/dicom/{filename}/info")
async def inspect_dicom_file(filename: str) -> Dict[str, Any]:
    """
    Inspecte un fichier DICOM et retourne ses métadonnées et statistiques des pixels
    """
    try:
        dicom_path = dicom_converter.dicom_dir / filename
        
        if not dicom_path.exists():
            raise HTTPException(status_code=404, detail=f"Fichier DICOM non trouvé: {filename}")
        
        # Lire le fichier DICOM
        ds = pydicom.dcmread(str(dicom_path))
        
        # Extraire les métadonnées importantes
        metadata = {
            "filename": filename,
            "modality": getattr(ds, 'Modality', 'N/A'),
            "rows": getattr(ds, 'Rows', 'N/A'),
            "columns": getattr(ds, 'Columns', 'N/A'),
            "bits_allocated": getattr(ds, 'BitsAllocated', 'N/A'),
            "bits_stored": getattr(ds, 'BitsStored', 'N/A'),
            "high_bit": getattr(ds, 'HighBit', 'N/A'),
            "pixel_representation": getattr(ds, 'PixelRepresentation', 'N/A'),
            "samples_per_pixel": getattr(ds, 'SamplesPerPixel', 'N/A'),
            "photometric_interpretation": getattr(ds, 'PhotometricInterpretation', 'N/A'),
            "window_center": getattr(ds, 'WindowCenter', None),
            "window_width": getattr(ds, 'WindowWidth', None),
        }
        
        # Analyser le pixel array
        try:
            pixel_array = ds.pixel_array
            
            pixel_stats = {
                "shape": list(pixel_array.shape),
                "dtype": str(pixel_array.dtype),
                "min": float(pixel_array.min()),
                "max": float(pixel_array.max()),
                "mean": float(pixel_array.mean()),
                "std": float(pixel_array.std()),
                "unique_values_count": len(np.unique(pixel_array)),
            }
            
            # Vérifier si c'est du bruit aléatoire
            # Si tous les pixels sont uniques ou presque, c'est probablement du bruit
            total_pixels = pixel_array.size
            unique_ratio = pixel_stats["unique_values_count"] / total_pixels
            
            # Critères pour détecter le bruit:
            # 1. Ratio de valeurs uniques > 90% = bruit
            # 2. Écart-type très faible par rapport à la plage = image uniforme
            # 3. Écart-type très élevé avec ratio unique élevé = bruit aléatoire
            value_range = pixel_stats["max"] - pixel_stats["min"]
            std_ratio = pixel_stats["std"] / (value_range + 1e-10)
            
            is_noise = unique_ratio > 0.9 or (unique_ratio > 0.5 and std_ratio > 0.8)
            is_uniform = std_ratio < 0.05
            
            pixel_stats["is_likely_noise"] = is_noise
            pixel_stats["is_uniform"] = is_uniform
            pixel_stats["unique_ratio"] = unique_ratio
            pixel_stats["std_ratio"] = std_ratio
            pixel_stats["value_range"] = value_range
            
            # Échantillon des premières valeurs (pour debug)
            if total_pixels > 0:
                sample_size = min(20, total_pixels)
                pixel_stats["sample_values"] = pixel_array.flatten()[:sample_size].tolist()
            
        except Exception as e:
            pixel_stats = {
                "error": f"Impossible d'extraire les pixels: {str(e)}"
            }
        
        return JSONResponse({
            "status": "success",
            "metadata": metadata,
            "pixel_stats": pixel_stats,
            "file_size": dicom_path.stat().st_size,
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'inspection du fichier DICOM {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/dicom/list-all")
async def list_all_dicoms_with_info() -> Dict[str, Any]:
    """
    Liste tous les fichiers DICOM avec leurs informations de base
    """
    try:
        dicom_files = []
        
        for file_path in dicom_converter.dicom_dir.glob("*.dcm"):
            try:
                ds = pydicom.dcmread(str(file_path), stop_before_pixels=True)
                
                dicom_files.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "modality": getattr(ds, 'Modality', 'N/A'),
                    "rows": getattr(ds, 'Rows', 'N/A'),
                    "columns": getattr(ds, 'Columns', 'N/A'),
                })
            except Exception as e:
                dicom_files.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "error": str(e)
                })
        
        return JSONResponse({
            "status": "success",
            "count": len(dicom_files),
            "files": dicom_files
        })
        
    except Exception as e:
        logger.error(f"Erreur lors du listing des DICOM: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

