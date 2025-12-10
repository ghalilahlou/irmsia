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


# ========== Anomaly Detection DTOs ==========

class BoundingBox(BaseModel):
    """Boîte englobante pour anomalie"""
    id: int
    x: int
    y: int
    width: int
    height: int
    area_pixels: float
    area_mm2: float
    perimeter_pixels: Optional[float] = None
    perimeter_mm: Optional[float] = None
    width_mm: Optional[float] = None
    height_mm: Optional[float] = None
    pathology: Optional[str] = None
    confidence: Optional[float] = None
    severity: Optional[str] = None


class Measurements(BaseModel):
    """Mesures d'anomalies"""
    num_regions: int
    total_area_pixels: Optional[float] = None
    total_area_mm2: Optional[float] = None
    pixel_to_mm_ratio: Optional[float] = None
    image_size: Optional[Dict[str, int]] = None


class AnomalyDetectionResponse(BaseModel):
    """Réponse de détection d'anomalies"""
    has_anomaly: bool
    anomaly_class: str
    confidence: float
    all_probabilities: Optional[Dict[str, float]] = None
    bounding_boxes: Optional[List[BoundingBox]] = None
    segmentation_mask: Optional[List[List[int]]] = None
    visualization: Optional[List[List[Any]]] = None
    measurements: Optional[Measurements] = None
    image_id: Optional[str] = None
    filename: Optional[str] = None
    timestamp: Optional[str] = None
    backend_used: Optional[str] = None
    request_id: Optional[str] = None
    model_name: Optional[str] = Field(default=None, alias="model_used")  # Éviter conflit avec namespace "model_"
    processing_time_seconds: Optional[float] = None
    risk_score: Optional[float] = None
    recommendations: Optional[List[str]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    
    class Config:
        populate_by_name = True
        protected_namespaces = ()


class MedicalReportResponse(BaseModel):
    """Réponse de rapport médical"""
    summary: str
    findings: List[str]
    measurements: str
    recommendations: List[str]
    severity: str
    confidence: float
    anomaly_type: str
    patient_info: Optional[Dict[str, Any]] = None
    image_id: Optional[str] = None
    report_date: Optional[str] = None
    explanatory_schemas: Optional[Dict[str, Any]] = None
    visualization_available: Optional[bool] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    num_regions: Optional[int] = None
    bounding_boxes_count: Optional[int] = None