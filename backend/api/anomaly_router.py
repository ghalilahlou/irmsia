"""
Anomaly Detection API Router
Endpoints pour détection d'anomalies, segmentation et génération de rapports
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional, List, Dict
from pathlib import Path
import tempfile
import shutil
import logging
from datetime import datetime
import json
import base64

logger = logging.getLogger(__name__)

# Import service avec fallback vers version simple
try:
    from ..services.anomaly_detection_service import get_anomaly_detection_service
    ANOMALY_SERVICE_AVAILABLE = True
except (ImportError, AttributeError) as e:
    logger.warning(f"Service de détection avancé non disponible: {e}. Utilisation du service simple.")
    ANOMALY_SERVICE_AVAILABLE = False
    # Fallback vers service simple
    from ..services.anomaly_detection_service_simple import get_simple_anomaly_detection_service
    def get_anomaly_detection_service():
        return get_simple_anomaly_detection_service()

# Import gRPC client avec gestion d'erreur
try:
    from ..services.grpc_anomaly_client import get_grpc_anomaly_client
    GRPC_CLIENT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"gRPC client non disponible: {e}. Le backend fonctionnera sans gRPC.")
    GRPC_CLIENT_AVAILABLE = False
    get_grpc_anomaly_client = None
# Les DTOs sont optionnels pour compatibilité
try:
    from ..models.dto import AnomalyDetectionResponse, MedicalReportResponse
except ImportError:
    # Fallback si les DTOs n'existent pas encore
    AnomalyDetectionResponse = None
    MedicalReportResponse = None

# Import ANOMALY_CLASSES
try:
    import sys
    from pathlib import Path
    grpc_path = Path(__file__).parent.parent.parent / "grpc-deeplearning" / "data_pipeline"
    sys.path.insert(0, str(grpc_path))
    from models.anomaly_detector import ANOMALY_CLASSES
except ImportError:
    ANOMALY_CLASSES = ['normal', 'tumor', 'infection', 'hemorrhage', 'fracture', 
                       'edema', 'atelectasis', 'pneumothorax', 'consolidation', 'other_anomaly']

router = APIRouter(prefix="/anomaly", tags=["Anomaly Detection"])

# Storage
UPLOAD_DIR = Path("storage/uploads/anomaly")
RESULTS_DIR = Path("storage/results/anomaly")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/detect", response_model=Dict if AnomalyDetectionResponse is None else AnomalyDetectionResponse)
async def detect_anomaly(
    file: UploadFile = File(...),
    return_visualization: bool = True,
    return_segmentation: bool = True
):
    """
    Détecter anomalies dans une image médicale
    
    Args:
        file: Image DICOM, PNG, TIFF, etc.
        return_visualization: Retourner image annotée
        return_segmentation: Retourner mask de segmentation
    
    Returns:
        {
            'has_anomaly': bool,
            'anomaly_class': str,
            'confidence': float,
            'bounding_boxes': List[Dict],
            'segmentation_mask': array (optional),
            'visualization': array (optional),
            'measurements': Dict,
            'image_id': str
        }
    """
    try:
        logger.info(f"Received file for anomaly detection: {file.filename}")
        
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = Path(file.filename).suffix
        saved_path = UPLOAD_DIR / f"upload_{timestamp}{file_ext}"
        
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved to: {saved_path}")
        
        # Try gRPC first, fallback to local service (optimisé avec retry)
        result = None
        grpc_used = False
        
        if GRPC_CLIENT_AVAILABLE and get_grpc_anomaly_client:
            try:
                grpc_client = await get_grpc_anomaly_client()
                health = await grpc_client.health_check()
                
                if health.get('is_healthy', False):
                    logger.info("Using gRPC for anomaly detection")
                    try:
                        result = await grpc_client.detect_anomaly(
                            image_path=str(saved_path),
                            return_visualization=return_visualization,
                            return_segmentation=return_segmentation
                        )
                        grpc_used = True
                        logger.info("✅ gRPC detection successful")
                    except Exception as grpc_error:
                        logger.warning(f"gRPC detection failed: {grpc_error}, falling back to local service")
                        # Fallback automatique
                        grpc_used = False
                else:
                    logger.warning(f"gRPC server not healthy: {health.get('error')}, using local service")
            except Exception as e:
                logger.warning(f"gRPC connection error: {e}, falling back to local service")
        
        # Fallback vers service local si gRPC n'a pas fonctionné
        if not grpc_used or result is None:
            logger.info("Using local anomaly detection service")
            service = get_anomaly_detection_service()
            result = service.detect_anomaly(
                image_path=str(saved_path),
                return_visualization=return_visualization,
                return_segmentation=return_segmentation
            )
            result['backend_used'] = 'local'
        else:
            result['backend_used'] = 'grpc'
        
        # Add metadata
        result['image_id'] = f"{timestamp}{file_ext}"
        result['filename'] = file.filename
        result['timestamp'] = timestamp
        
        # Save results
        result_file = RESULTS_DIR / f"result_{timestamp}.json"
        with open(result_file, 'w') as f:
            # Convert numpy arrays to lists for JSON serialization
            json_result = {
                k: (v.tolist() if hasattr(v, 'tolist') else v)
                for k, v in result.items()
            }
            json.dump(json_result, f, indent=2)
        
        logger.info(f"Detection complete: {result['anomaly_class']} ({result['confidence']:.2%})")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in anomaly detection: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-batch")
async def detect_anomaly_batch(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Détecter anomalies dans plusieurs images (batch)
    """
    try:
        results = []
        
        for file in files:
            # Process each file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            file_ext = Path(file.filename).suffix
            saved_path = UPLOAD_DIR / f"upload_{timestamp}{file_ext}"
            
            with open(saved_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Detect
            service = get_anomaly_detection_service()
            result = service.detect_anomaly(
                image_path=str(saved_path),
                return_visualization=False,  # Skip for batch
                return_segmentation=False
            )
            
            result['filename'] = file.filename
            result['image_id'] = f"{timestamp}{file_ext}"
            
            results.append(result)
        
        return {
            'num_images': len(files),
            'results': results,
            'summary': {
                'total_anomalies': sum(1 for r in results if r.get('has_anomaly')),
                'anomaly_types': list(set(r.get('anomaly_class') for r in results if r.get('has_anomaly')))
            }
        }
        
    except Exception as e:
        logger.error(f"Error in batch detection: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-report", response_model=Dict if MedicalReportResponse is None else MedicalReportResponse)
async def generate_medical_report(
    image_id: str,
    patient_name: Optional[str] = None,
    patient_id: Optional[str] = None,
    patient_age: Optional[int] = None,
    study_description: Optional[str] = None
):
    """
    Générer rapport médical à partir d'une détection
    
    Args:
        image_id: ID de l'image analysée
        patient_name: Nom du patient (optionnel)
        patient_id: ID du patient (optionnel)
        patient_age: Âge du patient (optionnel)
        study_description: Description de l'examen (optionnel)
    
    Returns:
        Rapport médical détaillé avec recommandations
    """
    try:
        # Load detection result
        result_file = None
        for f in RESULTS_DIR.glob(f"result_*.json"):
            with open(f, 'r') as file:
                data = json.load(file)
                if data.get('image_id') == image_id:
                    result_file = f
                    detection_result = data
                    break
        
        if result_file is None:
            raise HTTPException(status_code=404, detail=f"Result not found for image_id: {image_id}")
        
        # Patient info
        patient_info = {
            'name': patient_name or "Non spécifié",
            'id': patient_id or "N/A",
            'age': patient_age,
            'study_description': study_description or "Imagerie médicale"
        }
        
        # Generate report
        service = get_anomaly_detection_service()
        report = service.generate_medical_report(detection_result, patient_info)
        
        # Add patient info
        report['patient_info'] = patient_info
        report['image_id'] = image_id
        report['report_date'] = datetime.now().isoformat()
        
        # Save report
        report_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = RESULTS_DIR / f"report_{report_timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Medical report generated: {report_file}")
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/visualization/{image_id}")
async def get_visualization(image_id: str):
    """
    Récupérer visualisation annotée d'une détection
    """
    try:
        # Find result
        for f in RESULTS_DIR.glob(f"result_*.json"):
            with open(f, 'r') as file:
                data = json.load(file)
                if data.get('image_id') == image_id:
                    vis_data = data.get('visualization')
                    
                    if vis_data is None:
                        raise HTTPException(status_code=404, detail="Visualization not available")
                    
                    # Convert to base64 for transmission
                    import numpy as np
                    vis_array = np.array(vis_data, dtype=np.uint8)
                    
                    # Save as temporary image
                    import cv2
                    temp_file = RESULTS_DIR / f"vis_{image_id}.png"
                    cv2.imwrite(str(temp_file), vis_array)
                    
                    return FileResponse(
                        path=temp_file,
                        media_type="image/png",
                        filename=f"visualization_{image_id}.png"
                    )
        
        raise HTTPException(status_code=404, detail=f"Visualization not found for image_id: {image_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting visualization: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{image_id}")
