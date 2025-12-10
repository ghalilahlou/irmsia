"""
Unified Analysis API Routes
Combines anomaly detection, segmentation, visualization, and reporting
"""

import logging
import time
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Optional
import tempfile
import os

from backend.api.auth_router import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["Analysis"])


# Lazy imports for services
def get_detector():
    """Get anomaly detector with lazy loading - uses trained models"""
    try:
        from backend.services.analysis import get_anomaly_detector
        detector = get_anomaly_detector()
        logger.info(f"Detector loaded: {detector.device}")
        return detector
    except Exception as e:
        logger.warning(f"Could not load detector: {e}")
        return None


def get_visualizer():
    """Get visualization service with lazy loading"""
    try:
        from backend.services.analysis.visualization import get_visualization_service
        return get_visualization_service()
    except Exception as e:
        logger.warning(f"Could not load visualizer: {e}")
        return None


def get_segmenter():
    """Get segmentation service with lazy loading"""
    try:
        from backend.services.analysis.segmentation import get_segmentation_service
        return get_segmentation_service()
    except Exception as e:
        logger.warning(f"Could not load segmenter: {e}")
        return None


def get_reporter():
    """Get report generator with lazy loading"""
    try:
        from backend.services.reports.generator import get_report_generator
        return get_report_generator()
    except Exception as e:
        logger.warning(f"Could not load reporter: {e}")
        return None


@router.post("/detect")
async def detect_anomalies(
    file: UploadFile = File(...),
    include_segmentation: bool = True,
    include_visualization: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """
    Detect anomalies in a medical image
    
    Args:
        file: Image file (DICOM, PNG, JPEG)
        include_segmentation: Whether to include segmentation results
        include_visualization: Whether to include visualizations
        
    Returns:
        Complete analysis results with detection, segmentation, and visualizations
    """
    start_time = time.time()
    
    # Validate file
    allowed_extensions = ['.dcm', '.dicom', '.png', '.jpg', '.jpeg']
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Format non supporté. Formats acceptés: {', '.join(allowed_extensions)}"
        )
    
    # Save uploaded file temporarily
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir) / file.filename
    
    try:
        # Write file
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # Get detector
        detector = get_detector()
        if detector is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service de détection non disponible"
            )
        
        # Run detection with trained model
        detection_result = detector.detect(str(temp_path))
        
        # Prepare response with detailed analysis
        response = {
            "status": "success",
            "has_anomaly": detection_result.has_anomaly,
            "anomaly_class": detection_result.anomaly_class,
            "anomaly_name": detection_result.anomaly_name,
            "confidence": detection_result.confidence,
            "severity": detection_result.severity,
            "urgency": detection_result.urgency,
            "description": detection_result.description,
            "recommendations": detection_result.recommendations,
            "bounding_boxes": detection_result.bounding_boxes,
            "attention_regions": detection_result.attention_regions,
            "measurements": detection_result.measurements,
            "top_predictions": detection_result.top_predictions,
            "model_info": detection_result.model_info,
            "metadata": detection_result.metadata,
        }
        
        # Add segmentation if requested
        if include_segmentation:
            segmenter = get_segmenter()
            if segmenter:
                try:
                    import numpy as np
                    from PIL import Image
                    
                    # Load image
                    if file_ext in ['.dcm', '.dicom']:
                        import pydicom
                        ds = pydicom.dcmread(str(temp_path))
                        image = ds.pixel_array.astype(np.float32)
                        pixel_spacing = [float(x) for x in ds.PixelSpacing] if hasattr(ds, 'PixelSpacing') else None
                    else:
                        img = Image.open(str(temp_path)).convert('L')
                        image = np.array(img, dtype=np.float32) / 255.0
                        pixel_spacing = None
                    
                    seg_result = segmenter.segment(image, pixel_spacing)
                    response["segmentation"] = {
                        "regions": seg_result.regions,
                        "measurements": seg_result.measurements,
                    }
                except Exception as e:
                    logger.warning(f"Segmentation failed: {e}")
        
        # Add visualizations if requested
        if include_visualization:
            visualizer = get_visualizer()
            if visualizer:
                try:
                    import numpy as np
                    from PIL import Image
                    
                    # Load image
                    if file_ext in ['.dcm', '.dicom']:
                        import pydicom
                        ds = pydicom.dcmread(str(temp_path))
                        image = ds.pixel_array.astype(np.float32)
                        image = (image - image.min()) / (image.max() - image.min() + 1e-8)
                    else:
                        img = Image.open(str(temp_path)).convert('L')
                        image = np.array(img, dtype=np.float32) / 255.0
                    
                    # Use detection result's heatmap and segmentation mask if available
                    visuals = {}
                    
                    # Original image
                    visuals['original'] = visualizer.image_to_base64(image)
                    
                    # Annotated image with bounding boxes
                    if detection_result.bounding_boxes:
                        annotated = visualizer.create_annotated_image(
                            image,
                            detection_result.bounding_boxes,
                            detection_result.anomaly_class
                        )
                        visuals['annotated'] = visualizer.image_to_base64(annotated)
                    
                    # GradCAM heatmap
                    if detection_result.heatmap is not None:
                        heatmap_overlay = visualizer.create_heatmap_overlay(
                            image, detection_result.heatmap
                        )
                        visuals['heatmap'] = visualizer.image_to_base64(heatmap_overlay)
                    
                    # Segmentation mask
                    if detection_result.segmentation_mask is not None:
                        seg_overlay = visualizer.create_segmentation_overlay(
                            image, detection_result.segmentation_mask
                        )
                        visuals['segmentation'] = visualizer.image_to_base64(seg_overlay)
                    
                    # Zoomed regions
                    if detection_result.bounding_boxes:
                        zoomed = []
                        for box in detection_result.bounding_boxes[:3]:
                            zoomed_img = visualizer.create_zoom_view(image, box)
                            zoomed.append(visualizer.image_to_base64(zoomed_img))
                        visuals['zoomed_regions'] = zoomed
                    
                    response["visualizations"] = visuals
                except Exception as e:
                    logger.warning(f"Visualization failed: {e}")
        
        # Add timing
        response["processing_time_ms"] = (time.time() - start_time) * 1000
        
        return JSONResponse(response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur d'analyse: {str(e)}"
        )
    finally:
        # Cleanup
        try:
            os.unlink(temp_path)
            os.rmdir(temp_dir)
        except:
            pass


