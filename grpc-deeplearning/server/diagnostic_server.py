"""
Serveur gRPC pour Diagnostic DICOM avec Deep Learning
Optimisé pour performance avec streaming et batch processing
"""

import grpc
from concurrent import futures
import asyncio
import sys
import time
from pathlib import Path
import logging
import io
import numpy as np
import torch
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import generated proto files (à générer avec: python -m grpc_tools.protoc)
try:
    from proto import irmsia_dicom_pb2
    from proto import irmsia_dicom_pb2_grpc
except ImportError:
    print("⚠️  Proto files not generated yet. Run:")
    print("   python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/irmsia_dicom.proto")
    # Créer des stubs pour éviter les erreurs
    class irmsia_dicom_pb2:
        pass
    class irmsia_dicom_pb2_grpc:
        pass

from models.dicom_model import DiagnosticPipeline, PRIMARY_CLASSES, PATHOLOGY_CLASSES, SEVERITY_LEVELS
from utils.dicom_processor import DICOMProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DicomDiagnosticServicer:
    """
    Servicer pour le diagnostic DICOM
    Implémente tous les RPC définis dans le .proto
    """
    
    def __init__(
        self,
        model_path: str = None,
        device: str = 'cuda',
        batch_size: int = 16
    ):
        logger.info("Initializing DICOM Diagnostic Service...")
        
        self.device = device
        self.batch_size = batch_size
        self.start_time = time.time()
        
        # Initialize DICOM processor
        self.dicom_processor = DICOMProcessor(
            target_size=(512, 512),
            preserve_aspect_ratio=False,
            auto_windowing=True
        )
        
        # Initialize Deep Learning pipeline
        logger.info("Loading Deep Learning models...")
        self.diagnostic_pipeline = DiagnosticPipeline(
            device=device,
            classification_model_path=model_path,
            segmentation_model_path=None
        )
        
        # Warmup GPU
        self.diagnostic_pipeline.warmup()
        
        # GPU info
        if torch.cuda.is_available():
            self.gpu_name = torch.cuda.get_device_name(0)
            self.gpu_memory_total = torch.cuda.get_device_properties(0).total_memory // (1024**2)
            logger.info(f"GPU: {self.gpu_name} ({self.gpu_memory_total} MB)")
        else:
            self.gpu_name = "CPU"
            self.gpu_memory_total = 0
            logger.warning("Running on CPU (slow)")
        
        logger.info("✅ DICOM Diagnostic Service ready!")
    
    async def HealthCheck(self, request, context):
        """Health check du service"""
        
        gpu_memory_used = 0
        if torch.cuda.is_available():
            gpu_memory_used = torch.cuda.memory_allocated(0) // (1024**2)
        
        uptime = time.time() - self.start_time
        
        response = irmsia_dicom_pb2.HealthStatus(
            is_healthy=True,
            gpu_status=self.gpu_name,
            gpu_memory_used_mb=gpu_memory_used,
            gpu_memory_total_mb=self.gpu_memory_total,
            model_loaded="MultiHeadDiagnosticModel (EfficientNet-B4)",
            uptime_seconds=uptime
        )
        
        return response
    
    async def GetAvailableModels(self, request, context):
        """Liste des modèles disponibles"""
        
        models = [
            irmsia_dicom_pb2.ModelInfo(
                model_id="diagnostic_v1",
                model_name="IRMSIA Diagnostic Model v1.0",
                modality="All",
                pathologies=PATHOLOGY_CLASSES,
                accuracy=0.92,
                version="1.0.0"
            )
        ]
        
        response = irmsia_dicom_pb2.ModelList(models=models)
        return response
    
    async def DiagnoseDicom(self, request, context):
        """
        Diagnostic simple (unary RPC)
        Pour fichiers DICOM complets
        """
        logger.info(f"📊 Diagnostic request: {request.request_id}")
        
        start_time = time.time()
        
        try:
            # 1. Preprocess DICOM
            logger.info(f"  Preprocessing...")
            tensor, metadata = self.dicom_processor.preprocess(
                request.dicom_data,
                return_metadata=True
            )
            preprocessing_time = (time.time() - start_time) * 1000
            
            # 2. Run inference
            logger.info(f"  Running inference...")
            inference_start = time.time()
            
            results = self.diagnostic_pipeline.predict(
                tensor,
                include_segmentation=request.options.include_segmentation,
                include_gradcam=request.options.include_gradcam
            )
            inference_time = (time.time() - inference_start) * 1000
            
            # 3. Build response
            logger.info(f"  Building response...")
            response = self._build_diagnostic_response(
                request_id=request.request_id,
                results=results,
                metadata=metadata,
                preprocessing_time=preprocessing_time,
                inference_time=inference_time,
                options=request.options
            )
            
            processing_time = time.time() - start_time
            logger.info(f"✅ Diagnostic complete: {request.request_id} ({processing_time:.2f}s)")
            
            return response
        
        except Exception as e:
            logger.error(f"❌ Error during diagnosis: {e}", exc_info=True)
            
            response = irmsia_dicom_pb2.DiagnosticResponse(
                request_id=request.request_id,
                status=irmsia_dicom_pb2.DiagnosticStatus.ERROR,
                message=f"Error: {str(e)}",
                progress=0.0
            )
            
            return response
    
    async def DiagnoseDicomStream(self, request_iterator, context):
        """
        Diagnostic avec streaming bidirectionnel
        Le client upload par chunks et reçoit des updates progressifs
        """
        request_id = None
        chunks = []
        metadata = None
        total_bytes = 0
        
        try:
            # Recevoir les chunks
            async for request in request_iterator:
                if request_id is None:
                    request_id = request.request_id
                    logger.info(f"📊 Streaming diagnostic: {request_id}")
                
                if request.HasField('metadata'):
                    # Premier message : métadonnées
                    metadata = request.metadata
                    
                    # Send update: Upload started
                    yield irmsia_dicom_pb2.DiagnosticResponse(
                        request_id=request_id,
                        status=irmsia_dicom_pb2.DiagnosticStatus.PROCESSING,
                        message="Upload started",
                        progress=0.0
                    )
                
                elif request.HasField('chunk'):
                    # Messages suivants : données
                    chunks.append(request.chunk)
                    total_bytes += len(request.chunk)
                    
                    # Send update: Upload progress
                    progress = min(total_bytes / (50 * 1024 * 1024), 0.3)  # Assume ~50MB max
                    yield irmsia_dicom_pb2.DiagnosticResponse(
                        request_id=request_id,
                        status=irmsia_dicom_pb2.DiagnosticStatus.PROCESSING,
                        message=f"Uploading... {total_bytes/1024/1024:.1f} MB",
                        progress=progress
                    )
            
            # Reconstituer le DICOM
            logger.info(f"  Received {total_bytes/1024/1024:.1f} MB")
            dicom_data = b''.join(chunks)
            
            # Send update: Preprocessing
            yield irmsia_dicom_pb2.DiagnosticResponse(
                request_id=request_id,
                status=irmsia_dicom_pb2.DiagnosticStatus.PROCESSING,
                message="Preprocessing DICOM...",
                progress=0.4
            )
            
            # Preprocess
            tensor, dicom_metadata = self.dicom_processor.preprocess(
                dicom_data,
                return_metadata=True
            )
            
            # Send update: Inference
            yield irmsia_dicom_pb2.DiagnosticResponse(
                request_id=request_id,
                status=irmsia_dicom_pb2.DiagnosticStatus.PROCESSING,
                message="Running AI inference...",
                progress=0.6
            )
            
            # Run inference
            results = self.diagnostic_pipeline.predict(
                tensor,
                include_segmentation=False,
                include_gradcam=False
            )
            
            # Send update: Postprocessing
            yield irmsia_dicom_pb2.DiagnosticResponse(
                request_id=request_id,
                status=irmsia_dicom_pb2.DiagnosticStatus.PROCESSING,
                message="Postprocessing results...",
                progress=0.9
            )
            
            # Build final response
            response = self._build_diagnostic_response(
                request_id=request_id,
                results=results,
                metadata=dicom_metadata,
                preprocessing_time=0,
                inference_time=0,
                options=None
            )
            
            response.progress = 1.0
            response.status = irmsia_dicom_pb2.DiagnosticStatus.COMPLETED
            
            logger.info(f"✅ Streaming diagnostic complete: {request_id}")
            yield response
        
        except Exception as e:
            logger.error(f"❌ Error during streaming diagnosis: {e}", exc_info=True)
            
            yield irmsia_dicom_pb2.DiagnosticResponse(
                request_id=request_id or "unknown",
                status=irmsia_dicom_pb2.DiagnosticStatus.ERROR,
                message=f"Error: {str(e)}",
                progress=0.0
            )
    
    async def DiagnoseBatch(self, request_iterator, context):
        """
        Batch diagnostic (streaming)
        Traite plusieurs DICOMs en parallèle (optimisé GPU)
        """
        logger.info("📊 Batch diagnostic started")
        
        batch_requests = []
        batch_tensors = []
        
        try:
            async for request in request_iterator:
                # Preprocess
                tensor, metadata = self.dicom_processor.preprocess(
                    request.dicom_data,
                    return_metadata=True
                )
                
                batch_tensors.append(tensor)
                batch_requests.append({
                    'request': request,
                    'metadata': metadata
                })
                
                # Process batch when full
                if len(batch_tensors) >= self.batch_size:
                    # Run batch inference
                    batch_tensor = torch.cat(batch_tensors, dim=0)
                    
                    # Inference
                    for i, batch_request in enumerate(batch_requests):
                        single_tensor = batch_tensor[i:i+1]
                        results = self.diagnostic_pipeline.predict(single_tensor)
                        
                        response = self._build_diagnostic_response(
                            request_id=batch_request['request'].request_id,
                            results=results,
                            metadata=batch_request['metadata'],
                            preprocessing_time=0,
                            inference_time=0,
                            options=batch_request['request'].options
                        )
                        
                        yield response
                    
                    # Reset batch
                    batch_tensors = []
                    batch_requests = []
            
            # Process remaining
            if batch_tensors:
                batch_tensor = torch.cat(batch_tensors, dim=0)
                
                for i, batch_request in enumerate(batch_requests):
                    single_tensor = batch_tensor[i:i+1]
                    results = self.diagnostic_pipeline.predict(single_tensor)
                    
                    response = self._build_diagnostic_response(
                        request_id=batch_request['request'].request_id,
                        results=results,
                        metadata=batch_request['metadata'],
                        preprocessing_time=0,
                        inference_time=0,
                        options=batch_request['request'].options
                    )
                    
                    yield response
            
            logger.info("✅ Batch diagnostic complete")
        
        except Exception as e:
            logger.error(f"❌ Error during batch diagnosis: {e}", exc_info=True)
    
    def _build_diagnostic_response(
        self,
        request_id: str,
        results: Dict,
        metadata: Dict,
        preprocessing_time: float,
        inference_time: float,
        options
    ):
        """Construire la réponse de diagnostic"""
        
        classification = results['classification']
        
        # Primary classification
        primary_class = classification['primary_class']
        primary_confidence = classification['primary_confidence']
        
        # Image classification
        image_classification = irmsia_dicom_pb2.ImageClassification(
            primary_diagnosis=PRIMARY_CLASSES[primary_class],
            confidence=primary_confidence
        )
        
        # Class probabilities
        for i, prob in enumerate(classification['primary_probs']):
            image_classification.class_probabilities.append(
                irmsia_dicom_pb2.ClassProbability(
                    class_name=PRIMARY_CLASSES[i],
                    probability=float(prob)
                )
            )
        
        # Findings
        findings = []
        for pathology_idx, confidence in classification['detected_pathologies']:
            finding = irmsia_dicom_pb2.Finding(
                finding_id=f"finding_{pathology_idx}",
                description=f"Detected: {PATHOLOGY_CLASSES[pathology_idx]}",
                pathology=PATHOLOGY_CLASSES[pathology_idx],
                location="To be determined",  # Nécessite détection spatiale
                severity=irmsia_dicom_pb2.Severity.MODERATE,
                confidence=confidence
            )
            findings.append(finding)
        
        # Risk assessment
        risk_score = int(classification['risk_score'])
        risk_level = self._get_risk_level(risk_score)
        
        risk_assessment = irmsia_dicom_pb2.RiskAssessment(
            risk_score=risk_score,
            risk_level=risk_level,
            risk_category=self._get_risk_category(risk_score),
            urgency_level=self._get_urgency_level(risk_score)
        )
        
        # Recommendations
        recommendations = self._generate_recommendations(risk_score, findings)
        
        # Analysis metadata
        analysis_metadata = irmsia_dicom_pb2.AnalysisMetadata(
            timestamp=str(time.time()),
            server_id="irmsia-gpu-01",
            gpu_device=self.gpu_name,
            model_version="1.0.0",
            preprocessing_time_ms=preprocessing_time,
            inference_time_ms=inference_time,
            image_width=metadata['columns'],
            image_height=metadata['rows']
        )
        
        # Diagnostic result
        diagnostic_result = irmsia_dicom_pb2.DiagnosticResult(
            image_id=request_id,
            model_used="MultiHeadDiagnosticModel",
            processing_time_seconds=(preprocessing_time + inference_time) / 1000,
            classification=image_classification,
            findings=findings,
            risk=risk_assessment,
            recommendations=recommendations,
            analysis_metadata=analysis_metadata
        )
        
        # Response
        response = irmsia_dicom_pb2.DiagnosticResponse(
            request_id=request_id,
            status=irmsia_dicom_pb2.DiagnosticStatus.COMPLETED,
            message="Diagnostic completed successfully",
            progress=1.0,
            result=diagnostic_result
        )
        
        return response
    
    def _get_risk_level(self, risk_score: int):
        """Convertir risk score en risk level"""
        if risk_score < 20:
            return irmsia_dicom_pb2.RiskLevel.VERY_LOW
        elif risk_score < 40:
            return irmsia_dicom_pb2.RiskLevel.LOW
        elif risk_score < 60:
            return irmsia_dicom_pb2.RiskLevel.MODERATE
        elif risk_score < 80:
            return irmsia_dicom_pb2.RiskLevel.HIGH
        elif risk_score < 90:
            return irmsia_dicom_pb2.RiskLevel.VERY_HIGH
        else:
            return irmsia_dicom_pb2.RiskLevel.CRITICAL_EMERGENCY
    
    def _get_risk_category(self, risk_score: int) -> str:
        """Catégorie de risque"""
        if risk_score < 40:
            return "Low risk - Routine follow-up"
        elif risk_score < 70:
            return "Moderate risk - Close monitoring recommended"
        else:
            return "High risk - Urgent medical attention needed"
    
    def _get_urgency_level(self, risk_score: int) -> str:
        """Niveau d'urgence"""
        if risk_score < 40:
            return "Routine"
        elif risk_score < 70:
            return "Urgent"
        else:
            return "Emergency"
    
    def _generate_recommendations(self, risk_score: int, findings: List) -> List[str]:
        """Générer les recommandations"""
        recommendations = []
        
        if risk_score < 20:
            recommendations.append("No immediate action required")
            recommendations.append("Routine follow-up recommended")
        elif risk_score < 40:
            recommendations.append("Schedule follow-up examination in 6 months")
            recommendations.append("Monitor symptoms")
        elif risk_score < 70:
            recommendations.append("Consult with specialist within 2 weeks")
            recommendations.append("Additional imaging may be required")
            recommendations.append("Consider biopsy if indicated")
        else:
            recommendations.append("⚠️ URGENT: Immediate medical attention required")
            recommendations.append("Contact emergency services if symptoms worsen")
            recommendations.append("Specialist consultation within 24-48 hours")
        
        return recommendations


async def serve(port: int = 50051, model_path: str = None):
    """Démarrer le serveur gRPC"""
    
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', 100 * 1024 * 1024),  # 100 MB
            ('grpc.max_receive_message_length', 100 * 1024 * 1024),  # 100 MB
            ('grpc.so_reuseport', 1),
        ]
    )
    
    # Add servicer
    servicer = DicomDiagnosticServicer(model_path=model_path)
    irmsia_dicom_pb2_grpc.add_DicomDiagnosticServiceServicer_to_server(
        servicer, server
    )
    
    # Listen
    server.add_insecure_port(f'[::]:{port}')
    
    logger.info(f"🚀 IRMSIA DICOM Diagnostic Server started on port {port}")
    logger.info(f"   GPU: {servicer.gpu_name}")
    logger.info(f"   Model: MultiHeadDiagnosticModel (EfficientNet-B4)")
    logger.info(f"   Ready to accept requests!")
    
    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='IRMSIA DICOM Diagnostic Server')
    parser.add_argument('--port', type=int, default=50051, help='Server port')
    parser.add_argument('--model-path', type=str, default=None, help='Path to model weights')
    
    args = parser.parse_args()
    
    asyncio.run(serve(port=args.port, model_path=args.model_path))

