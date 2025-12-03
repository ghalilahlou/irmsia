# 🔌 Guide d'Intégration avec Backend IRMSIA

## Vue d'Ensemble

Ce guide explique comment intégrer le serveur gRPC Deep Learning avec le backend FastAPI existant d'IRMSIA.

---

## Architecture d'Intégration

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌─────────────────────────────────────────────────────────────┐
│             Backend FastAPI (Port 8000)                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  API Routes                                          │   │
│  │  - /api/v1/dicom/upload                             │   │
│  │  - /api/v1/dicom/diagnose                           │   │
│  │  - /api/v1/dicom/batch                              │   │
│  └────────────────────┬────────────────────────────────┘   │
│                       │ gRPC (internal)                     │
│                       ▼                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  gRPC Client                                         │   │
│  │  - DicomDiagnosticClient                            │   │
│  └────────────────────┬────────────────────────────────┘   │
└───────────────────────┼──────────────────────────────────────┘
                        │ gRPC (localhost:50051)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│             gRPC Server (Port 50051)                         │
│  - Deep Learning Service                                    │
│  - GPU Inference                                            │
│  - Batch Processing                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Étape 1 : Copier les Fichiers Nécessaires

### 1.1 Copier le Client gRPC

```bash
# Copier le client dans le backend IRMSIA
cp -r grpc-deeplearning/client ../backend/services/grpc_client
cp -r grpc-deeplearning/proto ../backend/services/grpc_client/
```

### 1.2 Ajouter les Dépendances

Ajouter dans `backend/requirements.txt` :

```txt
# gRPC
grpcio==1.60.0
grpcio-tools==1.60.0
protobuf==4.25.1
```

---

## Étape 2 : Créer le Service gRPC dans FastAPI

### 2.1 Créer `backend/services/grpc_diagnostic_service.py`

```python
"""
Service gRPC pour le diagnostic DICOM
Interface entre FastAPI et le serveur gRPC DL
"""

import logging
from typing import Optional, List, Dict
from pathlib import Path
import asyncio

# Import du client gRPC
from .grpc_client.client.diagnostic_client import DicomDiagnosticClient

logger = logging.getLogger(__name__)


class GRPCDiagnosticService:
    """
    Singleton service pour communiquer avec le serveur gRPC DL
    """
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialiser le client gRPC"""
        try:
            # Configuration depuis les variables d'environnement
            grpc_host = os.getenv('GRPC_DL_HOST', 'localhost')
            grpc_port = int(os.getenv('GRPC_DL_PORT', '50051'))
            
            self._client = DicomDiagnosticClient(host=grpc_host, port=grpc_port)
            
            logger.info(f"✅ gRPC Client initialized: {grpc_host}:{grpc_port}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize gRPC client: {e}")
            self._client = None
    
    async def health_check(self) -> Dict:
        """Vérifier la santé du service DL"""
        if not self._client:
            return {"status": "error", "message": "Client not initialized"}
        
        try:
            response = await self._client.health_check()
            
            return {
                "status": "healthy" if response.is_healthy else "unhealthy",
                "gpu": response.gpu_status,
                "gpu_memory_used": response.gpu_memory_used_mb,
                "gpu_memory_total": response.gpu_memory_total_mb,
                "model": response.model_loaded,
                "uptime": response.uptime_seconds
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def diagnose_dicom(
        self,
        dicom_path: str,
        confidence_threshold: float = 0.5,
        include_segmentation: bool = False,
        include_gradcam: bool = False
    ) -> Optional[Dict]:
        """
        Diagnostiquer un fichier DICOM
        
        Args:
            dicom_path: Path to DICOM file
            confidence_threshold: Confidence threshold
            include_segmentation: Include segmentation
            include_gradcam: Include Grad-CAM
        
        Returns:
            Dict with diagnostic results or None if error
        """
        if not self._client:
            logger.error("gRPC client not initialized")
            return None
        
        try:
            logger.info(f"Diagnosing DICOM: {dicom_path}")
            
            response = await self._client.diagnose_dicom(
                dicom_path=dicom_path,
                confidence_threshold=confidence_threshold,
                include_segmentation=include_segmentation,
                include_gradcam=include_gradcam
            )
            
            if not response:
                return None
            
            # Convert protobuf response to dict
            result = self._convert_response_to_dict(response)
            
            return result
        
        except Exception as e:
            logger.error(f"Diagnosis failed: {e}")
            return None
    
    async def diagnose_batch(
        self,
        dicom_paths: List[str],
        confidence_threshold: float = 0.5
    ) -> List[Dict]:
        """
        Diagnostiquer un batch de fichiers DICOM
        
        Args:
            dicom_paths: List of DICOM file paths
            confidence_threshold: Confidence threshold
        
        Returns:
            List of diagnostic results
        """
        if not self._client:
            logger.error("gRPC client not initialized")
            return []
        
        try:
            logger.info(f"Batch diagnosis: {len(dicom_paths)} files")
            
            responses = await self._client.diagnose_batch(
                dicom_paths=dicom_paths,
                confidence_threshold=confidence_threshold
            )
            
            results = [
                self._convert_response_to_dict(response)
                for response in responses
            ]
            
            return results
        
        except Exception as e:
            logger.error(f"Batch diagnosis failed: {e}")
            return []
    
    def _convert_response_to_dict(self, response) -> Dict:
        """Convertir la réponse protobuf en dict"""
        result = response.result
        
        return {
            "request_id": response.request_id,
            "status": response.status,
            "model_used": result.model_used,
            "processing_time": result.processing_time_seconds,
            
            # Classification
            "classification": {
                "primary_diagnosis": result.classification.primary_diagnosis,
                "confidence": result.classification.confidence,
                "probabilities": {
                    prob.class_name: prob.probability
                    for prob in result.classification.class_probabilities
                }
            },
            
            # Findings
            "findings": [
                {
                    "finding_id": f.finding_id,
                    "pathology": f.pathology,
                    "description": f.description,
                    "location": f.location,
                    "severity": f.severity,
                    "confidence": f.confidence
                }
                for f in result.findings
            ],
            
            # Risk
            "risk": {
                "score": result.risk.risk_score,
                "level": result.risk.risk_level,
                "category": result.risk.risk_category,
                "urgency": result.risk.urgency_level
            },
            
            # Recommendations
            "recommendations": list(result.recommendations)
        }


# Singleton instance
grpc_diagnostic_service = GRPCDiagnosticService()
```

