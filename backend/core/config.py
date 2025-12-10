"""
Configuration centrale de l'application
Variables d'environnement et paramètres
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Application
    APP_NAME: str = "IRMSIA Medical AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    AUTH_ENABLED: bool = Field(default=False, env="AUTH_ENABLED")  # Désactivé par défaut
    
    # CORS
    ALLOWED_HOSTS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://10.5.0.2:3000",  # Network IP for frontend access
        ],
        env="ALLOWED_HOSTS"
    )
    
    # DICOM & Storage
    UPLOAD_DIR: str = Field(default="./storage/uploads", env="UPLOAD_DIR")
    ENCRYPTED_DIR: str = Field(default="./storage/encrypted", env="ENCRYPTED_DIR")
    PNG_DIR: str = Field(default="./storage/png", env="PNG_DIR")
    MAX_UPLOAD_SIZE: int = Field(default=100 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 100MB
    
    # Encryption
    ENCRYPTION_KEY: str = Field(..., env="ENCRYPTION_KEY")  # 32 bytes for AES-256
    ENCRYPTION_ALGORITHM: str = "AES-256-GCM"
    
    # AI Configuration
    AI_PROVIDER: str = Field(default="mock", env="AI_PROVIDER")  # "mock", "huggingface", "openai"
    HUGGINGFACE_MODEL: str = Field(
        default="microsoft/git-base",
        env="HUGGINGFACE_MODEL"
    )
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4-vision-preview", env="OPENAI_MODEL")
    
    # Blockchain Configuration
    BLOCKCHAIN_TYPE: str = Field(default="ipfs", env="BLOCKCHAIN_TYPE")  # "ipfs" or "fabric"
    IPFS_HOST: str = Field(default="127.0.0.1", env="IPFS_HOST")
    IPFS_PORT: int = Field(default=5001, env="IPFS_PORT")
    ETHEREUM_RPC_URL: Optional[str] = Field(default=None, env="ETHEREUM_RPC_URL")
    CONTRACT_ADDRESS: Optional[str] = Field(default=None, env="CONTRACT_ADDRESS")
    PRIVATE_KEY: Optional[str] = Field(default=None, env="PRIVATE_KEY")
    
    # Hyperledger Fabric (if used)
    FABRIC_NETWORK_CONFIG: Optional[str] = Field(default=None, env="FABRIC_NETWORK_CONFIG")
    FABRIC_CHANNEL_NAME: str = Field(default="mychannel", env="FABRIC_CHANNEL_NAME")
    FABRIC_CHAINCODE_NAME: str = Field(default="medical-chaincode", env="FABRIC_CHAINCODE_NAME")
    
    # Database (for audit logs)
    DATABASE_URL: str = Field(
        default="sqlite:///./medical_audit.db",
        env="DATABASE_URL"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="./logs/irmsia.log", env="LOG_FILE")
    
    # S3 (Production)
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    S3_BUCKET_NAME: Optional[str] = Field(default=None, env="S3_BUCKET_NAME")
    USE_S3: bool = Field(default=False, env="USE_S3")
    
    class Config:
        env_file_encoding = "utf-8"
        case_sensitive = True


# Charger le fichier .env manuellement avant de créer Settings
# Chercher le fichier .env à la racine du projet
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"

if env_file.exists():
    # Charger les variables depuis .env dans os.environ
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    # Ne pas écraser les variables déjà définies
                    if key not in os.environ:
                        os.environ[key] = value
        logger.info(f"Fichier .env chargé depuis {env_file}")
    except Exception as e:
        logger.warning(f"Erreur lors du chargement du .env: {e}")
else:
    logger.warning(f"Fichier .env non trouvé à {env_file}")

# Instance globale avec gestion d'erreur
try:
    settings = Settings()
    logger.info("Configuration chargée avec succès")
except Exception as e:
    logger.error("=" * 60)
    logger.error(f"ERREUR CRITIQUE: Impossible de charger la configuration: {e}")
    logger.error("=" * 60)
    logger.error("SOLUTION:")
    logger.error("1. Créez un fichier .env dans backend/")
    logger.error("2. Copiez backend/.env.example vers backend/.env")
    logger.error("3. Remplissez SECRET_KEY et ENCRYPTION_KEY")
    logger.error("4. Exécutez: python backend/diagnose-startup.py")
    logger.error("=" * 60)
    # Ne pas faire échouer immédiatement, permettre le diagnostic
    import sys
    if 'diagnose-startup' not in sys.argv[0]:
        raise

