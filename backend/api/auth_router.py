"""
Routes d'authentification
JWT authentication
"""

import logging
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.security import security_manager
from backend.models.dto import Token, LoginRequest, UserCreate
# from backend.core.database import get_db  # Pour utilisation future avec vraie DB

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


# Base de données utilisateurs simplifiée (en production, utiliser une vraie DB)
# Pour l'instant, stockage en mémoire
# Initialisation différée pour éviter les erreurs au démarrage
users_db = {}

def init_users_db():
    """Initialise la base de données utilisateurs"""
    global users_db
    if not users_db:
        try:
            users_db = {
                "admin": {
                    "username": "admin",
                    "email": "admin@irmsia.com",
                    "hashed_password": security_manager.hash_password("admin123"),
                    "full_name": "Administrator",
                    "role": "admin",
                    "disabled": False
                },
                "radiologist": {
                    "username": "radiologist",
                    "email": "radiologist@irmsia.com",
                    "hashed_password": security_manager.hash_password("radio123"),
                    "full_name": "Radiologist User",
                    "role": "radiologist",
                    "disabled": False
                }
            }
            logger.info("Base de donnees utilisateurs initialisee")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la base de donnees utilisateurs: {e}")
            raise

# Initialiser au chargement du module
try:
    init_users_db()
except Exception as e:
    logger.error(f"ERREUR CRITIQUE: Impossible d'initialiser users_db: {e}")
    # Créer une base vide pour éviter les erreurs d'import
    users_db = {}


def get_user(username: str):
    """Récupère un utilisateur"""
    return users_db.get(username)


def authenticate_user(username: str, password: str):
    """Authentifie un utilisateur"""
    user = get_user(username)
    if not user:
        return False
    if not security_manager.verify_password(password, user["hashed_password"]):
        return False
    return user


def get_current_user(token: Optional[str] = Depends(oauth2_scheme)):
    """
    Récupère l'utilisateur actuel depuis le token
    Si AUTH_ENABLED=False, retourne un utilisateur par défaut sans vérification
    """
    # Si l'authentification est désactivée, retourner un utilisateur par défaut
    if not settings.AUTH_ENABLED:
        logger.debug("Authentification desactivee - retour utilisateur par defaut")
        return {
            "username": "admin",
            "email": "admin@irmsia.com",
            "full_name": "Administrator",
            "role": "admin",
            "disabled": False
        }
    
    # Authentification activée - vérifier le token
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Si pas de token fourni
    if token is None:
        raise credentials_exception
    
    payload = security_manager.verify_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = get_user(username)
    if user is None:
        raise credentials_exception
    
    return user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint de connexion
    Retourne un token JWT
    """
    try:
        # S'assurer que la base de données est initialisée
        if not users_db:
            init_users_db()
        
        logger.info(f"Tentative de connexion pour l'utilisateur: {form_data.username}")
        
        user = authenticate_user(form_data.username, form_data.password)
        if not user:
            logger.warning(f"Echec de connexion pour l'utilisateur: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Authentification reussie pour l'utilisateur: {form_data.username}")
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security_manager.create_access_token(
            data={"sub": user["username"], "role": user["role"]},
            expires_delta=access_token_expires
        )
        
        logger.info(f"Token genere avec succes pour l'utilisateur: {form_data.username}")
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except HTTPException:
        # Re-lancer les HTTPException telles quelles
        raise
    except Exception as e:
        # Logger toutes les autres erreurs
        logger.error(f"Erreur lors de la connexion: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne du serveur: {str(e)}" if settings.DEBUG else "Erreur interne du serveur",
        )


@router.post("/register")
async def register(user_data: UserCreate):
    """
    Enregistrement d'un nouvel utilisateur
    (En production, ajouter validation et stockage en DB)
    """
    if get_user(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = security_manager.hash_password(user_data.password)
    users_db[user_data.username] = {
        "username": user_data.username,
        "email": user_data.email,
        "hashed_password": hashed_password,
        "full_name": user_data.full_name,
        "role": user_data.role,
        "disabled": False
    }
    
    return {"message": "User registered successfully", "username": user_data.username}


@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Récupère les informations de l'utilisateur actuel"""
    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "role": current_user["role"]
    }

