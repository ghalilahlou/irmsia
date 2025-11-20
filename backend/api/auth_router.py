"""
Routes d'authentification
JWT authentication
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.security import security_manager
from backend.models.dto import Token, LoginRequest, UserCreate
# from backend.core.database import get_db  # Pour utilisation future avec vraie DB

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# Base de données utilisateurs simplifiée (en production, utiliser une vraie DB)
# Pour l'instant, stockage en mémoire
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


def get_current_user(token: str = Depends(oauth2_scheme)):
    """Récupère l'utilisateur actuel depuis le token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
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
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security_manager.create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


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

