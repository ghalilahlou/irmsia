"""
Routes DICOM
Upload, traitement, conversion
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from backend.services.dicom_service import dicom_service
from backend.services.blockchain_service import blockchain_service
# from backend.services.storage_service import storage_service  # Pour utilisation future
from backend.api.auth_router import get_current_user
from backend.models.dto import DICOMUploadResponse, DICOMMetadata

router = APIRouter(prefix="/dicom", tags=["DICOM"])

logger = logging.getLogger(__name__)


@router.post("/upload", response_model=DICOMUploadResponse)
async def upload_dicom(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload un fichier DICOM
    
    Processus:
    1. Upload du fichier DICOM
    2. Dé-identification des métadonnées
    3. Conversion en PNG
    4. Chiffrement AES-256
    5. Enregistrement du hash sur la blockchain
    6. Stockage (local ou S3)
    """
    try:
        # Vérifier le type de fichier
        if not file.filename.endswith(('.dcm', '.dicom')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le fichier doit être un fichier DICOM (.dcm ou .dicom)"
            )
        
        # Lire le contenu du fichier
        file_content = await file.read()
        
        # Vérifier la taille
        if len(file_content) > 100 * 1024 * 1024:  # 100MB
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Le fichier est trop volumineux (max 100MB)"
            )
        
        # Traiter le fichier DICOM
        image_id, metadata = dicom_service.upload_dicom(file_content, file.filename)
        
        # Enregistrer le hash sur la blockchain
        blockchain_record = blockchain_service.register_hash(
            image_id=image_id,
            file_hash=metadata["hash"],
            metadata=metadata["metadata"]
        )
        
        # Log d'accès (upload)
        blockchain_service.log_access(
            image_id=image_id,
            user_id=current_user["username"],
            action="upload"
        )
        
        return DICOMUploadResponse(
            image_id=image_id,
            message="Fichier DICOM traité avec succès",
            deidentified=True,
            converted=True,
            encrypted=True,
            hash_registered=blockchain_record.transaction_id is not None,
            timestamp=blockchain_record.timestamp
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'upload DICOM: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du traitement du fichier DICOM: {str(e)}"
        )


@router.get("/{image_id}/metadata")
async def get_metadata(
    image_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Récupère les métadonnées (dé-identifiées) d'une image"""
    try:
        # Récupérer l'enregistrement blockchain
        record = blockchain_service.get_hash_record(image_id)
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image non trouvée"
            )
        
        # Log d'accès
        blockchain_service.log_access(
            image_id=image_id,
            user_id=current_user["username"],
            action="view_metadata"
        )
        
        # Retourner les métadonnées (déjà dé-identifiées)
        return {
            "image_id": image_id,
            "metadata": record.metadata if hasattr(record, 'metadata') else {},
            "hash": record.hash,
            "timestamp": record.timestamp
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métadonnées: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

