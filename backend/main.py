"""
Application principale FastAPI
IRMSIA Medical AI - Backend
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH pour les imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

from backend.core.config import settings
from backend.core.database import init_db
from backend.api.auth_router import router as auth_router
from backend.api.dicom_router import router as dicom_router
from backend.api.ai_router import router as ai_router
from backend.api.blockchain_router import router as blockchain_router
from backend.api.medical_router import router as medical_router
from backend.api.debug_router import router as debug_router
from backend.models.dto import HealthCheck

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Gestion des erreurs au démarrage
def check_startup():
    """Vérifie que l'application peut démarrer"""
    try:
        # Vérifier les imports critiques
        from backend.core.config import settings
        from backend.core.security import security_manager
        from backend.core.database import engine
        
        # Vérifier les répertoires
        from pathlib import Path
        directories = [
            Path(settings.UPLOAD_DIR),
            Path(settings.ENCRYPTED_DIR),
            Path(settings.PNG_DIR),
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.info("Verifications de demarrage reussies")
        return True
    except Exception as e:
        logger.error(f"ERREUR CRITIQUE au demarrage: {e}", exc_info=True)
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    logger.info("Demarrage d'IRMSIA Medical AI Backend")
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info(f"Mode: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    
    # Créer les répertoires nécessaires
    try:
        from pathlib import Path
        directories = [
            Path(settings.UPLOAD_DIR),
            Path(settings.ENCRYPTED_DIR),
            Path(settings.PNG_DIR),
            Path(settings.LOG_FILE).parent
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        logger.info("Repertoires de stockage crees")
    except Exception as e:
        logger.error(f"Erreur lors de la creation des repertoires: {e}")
    
    # Initialisation de la base de données
    try:
        await init_db()
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de donnees: {e}")
        logger.warning("L'application continue en mode degrade")
    
    logger.info("Backend IRMSIA initialise avec succes")
    
    yield
    
    # Shutdown
    logger.info("Arret d'IRMSIA Medical AI Backend")


# Vérifier le démarrage avant de créer l'application
if not check_startup():
    logger.error("ERREUR: Impossible de demarrer l'application. Verifiez les logs ci-dessus.")
    raise RuntimeError("Erreur critique au demarrage. Consultez les logs.")

# Créer l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="API d'analyse medicale IA avec blockchain pour IRM",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(dicom_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(blockchain_router, prefix="/api/v1")
app.include_router(medical_router, prefix="/api/v1")
app.include_router(debug_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Page d'accueil"""
    return {
        "message": "IRMSIA Medical AI Backend",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Vérification de santé de l'application"""
    components = {
        "database": "ok",
        "blockchain": "ok",
        "ai": "ok",
        "storage": "ok"
    }
    
    # Vérifier les composants (simplifié)
    try:
        from backend.services.blockchain_service import blockchain_service
        components["blockchain"] = "connected" if blockchain_service.blockchain_type != "mock" else "mock"
    except:
        components["blockchain"] = "error"
    
    try:
        from backend.services.ai_service import ai_service
        components["ai"] = ai_service.provider
    except:
        components["ai"] = "error"
    
    return HealthCheck(
        status="healthy",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        timestamp=datetime.now(),
        components=components
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Gestionnaire d'erreurs global"""
    logger.error(f"Erreur non gérée: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erreur interne du serveur",
            "detail": str(exc) if settings.DEBUG else "Une erreur est survenue"
        }
    )


if __name__ == "__main__":
    import uvicorn
    import sys
    from pathlib import Path
    
    # Ajouter la racine du projet au PYTHONPATH
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

