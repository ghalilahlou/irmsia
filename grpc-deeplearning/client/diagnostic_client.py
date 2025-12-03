"""
Client gRPC pour IRMSIA DICOM Diagnostic Service
Exemples d'utilisation pour tous les types de RPC
"""

import grpc
import asyncio
import sys
from pathlib import Path
import logging
import time
from typing import List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import generated proto files
try:
    from proto import irmsia_dicom_pb2
    from proto import irmsia_dicom_pb2_grpc
except ImportError:
    print("⚠️  Proto files not generated. Run:")
    print("   python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/irmsia_dicom.proto")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DicomDiagnosticClient:
    """
    Client pour le service de diagnostic DICOM
    """
    
    def __init__(self, host: str = 'localhost', port: int = 50051):
        self.address = f'{host}:{port}'
        self.channel = grpc.aio.insecure_channel(
            self.address,
            options=[
                ('grpc.max_send_message_length', 100 * 1024 * 1024),
                ('grpc.max_receive_message_length', 100 * 1024 * 1024),
            ]
        )
        self.stub = irmsia_dicom_pb2_grpc.DicomDiagnosticServiceStub(self.channel)
        
        logger.info(f"Client initialized: {self.address}")
    
    async def health_check(self):
        """Vérifier la santé du service"""
        logger.info("Checking service health...")
        
        try:
            response = await self.stub.HealthCheck(irmsia_dicom_pb2.Empty())
            
            logger.info(f"✅ Service is healthy")
            logger.info(f"   GPU: {response.gpu_status}")
            logger.info(f"   GPU Memory: {response.gpu_memory_used_mb}/{response.gpu_memory_total_mb} MB")
            logger.info(f"   Model: {response.model_loaded}")
            logger.info(f"   Uptime: {response.uptime_seconds:.1f}s")
            
            return response
        
        except grpc.RpcError as e:
            logger.error(f"❌ Health check failed: {e.code()} - {e.details()}")
            return None
    
    async def get_available_models(self):
        """Lister les modèles disponibles"""
        logger.info("Getting available models...")
        
        try:
            response = await self.stub.GetAvailableModels(irmsia_dicom_pb2.Empty())
            
            logger.info(f"✅ Available models: {len(response.models)}")
            for model in response.models:
                logger.info(f"   - {model.model_name} (v{model.version})")
                logger.info(f"     Modality: {model.modality}")
                logger.info(f"     Accuracy: {model.accuracy*100:.1f}%")
                logger.info(f"     Pathologies: {len(model.pathologies)}")
            
            return response
        
        except grpc.RpcError as e:
            logger.error(f"❌ Failed to get models: {e.code()} - {e.details()}")
            return None
    
    async def diagnose_dicom(
        self,
        dicom_path: str,
        request_id: Optional[str] = None,
        confidence_threshold: float = 0.5,
        include_segmentation: bool = False,
        include_gradcam: bool = False
    ):
        """
        Diagnostic simple (unary RPC)
        
        Args:
            dicom_path: Path to DICOM file
            request_id: Request ID (or auto-generate)
            confidence_threshold: Confidence threshold
            include_segmentation: Include segmentation masks
            include_gradcam: Include Grad-CAM heatmap
        
        Returns:
            DiagnosticResponse
        """
        if request_id is None:
            import uuid
            request_id = str(uuid.uuid4())
        
        logger.info(f"📊 Diagnosing DICOM: {dicom_path}")
        logger.info(f"   Request ID: {request_id}")
        
        # Read DICOM file
        with open(dicom_path, 'rb') as f:
            dicom_data = f.read()
        
        logger.info(f"   File size: {len(dicom_data)/1024/1024:.1f} MB")
        
        # Prepare request
        options = irmsia_dicom_pb2.DiagnosticOptions(
            model_preference="auto",
            confidence_threshold=confidence_threshold,
            include_segmentation=include_segmentation,
            include_gradcam=include_gradcam,
            fast_mode=False
        )
        
        request = irmsia_dicom_pb2.DicomRequest(
            request_id=request_id,
            dicom_data=dicom_data,
            options=options
        )
        
        # Send request
        try:
            start_time = time.time()
            response = await self.stub.DiagnoseDicom(request)
            elapsed_time = time.time() - start_time
            
            # Display results
            self._display_results(response, elapsed_time)
            
            return response
        
        except grpc.RpcError as e:
            logger.error(f"❌ Diagnosis failed: {e.code()} - {e.details()}")
            return None
    
    async def diagnose_dicom_stream(
        self,
        dicom_path: str,
        request_id: Optional[str] = None,
        chunk_size: int = 4 * 1024 * 1024  # 4 MB chunks
    ):
        """
        Diagnostic avec streaming bidirectionnel
        Upload par chunks + updates en temps réel
        
        Args:
            dicom_path: Path to DICOM file
            request_id: Request ID
            chunk_size: Chunk size in bytes
        
        Returns:
            Final DiagnosticResponse
        """
        if request_id is None:
            import uuid
            request_id = str(uuid.uuid4())
        
        logger.info(f"📊 Streaming diagnosis: {dicom_path}")
        logger.info(f"   Request ID: {request_id}")
        
        # Read DICOM file
        with open(dicom_path, 'rb') as f:
            dicom_data = f.read()
        
        total_size = len(dicom_data)
        num_chunks = (total_size + chunk_size - 1) // chunk_size
        
        logger.info(f"   File size: {total_size/1024/1024:.1f} MB")
        logger.info(f"   Chunks: {num_chunks}")
        
        async def request_generator():
            """Générer les requêtes de streaming"""
            # Premier message : métadonnées
            metadata = irmsia_dicom_pb2.DicomMetadata(
                patient_id="PSEUDO-12345",
                modality="MRI",
                body_part="Brain"
            )
            
            yield irmsia_dicom_pb2.DicomUploadRequest(
                request_id=request_id,
                metadata=metadata
            )
            
            # Messages suivants : chunks
            for i in range(num_chunks):
                start = i * chunk_size
                end = min(start + chunk_size, total_size)
                chunk = dicom_data[start:end]
                
                yield irmsia_dicom_pb2.DicomUploadRequest(
                    request_id=request_id,
                    chunk=chunk
                )
                
                logger.debug(f"   Sent chunk {i+1}/{num_chunks}")
        
        # Stream request and receive updates
        try:
            start_time = time.time()
            
            async for response in self.stub.DiagnoseDicomStream(request_generator()):
                # Display progress
                if response.status == irmsia_dicom_pb2.DiagnosticStatus.PROCESSING:
                    logger.info(f"   📊 {response.message} ({response.progress*100:.0f}%)")
                
                elif response.status == irmsia_dicom_pb2.DiagnosticStatus.COMPLETED:
                    elapsed_time = time.time() - start_time
                    logger.info(f"   ✅ Diagnosis complete!")
                    
                    # Display results
                    self._display_results(response, elapsed_time)
                    
                    return response
                
                elif response.status == irmsia_dicom_pb2.DiagnosticStatus.ERROR:
                    logger.error(f"   ❌ Error: {response.message}")
                    return None
        
        except grpc.RpcError as e:
            logger.error(f"❌ Streaming diagnosis failed: {e.code()} - {e.details()}")
            return None
    
    async def diagnose_batch(
        self,
        dicom_paths: List[str],
        confidence_threshold: float = 0.5
    ):
        """
        Batch diagnosis (streaming)
        Optimisé pour GPU avec traitement parallèle
        
        Args:
            dicom_paths: List of DICOM file paths
            confidence_threshold: Confidence threshold
        
        Returns:
            List of DiagnosticResponse
        """
        logger.info(f"📊 Batch diagnosis: {len(dicom_paths)} files")
        
        async def request_generator():
            """Générer les requêtes batch"""
            for i, dicom_path in enumerate(dicom_paths):
                import uuid
                request_id = str(uuid.uuid4())
                
                # Read DICOM
                with open(dicom_path, 'rb') as f:
                    dicom_data = f.read()
                
                # Metadata
                metadata = irmsia_dicom_pb2.DicomMetadata(
                    patient_id=f"PSEUDO-{i}",
                    modality="MRI",
                    body_part="Brain"
                )
                
                # Options
                options = irmsia_dicom_pb2.DiagnosticOptions(
                    confidence_threshold=confidence_threshold,
                    fast_mode=True  # Fast mode for batch
                )
                
                # Request
                yield irmsia_dicom_pb2.DicomRequest(
                    request_id=request_id,
                    dicom_data=dicom_data,
                    metadata=metadata,
                    options=options
                )
                
                logger.info(f"   Sent request {i+1}/{len(dicom_paths)}")
        
        # Stream requests and receive responses
        try:
            start_time = time.time()
            results = []
            
            async for response in self.stub.DiagnoseBatch(request_generator()):
                logger.info(f"   ✅ Result {len(results)+1}: {response.request_id}")
                logger.info(f"      Risk Score: {response.result.risk.risk_score}/100")
                logger.info(f"      Primary: {response.result.classification.primary_diagnosis}")
                
                results.append(response)
            
            elapsed_time = time.time() - start_time
            throughput = len(results) / elapsed_time
            
            logger.info(f"\n🎉 Batch complete!")
            logger.info(f"   Total time: {elapsed_time:.2f}s")
            logger.info(f"   Throughput: {throughput:.2f} images/sec")
            
            return results
        
        except grpc.RpcError as e:
            logger.error(f"❌ Batch diagnosis failed: {e.code()} - {e.details()}")
            return []
    
    def _display_results(self, response, elapsed_time):
        """Afficher les résultats de diagnostic"""
        result = response.result
        
        logger.info(f"\n{'='*60}")
        logger.info(f"DIAGNOSTIC RESULTS")
        logger.info(f"{'='*60}")
        logger.info(f"Request ID: {response.request_id}")
        logger.info(f"Processing Time: {elapsed_time:.2f}s")
        logger.info(f"Model: {result.model_used}")
        
        # Classification
        logger.info(f"\n📊 CLASSIFICATION:")
        logger.info(f"   Primary Diagnosis: {result.classification.primary_diagnosis}")
        logger.info(f"   Confidence: {result.classification.confidence*100:.1f}%")
        
        logger.info(f"\n   Class Probabilities:")
        for prob in result.classification.class_probabilities:
            logger.info(f"      {prob.class_name}: {prob.probability*100:.1f}%")
        
        # Findings
        if result.findings:
            logger.info(f"\n🔍 FINDINGS ({len(result.findings)}):")
            for i, finding in enumerate(result.findings, 1):
                logger.info(f"   {i}. {finding.pathology}")
                logger.info(f"      Description: {finding.description}")
                logger.info(f"      Location: {finding.location}")
                logger.info(f"      Severity: {finding.severity}")
                logger.info(f"      Confidence: {finding.confidence*100:.1f}%")
        else:
            logger.info(f"\n🔍 FINDINGS: None detected")
        
        # Risk Assessment
        logger.info(f"\n⚠️  RISK ASSESSMENT:")
        logger.info(f"   Risk Score: {result.risk.risk_score}/100")
        logger.info(f"   Risk Level: {result.risk.risk_level}")
        logger.info(f"   Category: {result.risk.risk_category}")
        logger.info(f"   Urgency: {result.risk.urgency_level}")
        
        # Recommendations
        if result.recommendations:
            logger.info(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(result.recommendations, 1):
                logger.info(f"   {i}. {rec}")
        
        logger.info(f"{'='*60}\n")
    
    async def close(self):
        """Fermer la connexion"""
        await self.channel.close()
        logger.info("Connection closed")


# ============================================
# Exemples d'utilisation
# ============================================

async def example_health_check():
    """Exemple: Health check"""
    client = DicomDiagnosticClient()
    
    await client.health_check()
    await client.get_available_models()
    
    await client.close()


async def example_simple_diagnosis(dicom_path: str):
    """Exemple: Diagnostic simple"""
    client = DicomDiagnosticClient()
    
    # Health check
    await client.health_check()
    
    # Diagnose
    response = await client.diagnose_dicom(
        dicom_path=dicom_path,
        confidence_threshold=0.5,
        include_segmentation=False,
        include_gradcam=False
    )
    
    await client.close()
    
    return response


async def example_streaming_diagnosis(dicom_path: str):
    """Exemple: Diagnostic streaming (pour gros fichiers)"""
    client = DicomDiagnosticClient()
    
    # Diagnose with streaming
    response = await client.diagnose_dicom_stream(
        dicom_path=dicom_path,
        chunk_size=4 * 1024 * 1024  # 4 MB chunks
    )
    
    await client.close()
    
    return response


async def example_batch_diagnosis(dicom_paths: List[str]):
    """Exemple: Batch diagnosis (optimisé GPU)"""
    client = DicomDiagnosticClient()
    
    # Batch diagnose
    results = await client.diagnose_batch(
        dicom_paths=dicom_paths,
        confidence_threshold=0.5
    )
    
    await client.close()
    
    return results


async def main():
    """Main function - Examples"""
    import argparse
    
    parser = argparse.ArgumentParser(description='IRMSIA DICOM Diagnostic Client')
    parser.add_argument('--host', type=str, default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=50051, help='Server port')
    parser.add_argument('--dicom', type=str, help='DICOM file path')
    parser.add_argument('--batch', nargs='+', help='Batch of DICOM files')
    parser.add_argument('--streaming', action='store_true', help='Use streaming mode')
    parser.add_argument('--health', action='store_true', help='Health check only')
    
    args = parser.parse_args()
    
    # Create client
    client = DicomDiagnosticClient(host=args.host, port=args.port)
    
    try:
        if args.health:
            # Health check
            await client.health_check()
            await client.get_available_models()
        
        elif args.dicom:
            if args.streaming:
                # Streaming diagnosis
                await client.diagnose_dicom_stream(args.dicom)
            else:
                # Simple diagnosis
                await client.diagnose_dicom(args.dicom)
        
        elif args.batch:
            # Batch diagnosis
            await client.diagnose_batch(args.batch)
        
        else:
            print("Please specify --health, --dicom, or --batch")
            parser.print_help()
    
    finally:
        await client.close()


if __name__ == '__main__':
    asyncio.run(main())