@router.post("/report")
async def generate_report(
    file: UploadFile = File(...),
    modality: str = "UNKNOWN",
    format: str = "json",
    current_user: dict = Depends(get_current_user)
):
    """
    Generate a complete medical analysis report
    
    Args:
        file: Image file
        modality: Imaging modality (CT, MRI, X-Ray, etc.)
        format: Output format (json, text)
        
    Returns:
        Complete medical report
    """
    start_time = time.time()
    
    # Validate file
    allowed_extensions = ['.dcm', '.dicom', '.png', '.jpg', '.jpeg']
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Format non supporté"
        )
    
    # Save uploaded file temporarily
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir) / file.filename
    
    try:
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # Get services
        detector = get_detector()
        segmenter = get_segmenter()
        visualizer = get_visualizer()
        reporter = get_reporter()
        
        if detector is None or reporter is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Services non disponibles"
            )
        
        # Run detection
        detection_result = detector.detect(str(temp_path))
        
        # Run segmentation
        segmentation_result = None
        if segmenter:
            try:
                import numpy as np
                from PIL import Image
                
                if file_ext in ['.dcm', '.dicom']:
                    import pydicom
                    ds = pydicom.dcmread(str(temp_path))
                    image = ds.pixel_array.astype(np.float32)
                    pixel_spacing = [float(x) for x in ds.PixelSpacing] if hasattr(ds, 'PixelSpacing') else None
                else:
                    img = Image.open(str(temp_path)).convert('L')
                    image = np.array(img, dtype=np.float32) / 255.0
                    pixel_spacing = None
                
                segmentation_result = segmenter.segment(image, pixel_spacing)
            except Exception as e:
                logger.warning(f"Segmentation failed: {e}")
        
        # Generate visualizations
        visualizations = None
        if visualizer:
            try:
                import numpy as np
                from PIL import Image
                
                if file_ext in ['.dcm', '.dicom']:
                    import pydicom
                    ds = pydicom.dcmread(str(temp_path))
                    image = ds.pixel_array.astype(np.float32)
                    image = (image - image.min()) / (image.max() - image.min() + 1e-8)
                else:
                    img = Image.open(str(temp_path)).convert('L')
                    image = np.array(img, dtype=np.float32) / 255.0
                
                visualizations = visualizer.generate_analysis_report_visuals(image, detection_result)
            except Exception as e:
                logger.warning(f"Visualization failed: {e}")
        
        # Generate report
        processing_time = (time.time() - start_time) * 1000
        
        report = reporter.generate_report(
            image_id=file.filename,
            detection_result=detection_result,
            segmentation_result=segmentation_result,
            visualizations=visualizations,
            modality=modality,
            processing_time_ms=processing_time
        )
        
        # Return in requested format
        if format == "text":
            return JSONResponse({
                "status": "success",
                "format": "text",
                "report": reporter.export_to_text(report)
            })
        else:
            return JSONResponse({
                "status": "success",
                "format": "json",
                "report": report.to_dict()
            })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de génération du rapport: {str(e)}"
        )
    finally:
        try:
            os.unlink(temp_path)
            os.rmdir(temp_dir)
        except:
            pass


@router.get("/status")
async def get_analysis_status():
    """Get analysis service status"""
    status_info = {
        "detector": False,
        "segmenter": False,
        "visualizer": False,
        "reporter": False,
        "backend": "none",
        "device": "cpu",
        "model_loaded": False
    }
    
    detector = get_detector()
    if detector:
        status_info["detector"] = True
        status_info["device"] = detector.device
        status_info["model_loaded"] = detector.model_loader is not None and detector.model_loader.model is not None
        if detector.model_loader:
            status_info["backend"] = detector.model_loader.model_type or "fallback"
    
    if get_segmenter():
        status_info["segmenter"] = True
    
    if get_visualizer():
        status_info["visualizer"] = True
    
    if get_reporter():
        status_info["reporter"] = True
    
    return JSONResponse(status_info)


@router.get("/anomaly-classes")
async def get_anomaly_classes():
    """
    Get all available anomaly classes with descriptions
    
    Returns:
        List of anomaly classes with detailed information
    """
    try:
        from backend.services.analysis import ANOMALY_CLASSES, ANOMALY_DESCRIPTIONS
        
        classes = []
        for i, class_name in enumerate(ANOMALY_CLASSES):
            info = ANOMALY_DESCRIPTIONS.get(class_name, {})
            classes.append({
                "id": i,
                "name": class_name,
                "display_name": info.get("name", class_name),
                "description": info.get("description", ""),
                "severity": info.get("severity", "unknown"),
                "urgency": info.get("urgency", "routine"),
                "recommendations": info.get("recommendations", [])
            })
        
        return JSONResponse({
            "status": "success",
            "total_classes": len(classes),
            "classes": classes
        })
    except Exception as e:
        logger.error(f"Failed to get anomaly classes: {e}")
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

