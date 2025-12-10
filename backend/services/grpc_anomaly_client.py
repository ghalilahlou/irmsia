"""
gRPC Client pour Anomaly Detection Service
Wrapper pour communiquer avec le serveur gRPC Deep Learning
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional, Dict, List
import logging
import uuid
import base64
import numpy as np
from PIL import Image
import io

logger = logging.getLogger(__name__)

# Import grpc avec gestion d'erreur
try:
    import grpc
    GRPC_AVAILABLE = True
except ImportError:
    logger.warning("grpc non disponible. Le backend fonctionnera sans gRPC.")
    grpc = None
    GRPC_AVAILABLE = False

# Add grpc-deeplearning to path
project_root = Path(__file__).parent.parent.parent
grpc_path = project_root / "grpc-deeplearning"
sys.path.insert(0, str(grpc_path))

# Import proto files (seulement si grpc disponible)
irmsia_dicom_pb2 = None
irmsia_dicom_pb2_grpc = None

if GRPC_AVAILABLE:
    try:
        from proto import irmsia_dicom_pb2
        from proto import irmsia_dicom_pb2_grpc
    except ImportError:
        logger.warning("Proto files not found. Run generate_proto.py first")
        GRPC_AVAILABLE = False
else:
    logger.warning("gRPC non disponible. Le service utilisera uniquement le backend local.")


class GrpcAnomalyClient:
    """
    Client gRPC pour détection d'anomalies
    Communique avec le serveur gRPC Deep Learning
    Optimisé avec retry logic et gestion robuste des erreurs
    """
    
    def __init__(self, host: str = 'localhost', port: int = 50051, max_retries: int = 3):
        self.host = host
        self.port = port
        self.address = f'{host}:{port}'
        self.channel = None
        self.stub = None
        self._connected = False
        self.max_retries = max_retries
        self._connection_lock = asyncio.Lock()
        
    async def connect(self, retry: bool = True):
        """Établir connexion gRPC avec retry logic"""
        if not GRPC_AVAILABLE:
            logger.warning("gRPC non disponible. Le service utilisera uniquement le backend local.")
            self._connected = False
            return
        
        async with self._connection_lock:
            if self._connected and self.channel:
                # Vérifier que la connexion est toujours valide
                try:
                    await asyncio.wait_for(
                        self.channel.get_state(), 
                        timeout=1.0
                    )
                    return
                except:
                    # Connexion perdue, reconnecter
                    self._connected = False
                    if self.channel:
                        await self.channel.close()
            
            retries = 0
            while retries < (self.max_retries if retry else 1):
                try:
                    self.channel = grpc.aio.insecure_channel(
                        self.address,
                        options=[
                            ('grpc.max_send_message_length', 100 * 1024 * 1024),  # 100MB
                            ('grpc.max_receive_message_length', 100 * 1024 * 1024),
                            ('grpc.keepalive_time_ms', 30000),
                            ('grpc.keepalive_timeout_ms', 5000),
                            ('grpc.keepalive_permit_without_calls', True),
                            ('grpc.enable_retries', 1),
                            ('grpc.initial_reconnect_backoff_ms', 1000),
                        ]
                    )
                    
                    if irmsia_dicom_pb2_grpc:
                        self.stub = irmsia_dicom_pb2_grpc.DicomDiagnosticServiceStub(self.channel)
                        
                        # Test connexion avec health check
                        try:
                            await asyncio.wait_for(
                                self.stub.HealthCheck(irmsia_dicom_pb2.Empty()),
                                timeout=5.0
                            )
                            self._connected = True
                            logger.info(f"✅ gRPC client connected to {self.address}")
                            return
                        except asyncio.TimeoutError:
                            logger.warning(f"Health check timeout, retrying... ({retries + 1}/{self.max_retries})")
                            await self.channel.close()
                            self.channel = None
                            retries += 1
                            await asyncio.sleep(1)
                            continue
                    else:
                        logger.error("Proto files not available")
                        return
                        
                except Exception as e:
                    logger.warning(f"Connection attempt {retries + 1} failed: {e}")
                    if self.channel:
                        try:
                            await self.channel.close()
                        except:
                            pass
                    self.channel = None
                    retries += 1
                    if retries < self.max_retries:
                        await asyncio.sleep(2 ** retries)  # Exponential backoff
            
            logger.error(f"❌ Failed to connect to gRPC server after {self.max_retries} attempts")
            self._connected = False
    
    async def disconnect(self):
        """Fermer connexion"""
        if self.channel:
            await self.channel.close()
            self._connected = False
            logger.info("gRPC client disconnected")
    
    async def health_check(self) -> Dict:
        """Vérifier santé du service gRPC"""
        if not GRPC_AVAILABLE:
            return {
                'is_healthy': False,
                'error': 'gRPC non disponible. Installez grpcio et grpcio-tools.'
            }
        
        if not self._connected:
            await self.connect()
        
        if not self.stub:
            return {
                'is_healthy': False,
                'error': 'gRPC stub not available'
            }
        
        try:
            response = await self.stub.HealthCheck(irmsia_dicom_pb2.Empty())
            return {
                'is_healthy': response.is_healthy,
                'gpu_status': response.gpu_status,
                'gpu_memory_used_mb': response.gpu_memory_used_mb,
                'gpu_memory_total_mb': response.gpu_memory_total_mb,
                'model_loaded': response.model_loaded,
                'uptime_seconds': response.uptime_seconds
            }
        except grpc.RpcError as e:
            logger.error(f"Health check failed: {e.code()} - {e.details()}")
            return {
                'is_healthy': False,
                'error': f"{e.code()}: {e.details()}"
            }
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {
                'is_healthy': False,
                'error': str(e)
            }
    
    async def detect_anomaly(
        self,
        image_path: str,
        return_visualization: bool = True,
        return_segmentation: bool = True
    ) -> Dict:
        """
        Détecter anomalies via gRPC
        
        Args:
            image_path: Chemin vers l'image (DICOM, PNG, TIFF)
            return_visualization: Retourner image annotée
            return_segmentation: Retourner mask de segmentation
        
        Returns:
            Dict avec résultats de détection
        """
        if not GRPC_AVAILABLE:
            # Fallback automatique vers service local
            logger.info("gRPC non disponible, utilisation du service local")
            from .anomaly_detection_service import get_anomaly_detection_service
            service = get_anomaly_detection_service()
            return service.detect_anomaly(
                image_path=image_path,
                return_visualization=return_visualization,
                return_segmentation=return_segmentation
            )
        
        if not self._connected:
            await self.connect()
        
        if not self.stub:
            # Fallback vers service local si gRPC non disponible
            logger.warning("gRPC not available, using local service")
            from .anomaly_detection_service import get_anomaly_detection_service
            service = get_anomaly_detection_service()
            return service.detect_anomaly(
                image_path=image_path,
                return_visualization=return_visualization,
                return_segmentation=return_segmentation
            )
        
        try:
            # Lire fichier image
            image_path_obj = Path(image_path)
            
            if image_path_obj.suffix.lower() in ['.dcm', '.dicom']:
                # DICOM file
                with open(image_path, 'rb') as f:
                    dicom_data = f.read()
            else:
                # Image standard (PNG, TIFF, etc.)
                img = Image.open(image_path)
                # Convertir en bytes
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                dicom_data = buffer.getvalue()
            
            # Créer requête
            request_id = str(uuid.uuid4())
            
            # Créer métadonnées basiques
            metadata = irmsia_dicom_pb2.DicomMetadata(
                patient_id="anonymous",
                study_id=request_id,
                modality="MRI"  # À détecter automatiquement
            )
            
            # Options de diagnostic
            options = irmsia_dicom_pb2.DiagnosticOptions(
                confidence_threshold=0.5,
                include_segmentation=return_segmentation,
                include_gradcam=return_visualization,  # GradCAM pour visualisation explicative
                fast_mode=False
            )
            
            # Créer requête DICOM
            request = irmsia_dicom_pb2.DicomRequest(
                request_id=request_id,
                dicom_data=dicom_data,
                metadata=metadata,
                options=options
            )
            
            # Appel gRPC avec retry
            logger.info(f"Calling gRPC DiagnoseDicom for {image_path}")
            retries = 0
            response = None
            
            while retries < self.max_retries:
                try:
                    response = await asyncio.wait_for(
                        self.stub.DiagnoseDicom(request),
                        timeout=60.0  # 60 secondes timeout pour inference
                    )
                    break
                except grpc.RpcError as e:
                    if e.code() == grpc.StatusCode.UNAVAILABLE:
                        logger.warning(f"gRPC unavailable, retrying... ({retries + 1}/{self.max_retries})")
                        await self.connect(retry=False)  # Reconnecter
                        retries += 1
                        if retries < self.max_retries:
                            await asyncio.sleep(1)
                        else:
                            raise
                    else:
                        raise
                except asyncio.TimeoutError:
                    logger.warning(f"gRPC timeout, retrying... ({retries + 1}/{self.max_retries})")
                    retries += 1
                    if retries < self.max_retries:
                        await asyncio.sleep(2)
                    else:
                        raise Exception("gRPC request timeout after retries")
            
            if response is None:
                raise Exception("Failed to get response from gRPC server")
            
            # Convertir réponse en format dict
            return self._convert_grpc_response_to_dict(
                response,
                return_visualization=return_visualization,
                return_segmentation=return_segmentation
            )
            
        except grpc.RpcError as e:
            logger.error(f"gRPC error: {e.code()} - {e.details()}")
            # Fallback vers service local
            logger.info("Falling back to local anomaly detection service")
            from .anomaly_detection_service import get_anomaly_detection_service
            service = get_anomaly_detection_service()
            return service.detect_anomaly(
                image_path=image_path,
                return_visualization=return_visualization,
                return_segmentation=return_segmentation
            )
        except Exception as e:
            logger.error(f"Error in gRPC anomaly detection: {e}", exc_info=True)
            raise
    
    def _convert_grpc_response_to_dict(
        self,
        response: 'irmsia_dicom_pb2.DiagnosticResponse',
        return_visualization: bool = True,
        return_segmentation: bool = True
    ) -> Dict:
        """Convertir réponse gRPC en format dict pour API REST"""
        
        if response.status != irmsia_dicom_pb2.DiagnosticStatus.COMPLETED:
            return {
                'has_anomaly': False,
                'error': response.message,
                'status': response.status
            }
        
        result = response.result
        
        # Classification
        classification = result.classification
        has_anomaly = classification.primary_diagnosis.lower() != 'normal'
        confidence = classification.confidence
        
        # Déterminer classe d'anomalie
        anomaly_class = 'normal'
        if result.findings:
            # Prendre la première finding comme classe principale
            primary_finding = result.findings[0]
            anomaly_class = primary_finding.pathology.lower() if primary_finding.pathology else 'unknown'
        
        # Bounding boxes avec calcul du périmètre depuis les masks
        bounding_boxes = []
        pixel_to_mm = 0.5  # Ratio par défaut, à améliorer avec métadonnées DICOM
        
        for i, finding in enumerate(result.findings):
            if finding.bbox:
                bbox = finding.bbox
                measurements = finding.measurements
                
                # Calculer périmètre depuis le mask de segmentation si disponible
                perimeter_pixels = 0.0
                perimeter_mm = 0.0
                
                if return_segmentation and result.segmentations:
                    # Trouver le mask correspondant à ce finding
                    for seg in result.segmentations:
                        if seg.structure_name.lower() == finding.pathology.lower() or i < len(result.segmentations):
                            try:
                                mask_img = Image.open(io.BytesIO(seg.mask_data))
                                mask_array = np.array(mask_img.convert('L'))
                                
                                # Calculer le périmètre avec OpenCV
                                import cv2
                                contours, _ = cv2.findContours(
                                    (mask_array > 127).astype(np.uint8),
                                    cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE
                                )
                                
                                if contours:
                                    # Prendre le plus grand contour
                                    largest_contour = max(contours, key=cv2.contourArea)
                                    perimeter_pixels = cv2.arcLength(largest_contour, True)
                                    perimeter_mm = perimeter_pixels * pixel_to_mm
                                
                                break
                            except Exception as e:
                                logger.warning(f"Failed to calculate perimeter from mask: {e}")
                                # Fallback: estimer depuis bounding box
                                perimeter_pixels = 2 * (bbox.width + bbox.height)
                                perimeter_mm = perimeter_pixels * pixel_to_mm
                            break
                
                # Si pas de mask, estimer depuis bounding box
                if perimeter_pixels == 0.0:
                    perimeter_pixels = 2 * (bbox.width + bbox.height)
                    perimeter_mm = perimeter_pixels * pixel_to_mm
                
                # Calculer dimensions réelles
                width_mm = bbox.width * pixel_to_mm
                height_mm = bbox.height * pixel_to_mm
                area_pixels = float(bbox.width * bbox.height)
                area_mm2 = measurements.size_mm if measurements and measurements.size_mm > 0 else (area_pixels * pixel_to_mm ** 2)
                
                bounding_boxes.append({
                    'id': i,
                    'x': bbox.x,
                    'y': bbox.y,
                    'width': bbox.width,
                    'height': bbox.height,
                    'area_pixels': area_pixels,
                    'area_mm2': float(area_mm2),
                    'perimeter_pixels': float(perimeter_pixels),
                    'perimeter_mm': float(perimeter_mm),
                    'width_mm': float(width_mm),
                    'height_mm': float(height_mm),
                    'pathology': finding.pathology,
                    'confidence': finding.confidence,
                    'severity': finding.severity
                })
        
        # Segmentation masks
        segmentation_mask = None
        if return_segmentation and result.segmentations:
            # Prendre le premier mask
            seg = result.segmentations[0]
            # Décompresser mask_data (PNG bytes)
            try:
                mask_img = Image.open(io.BytesIO(seg.mask_data))
                mask_array = np.array(mask_img.convert('L'))
                segmentation_mask = mask_array.tolist()
            except Exception as e:
                logger.warning(f"Failed to decode segmentation mask: {e}")
        
        # Visualization (GradCAM heatmap)
        visualization = None
        if return_visualization and result.gradcam_heatmap:
            try:
                vis_img = Image.open(io.BytesIO(result.gradcam_heatmap))
                vis_array = np.array(vis_img)
                # Convertir en format RGB si nécessaire
                if len(vis_array.shape) == 2:
                    # Grayscale -> RGB
                    vis_array = np.stack([vis_array] * 3, axis=-1)
                visualization = vis_array.tolist()
                logger.info(f"Visualization decoded: {vis_array.shape}")
            except Exception as e:
                logger.warning(f"Failed to decode visualization: {e}")
                # Essayer de créer une visualisation basique à partir des bounding boxes
                if bounding_boxes:
                    visualization = self._create_basic_visualization(
                        result.analysis_metadata.image_width if result.analysis_metadata else 512,
                        result.analysis_metadata.image_height if result.analysis_metadata else 512,
                        bounding_boxes
                    )
        
        # Mesures globales
        measurements = {
            'num_regions': len(result.findings),
            'total_area_pixels': sum(bbox['area_pixels'] for bbox in bounding_boxes),
            'total_area_mm2': sum(bbox['area_mm2'] for bbox in bounding_boxes),
            'pixel_to_mm_ratio': 0.5,  # À extraire des métadonnées DICOM
            'image_size': {
                'width': result.analysis_metadata.image_width if result.analysis_metadata else 0,
                'height': result.analysis_metadata.image_height if result.analysis_metadata else 0
            }
        }
        
        # Probabilités de classes
        all_probabilities = {}
        for class_prob in classification.class_probabilities:
            all_probabilities[class_prob.class_name] = class_prob.probability
        
        return {
            'has_anomaly': has_anomaly,
            'anomaly_class': anomaly_class,
            'confidence': float(confidence),
            'all_probabilities': all_probabilities,
            'bounding_boxes': bounding_boxes,
            'segmentation_mask': segmentation_mask,
            'visualization': visualization,
            'measurements': measurements,
            'request_id': response.request_id,
            'model_used': result.model_used,
            'processing_time_seconds': result.processing_time_seconds,
            'risk_score': result.risk.risk_score if result.risk else 0,
            'recommendations': list(result.recommendations) if result.recommendations else [],
            'risk_assessment': {
                'risk_score': result.risk.risk_score if result.risk else 0,
                'risk_level': result.risk.risk_level if result.risk else 0,
                'risk_category': result.risk.risk_category if result.risk else 'Unknown',
                'urgency_level': result.risk.urgency_level if result.risk else 'Routine'
            }
        }
    
    def _create_basic_visualization(self, width: int, height: int, bounding_boxes: List[Dict]) -> List:
        """Créer une visualisation basique à partir des bounding boxes"""
        try:
            from PIL import Image, ImageDraw
            import numpy as np
            
            # Créer image noire
            img = Image.new('RGB', (width, height), color='black')
            draw = ImageDraw.Draw(img)
            
            # Dessiner bounding boxes
            for bbox in bounding_boxes:
                x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']
                # Couleur selon pathologie
                color = '#00ffff'  # Cyan par défaut
                if 'tumor' in bbox.get('pathology', '').lower():
                    color = '#ff0000'  # Rouge pour tumeur
                elif 'hemorrhage' in bbox.get('pathology', '').lower():
                    color = '#ff8800'  # Orange pour hémorragie
                
                draw.rectangle([x, y, x + w, y + h], outline=color, width=3)
            
            return np.array(img).tolist()
        except Exception as e:
            logger.warning(f"Failed to create basic visualization: {e}")
            return None


# Singleton instance
_grpc_client_instance = None

async def get_grpc_anomaly_client() -> GrpcAnomalyClient:
    """Get singleton instance of gRPC anomaly client"""
    import os
    global _grpc_client_instance
    if _grpc_client_instance is None:
        # Utiliser les variables d'environnement pour Docker
        host = os.getenv('GRPC_DL_HOST', 'localhost')
        port = int(os.getenv('GRPC_DL_PORT', '50051'))
        _grpc_client_instance = GrpcAnomalyClient(host=host, port=port)
        await _grpc_client_instance.connect()
    return _grpc_client_instance