---

## Étape 3 : Créer les Routes FastAPI

### 3.1 Créer `backend/api/ai_router_grpc.py`

```python
"""
Router FastAPI pour l'analyse IA via gRPC
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import logging
import os
import uuid
from pathlib import Path

from backend.services.grpc_diagnostic_service import grpc_diagnostic_service
from backend.core.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-grpc", tags=["AI gRPC"])


class DiagnosisRequest(BaseModel):
    """Request pour diagnostic"""
    image_id: str
    confidence_threshold: Optional[float] = 0.5
    include_segmentation: Optional[bool] = False
    include_gradcam: Optional[bool] = False


@router.get("/health")
async def health_check():
    """Health check du service gRPC DL"""
    health = await grpc_diagnostic_service.health_check()
    
    return JSONResponse(content=health)


@router.post("/diagnose")
async def diagnose_dicom(
    file: UploadFile = File(...),
    confidence_threshold: float = 0.5,
    include_segmentation: bool = False,
    include_gradcam: bool = False,
    current_user = Depends(get_current_user)
):
    """
    Diagnostiquer un fichier DICOM
    """
    logger.info(f"User {current_user['username']} requested diagnosis")
    
    # Save uploaded file temporarily
    temp_dir = Path("storage/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    file_id = str(uuid.uuid4())
    temp_path = temp_dir / f"{file_id}.dcm"
    
    try:
        # Save file
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Saved temp file: {temp_path} ({len(content)/1024/1024:.1f} MB)")
        
        # Diagnose via gRPC
        result = await grpc_diagnostic_service.diagnose_dicom(
            dicom_path=str(temp_path),
            confidence_threshold=confidence_threshold,
            include_segmentation=include_segmentation,
            include_gradcam=include_gradcam
        )
        
        if result is None:
            raise HTTPException(status_code=500, detail="Diagnosis failed")
        
        return JSONResponse(content={
            "status": "success",
            "data": result
        })
    
    except Exception as e:
        logger.error(f"Error during diagnosis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up temp file
        if temp_path.exists():
            os.remove(temp_path)


@router.post("/diagnose-batch")
async def diagnose_batch(
    files: List[UploadFile] = File(...),
    confidence_threshold: float = 0.5,
    current_user = Depends(get_current_user)
):
    """
    Diagnostiquer un batch de fichiers DICOM
    """
    logger.info(f"User {current_user['username']} requested batch diagnosis ({len(files)} files)")
    
    temp_dir = Path("storage/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    temp_paths = []
    
    try:
        # Save all files
        for file in files:
            file_id = str(uuid.uuid4())
            temp_path = temp_dir / f"{file_id}.dcm"
            
            with open(temp_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            temp_paths.append(str(temp_path))
        
        logger.info(f"Saved {len(temp_paths)} temp files")
        
        # Diagnose batch via gRPC
        results = await grpc_diagnostic_service.diagnose_batch(
            dicom_paths=temp_paths,
            confidence_threshold=confidence_threshold
        )
        
        return JSONResponse(content={
            "status": "success",
            "count": len(results),
            "data": results
        })
    
    except Exception as e:
        logger.error(f"Error during batch diagnosis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up temp files
        for temp_path in temp_paths:
            if Path(temp_path).exists():
                os.remove(temp_path)
```