async def get_detection_result(image_id: str):
    """
    Récupérer résultats d'une détection spécifique
    """
    try:
        for f in RESULTS_DIR.glob(f"result_*.json"):
            with open(f, 'r') as file:
                data = json.load(file)
                if data.get('image_id') == image_id:
                    return data
        
        raise HTTPException(status_code=404, detail=f"Result not found for image_id: {image_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting result: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results")
async def list_detection_results(limit: int = 50):
    """
    Lister tous les résultats de détection
    """
    try:
        results = []
        
        result_files = sorted(
            RESULTS_DIR.glob("result_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:limit]
        
        for f in result_files:
            with open(f, 'r') as file:
                data = json.load(file)
                # Extract summary only
                summary = {
                    'image_id': data.get('image_id'),
                    'filename': data.get('filename'),
                    'timestamp': data.get('timestamp'),
                    'has_anomaly': data.get('has_anomaly'),
                    'anomaly_class': data.get('anomaly_class'),
                    'confidence': data.get('confidence'),
                    'num_regions': data.get('measurements', {}).get('num_regions', 0)
                }
                results.append(summary)
        
        return {
            'total': len(results),
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Error listing results: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/results/{image_id}")
async def delete_detection_result(image_id: str):
    """
    Supprimer résultats d'une détection
    """
    try:
        deleted = False
        
        # Delete result file
        for f in RESULTS_DIR.glob(f"result_*.json"):
            with open(f, 'r') as file:
                data = json.load(file)
                if data.get('image_id') == image_id:
                    f.unlink()
                    deleted = True
                    break
        
        # Delete original upload
        upload_file = UPLOAD_DIR / f"upload_{image_id}"
        if upload_file.exists():
            upload_file.unlink()
            deleted = True
        
        # Delete visualization
        vis_file = RESULTS_DIR / f"vis_{image_id}.png"
        if vis_file.exists():
            vis_file.unlink()
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Result not found for image_id: {image_id}")
        
        return {"message": f"Result {image_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting result: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/grpc/status")
async def get_grpc_status():
    """
    Vérifier statut du serveur gRPC
    """
    if not GRPC_CLIENT_AVAILABLE or not get_grpc_anomaly_client:
        return {
            'grpc_enabled': False,
            'error': 'gRPC client non disponible. Installez grpcio et grpcio-tools.',
            'fallback': 'local_service',
            'installation': 'pip install grpcio grpcio-tools protobuf'
        }
    
    try:
        grpc_client = await get_grpc_anomaly_client()
        health = await grpc_client.health_check()
        
        return {
            'grpc_enabled': True,
            'grpc_address': grpc_client.address,
            'connected': grpc_client._connected,
            'health': health
        }
        
    except Exception as e:
        logger.error(f"Error checking gRPC status: {e}", exc_info=True)
        return {
            'grpc_enabled': False,
            'error': str(e),
            'fallback': 'local_service'
        }


@router.get("/model/info")
async def get_model_info():
    """
    Obtenir informations sur le modèle chargé
    """
    try:
        # Vérifier gRPC d'abord
        if GRPC_CLIENT_AVAILABLE and get_grpc_anomaly_client:
            try:
                grpc_client = await get_grpc_anomaly_client()
                health = await grpc_client.health_check()
                
                if health.get('is_healthy'):
                    return {
                        'backend': 'grpc',
                        'grpc_address': grpc_client.address,
                        'model_loaded': health.get('model_loaded', 'unknown'),
                        'gpu_status': health.get('gpu_status', 'unknown'),
                        'gpu_memory': f"{health.get('gpu_memory_used_mb', 0)}/{health.get('gpu_memory_total_mb', 0)} MB"
                    }
            except Exception as e:
                logger.warning(f"gRPC not available: {e}, using local service info")
        
        # Fallback vers service local
        service = get_anomaly_detection_service()
        
        return {
            'backend': 'local',
            'model_path': service.model_path,
            'device': service.device,
            'model_loaded': service.model is not None,
            'anomaly_classes': ANOMALY_CLASSES,
            'num_classes': len(ANOMALY_CLASSES)
        }
        
    except Exception as e:
        logger.error(f"Error getting model info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/model/reload")
async def reload_model(model_path: Optional[str] = None):
    """
    Recharger le modèle (utile après nouveau training)
    """
    try:
        global _service_instance
        from ..services.anomaly_detection_service import _service_instance
        
        # Clear current instance
        _service_instance = None
        
        # Create new instance with new model
        from ..services.anomaly_detection_service import AnomalyDetectionService
        if model_path:
            _service_instance = AnomalyDetectionService(model_path=model_path)
        else:
            _service_instance = AnomalyDetectionService()
        
        return {
            'message': 'Model reloaded successfully',
            'model_path': _service_instance.model_path,
            'device': _service_instance.device
        }
        
    except Exception as e:
        logger.error(f"Error reloading model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


