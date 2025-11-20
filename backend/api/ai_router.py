"""
Routes d'analyse IA
Analyse d'images médicales avec vision + LLM
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, status
from pathlib import Path

from backend.services.ai_service import ai_service
from backend.services.dicom_service import dicom_service
from backend.services.blockchain_service import blockchain_service
from backend.api.auth_router import get_current_user
from backend.models.dto import AIAnalysisRequest, AIAnalysisResponse

router = APIRouter(prefix="/ai", tags=["AI Analysis"])

logger = logging.getLogger(__name__)


@router.post("/analyze/{image_id}", response_model=AIAnalysisResponse)
async def analyze_image(
    image_id: str,
    request: AIAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyse une image médicale avec IA
    
    Processus:
    1. Vérification de l'existence de l'image
    2. Déchiffrement temporaire de l'image
    3. Analyse avec modèle vision + LLM
    4. Log d'accès sur la blockchain
    5. Nettoyage du fichier temporaire
    """
    try:
        # Vérifier que l'image_id correspond
        if request.image_id != image_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'image_id dans l'URL ne correspond pas à celui dans le body"
            )
        
        # Déchiffrer temporairement l'image
        decrypted_path = dicom_service.get_decrypted_image_path(image_id)
        
        if not decrypted_path or not decrypted_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image non trouvée ou impossible à déchiffrer"
            )
        
        try:
            # Analyser l'image
            analysis_result = ai_service.analyze_image(
                image_path=str(decrypted_path),
                modality=request.modality or "MRI",
                additional_context=request.additional_context
            )
            
            # Mettre à jour l'image_id dans le résultat
            analysis_result.image_id = image_id
            
            # Log d'accès sur la blockchain
            blockchain_service.log_access(
                image_id=image_id,
                user_id=current_user["username"],
                action="analyze"
            )
            
            return analysis_result
            
        finally:
            # Nettoyer le fichier temporaire
            dicom_service.cleanup_temp_file(image_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse IA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'analyse: {str(e)}"
        )


@router.get("/models")
async def list_models(current_user: dict = Depends(get_current_user)):
    """Liste les modèles IA disponibles"""
    return {
        "current_provider": ai_service.provider,
        "available_providers": ["mock", "huggingface", "openai"],
        "current_model": ai_service.model.__class__.__name__ if ai_service.model else "mock"
    }