---

## Étape 4 : Intégrer dans main.py

### 4.1 Modifier `backend/main.py`

```python
# Ajouter l'import
from backend.api.ai_router_grpc import router as ai_grpc_router

# Inclure le router
app.include_router(ai_grpc_router, prefix="/api/v1")
```

---

## Étape 5 : Configuration

### 5.1 Ajouter dans `.env`

```env
# gRPC Deep Learning Service
GRPC_DL_HOST=localhost
GRPC_DL_PORT=50051
```

---

## Étape 6 : Démarrage

### 6.1 Démarrer les Deux Services

**Terminal 1 - gRPC Server:**
```bash
cd grpc-deeplearning
python server/diagnostic_server.py --port 50051
```

**Terminal 2 - FastAPI Backend:**
```bash
cd backend
python main.py
```

---

## Étape 7 : Tester

### 7.1 Health Check

```bash
curl http://localhost:8000/api/v1/ai-grpc/health
```

### 7.2 Diagnostic

```bash
curl -X POST http://localhost:8000/api/v1/ai-grpc/diagnose \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@scan.dcm" \
  -F "confidence_threshold=0.7"
```

---

## Production Deployment

### Docker Compose

```yaml
version: '3.8'

services:
  # Backend FastAPI
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GRPC_DL_HOST=grpc-server
      - GRPC_DL_PORT=50051
    depends_on:
      - grpc-server
  
  # gRPC Deep Learning Server
  grpc-server:
    build: ./grpc-deeplearning
    ports:
      - "50051:50051"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    command: python server/diagnostic_server.py --port 50051
```

---

## Monitoring

### Prometheus Metrics (à implémenter)

```python
# Ajouter des métriques
from prometheus_client import Counter, Histogram

diagnosis_counter = Counter('diagnosis_total', 'Total diagnoses')
diagnosis_duration = Histogram('diagnosis_duration_seconds', 'Diagnosis duration')

@diagnosis_duration.time()
async def diagnose_dicom(...):
    diagnosis_counter.inc()
    # ...
```

---

## Troubleshooting

### Problème: Connection refused

**Solution:** Vérifier que le serveur gRPC est lancé
```bash
python client/diagnostic_client.py --health
```

### Problème: Timeout

**Solution:** Augmenter le timeout
```python
self.channel = grpc.aio.insecure_channel(
    self.address,
    options=[
        ('grpc.max_send_message_length', 100 * 1024 * 1024),
        ('grpc.max_receive_message_length', 100 * 1024 * 1024),
        ('grpc.keepalive_time_ms', 10000),  # Add
        ('grpc.keepalive_timeout_ms', 5000),  # Add
    ]
)
```

---

**🎉 Intégration complète ! Votre backend IRMSIA communique maintenant avec le serveur gRPC Deep Learning pour des performances optimales !**

