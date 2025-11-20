"""
Routes blockchain
Consultation des enregistrements et logs
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List

from backend.services.blockchain_service import blockchain_service
from backend.api.auth_router import get_current_user
from backend.models.dto import BlockchainRecord, AccessLog

router = APIRouter(prefix="/blockchain", tags=["Blockchain"])

logger = logging.getLogger(__name__)


@router.get("/hash/{image_id}", response_model=BlockchainRecord)
async def get_hash_record(
    image_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Récupère l'enregistrement blockchain d'une image"""
    try:
        record = blockchain_service.get_hash_record(image_id)
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enregistrement blockchain non trouvé"
            )
        
        return record
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'enregistrement: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/access-logs/{image_id}", response_model=List[AccessLog])
async def get_access_logs(
    image_id: str,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère les logs d'accès d'une image
    
    Seuls les admins peuvent voir tous les logs
    """
    try:
        # Vérifier les permissions (simplifié)
        if current_user["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seuls les administrateurs peuvent consulter les logs d'accès"
            )
        
        logs = blockchain_service.get_access_logs(image_id, limit=limit)
        return logs
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/status")
async def blockchain_status(current_user: dict = Depends(get_current_user)):
    """Statut de la connexion blockchain"""
    return {
        "blockchain_type": blockchain_service.blockchain_type,
        "status": "connected" if blockchain_service.blockchain_type != "mock" else "mock",
        "provider": blockchain_service.blockchain_type
    }

