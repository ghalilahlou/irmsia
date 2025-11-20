"""
Configuration de la base de données
SQLite pour les logs d'audit (POC)
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)

# Créer l'engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()


def get_db():
    """Dependency pour obtenir une session DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """Initialise la base de données"""
    try:
        # Créer les répertoires nécessaires
        from pathlib import Path
        db_path = Path(settings.DATABASE_URL.replace("sqlite:///", ""))
        if db_path.parent != Path("."):
            db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Créer les tables
        Base.metadata.create_all(bind=engine)
        logger.info("Base de données initialisée")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        # Ne pas faire échouer l'application si la DB échoue (mode dégradé)
        logger.warning("L'application continue en mode dégradé (sans base de données)")

