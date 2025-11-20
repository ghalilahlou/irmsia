"""
Data Transfer Objects (DTOs)
Modèles Pydantic pour les requêtes et réponses API
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr


# ========== Authentication DTOs ==========

class Token(BaseModel):
    """Token d'authentification"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Données du token"""
    username: Optional[str] = None
    user_id: Optional[int] = None


class LoginRequest(BaseModel):
    """Requête de connexion"""
    username: str
    password: str


class UserCreate(BaseModel):
    """Création d'utilisateur"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "radiologist"  # "radiologist", "admin", "viewer"


# ========== DICOM DTOs ==========

class DICOMUploadResponse(BaseModel):
    """Réponse après upload DICOM"""
    image_id: str
    message: str
    deidentified: bool
    converted: bool
    encrypted: bool
    hash_registered: bool
    timestamp: datetime


class DICOMMetadata(BaseModel):
    """Métadonnées DICOM (dé-identifiées)"""
    modality: Optional[str] = None
    study_date: Optional[str] = None
    study_time: Optional[str] = None
    series_description: Optional[str] = None
    image_type: Optional[str] = None
    pixel_spacing: Optional[List[float]] = None
    slice_thickness: Optional[float] = None
    # Pas de données patient (dé-identifié)


# ========== AI Analysis DTOs ==========

class AIAnalysisRequest(BaseModel):
    """Requête d'analyse IA"""
    image_id: str
    modality: Optional[str] = "MRI"
    additional_context: Optional[str] = None


class Finding(BaseModel):
    """Trouvaille médicale"""
    description: str
    location: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    severity: str = Field(default="normal")  # "normal", "mild", "moderate", "severe"


class AIAnalysisResponse(BaseModel):
    """Réponse d'analyse IA"""
    image_id: str
    findings: List[Finding]
    risk_score: int = Field(ge=0, le=100, description="Score de risque de 0 à 100")
    suggested_diagnosis: str
    confidence: float = Field(ge=0.0, le=1.0)
    ai_model: str = Field(description="Modèle IA utilisé pour l'analyse")
    processing_time: float
    timestamp: datetime
    recommendations: List[str] = []


# ========== Blockchain DTOs ==========

class BlockchainRecord(BaseModel):
    """Enregistrement blockchain"""
    image_id: str
    hash: str
    timestamp: datetime
    transaction_id: Optional[str] = None
    block_number: Optional[int] = None
    ipfs_hash: Optional[str] = None


class AccessLog(BaseModel):
    """Log d'accès"""
    image_id: str
    user_id: str
    action: str  # "view", "analyze", "download"
    timestamp: datetime
    ip_address: Optional[str] = None
    transaction_id: Optional[str] = None


# ========== Audit DTOs ==========

class AuditLogResponse(BaseModel):
    """Réponse de log d'audit"""
    logs: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int


# ========== Health Check DTOs ==========

class HealthCheck(BaseModel):
    """Statut de santé"""
    status: str
    service: str
    version: str
    timestamp: datetime
    components: Dict[str, str] = {}  # "database", "blockchain", "ai", "storage"

