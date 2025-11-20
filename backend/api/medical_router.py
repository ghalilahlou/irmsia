"""
Routes API pour l'analyse médicale
Upload DICOM, conversion PNG, analyse LLM
"""

import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Dict, Any

from backend.services.dicom_converter import dicom_converter
from backend.services.tcia_service import tcia_service
from backend.services.llm_analyzer import llm_analyzer
from backend.api.auth_router import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/medical", tags=["Medical Imaging"])


@router.post("/dicom/upload")
async def upload_dicom(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload un fichier DICOM et le convertit en PNG
    
    Body: fichier DICOM
    Returns: nom du PNG généré
    """
    try:
        # Lire le contenu du fichier
        file_content = await file.read()
        
        # Vérifier que c'est un fichier DICOM
        if not file.filename.lower().endswith(('.dcm', '.dicom')):
            raise HTTPException(
                status_code=400,
                detail="Le fichier doit être un DICOM (.dcm ou .dicom)"
            )
        
        # Sauvegarder le fichier DICOM
        dicom_path = dicom_converter.save_uploaded_dicom(file_content, file.filename)
        
        # Convertir en PNG
        try:
            png_filename, png_path = dicom_converter.convert_to_png(dicom_path)
            
            return JSONResponse({
                "status": "success",
                "message": "Fichier DICOM uploadé et converti avec succès",
                "dicom_filename": file.filename,
                "png_filename": png_filename,
                "png_path": str(png_path)
            })
            
        except ValueError as e:
            # Erreur de conversion
            raise HTTPException(
                status_code=400,
                detail=f"Erreur de conversion DICOM → PNG: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'upload DICOM: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur serveur: {str(e)}"
        )


@router.get("/dicom/list")
async def list_dicom_files(
    current_user: dict = Depends(get_current_user)
):
    """
    Liste tous les fichiers DICOM disponibles
    """
    try:
        dicom_files = dicom_converter.list_dicom_files()
        
        return JSONResponse({
            "status": "success",
            "count": len(dicom_files),
            "files": dicom_files
        })
        
    except Exception as e:
        logger.error(f"Erreur lors du listing DICOM: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur serveur: {str(e)}"
        )


@router.get("/png/list")
async def list_png_files(
    current_user: dict = Depends(get_current_user)
):
    """
    Liste tous les fichiers PNG disponibles
    """
    try:
        png_files = dicom_converter.list_png_files()
        
        return JSONResponse({
            "status": "success",
            "count": len(png_files),
            "files": png_files
        })
        
    except Exception as e:
        logger.error(f"Erreur lors du listing PNG: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur serveur: {str(e)}"
        )


@router.get("/dicom/import")
async def import_tcia_dicoms(
    current_user: dict = Depends(get_current_user)
):
    """
    Télécharge 10 fichiers DICOM depuis TCIA
    """
    try:
        downloaded_files = tcia_service.download_sample_dicoms(count=10)
        
        return JSONResponse({
            "status": "success",
            "message": f"{len(downloaded_files)} fichiers téléchargés depuis TCIA",
            "files": downloaded_files
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'import TCIA: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur serveur: {str(e)}"
        )


@router.post("/analyze")
async def analyze_image(
    request: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Analyse une image PNG avec LLM
    
    Body: { "filename": "image.png" }
    """
    try:
        filename = request.get("filename")
        if not filename:
            raise HTTPException(
                status_code=400,
                detail="Le champ 'filename' est requis"
            )
        
        # Trouver le fichier PNG
        png_dir = Path(dicom_converter.png_dir)
        image_path = png_dir / filename
        
        if not image_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Image non trouvée: {filename}"
            )
        
        # Analyser l'image
        analysis_result = llm_analyzer.analyze_image(image_path)
        
        return JSONResponse(analysis_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur serveur: {str(e)}"
        )


@router.get("/dicom/{filename}")
async def get_dicom_file(
    filename: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère un fichier DICOM
    """
    try:
        dicom_dir = Path(dicom_converter.dicom_dir)
        dicom_path = dicom_dir / filename
        
        if not dicom_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Fichier DICOM non trouvé: {filename}"
            )
        
        return FileResponse(
            path=dicom_path,
            media_type="application/dicom",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du fichier DICOM: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur serveur: {str(e)}"
        )


@router.post("/dicom/{filename}/convert")
async def convert_dicom_file(
    filename: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Convertit un fichier DICOM existant en PNG
    """
    try:
        dicom_dir = Path(dicom_converter.dicom_dir)
        dicom_path = dicom_dir / filename
        
        if not dicom_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Fichier DICOM non trouvé: {filename}"
            )
        
        # Convertir en PNG
        png_filename, png_path = dicom_converter.convert_to_png(dicom_path)
        
        return JSONResponse({
            "status": "success",
            "message": "Fichier DICOM converti avec succès",
            "dicom_filename": filename,
            "png_filename": png_filename,
            "png_path": str(png_path)
        })
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erreur de conversion: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la conversion: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur serveur: {str(e)}"
        )


@router.get("/png/{filename}")
async def get_png_image(
    filename: str,
    # Optionnel: rendre accessible sans authentification pour les images dé-identifiées
    # current_user: dict = Depends(get_current_user)
):
    """
    Récupère une image PNG (accessible sans authentification car images dé-identifiées)
    """
    try:
        png_dir = Path(dicom_converter.png_dir)
        image_path = png_dir / filename
        
        if not image_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Image non trouvée: {filename}"
            )
        
        return FileResponse(
            path=image_path,
            media_type="image/png",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'image: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur serveur: {str(e)}"
        )


@router.delete("/png/{filename}")
async def delete_png_image(
    filename: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Supprime une image PNG
    """
    try:
        png_dir = Path(dicom_converter.png_dir)
        image_path = png_dir / filename
        
        if not image_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Image non trouvée: {filename}"
            )
        
        # Supprimer le fichier
        image_path.unlink()
        
        logger.info(f"Image PNG supprimée: {filename} par {current_user.get('username', 'unknown')}")
        
        return JSONResponse({
            "status": "success",
            "message": f"Image {filename} supprimée avec succès"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de l'image: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur serveur: {str(e)}"
        )

