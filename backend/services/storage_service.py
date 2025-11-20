"""
Service de stockage
Gestion du stockage local et S3
"""

import os
from pathlib import Path
from typing import Optional, BinaryIO
import logging
import boto3
from botocore.exceptions import ClientError

from backend.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Service de stockage (local ou S3)"""
    
    def __init__(self):
        self.use_s3 = settings.USE_S3
        self.s3_client = None
        
        if self.use_s3:
            self._init_s3()
    
    def _init_s3(self):
        """Initialise le client S3"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            logger.info(f"S3 client initialisé pour le bucket: {settings.S3_BUCKET_NAME}")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation S3: {e}")
            logger.info("Basculement vers le stockage local")
            self.use_s3 = False
    
    def upload_file(
        self,
        file_path: str,
        object_name: Optional[str] = None,
        bucket: Optional[str] = None
    ) -> str:
        """
        Upload un fichier (local ou S3)
        
        Returns:
            Chemin ou clé S3 du fichier
        """
        if self.use_s3 and self.s3_client:
            return self._upload_to_s3(file_path, object_name, bucket)
        else:
            return self._upload_local(file_path)
    
    def _upload_to_s3(
        self,
        file_path: str,
        object_name: Optional[str],
        bucket: Optional[str]
    ) -> str:
        """Upload vers S3"""
        bucket_name = bucket or settings.S3_BUCKET_NAME
        if not object_name:
            object_name = Path(file_path).name
        
        try:
            self.s3_client.upload_file(file_path, bucket_name, object_name)
            logger.info(f"Fichier uploadé vers S3: {object_name}")
            return f"s3://{bucket_name}/{object_name}"
        except ClientError as e:
            logger.error(f"Erreur lors de l'upload S3: {e}")
            raise
    
    def _upload_local(self, file_path: str) -> str:
        """Stockage local (déjà fait, retourne le chemin)"""
        return file_path
    
    def download_file(
        self,
        object_name: str,
        local_path: str,
        bucket: Optional[str] = None
    ) -> str:
        """
        Télécharge un fichier (S3 ou local)
        
        Returns:
            Chemin local du fichier téléchargé
        """
        if self.use_s3 and self.s3_client and object_name.startswith("s3://"):
            return self._download_from_s3(object_name, local_path, bucket)
        else:
            # Fichier local
            if os.path.exists(object_name):
                return object_name
            else:
                raise FileNotFoundError(f"Fichier non trouvé: {object_name}")
    
    def _download_from_s3(
        self,
        s3_path: str,
        local_path: str,
        bucket: Optional[str]
    ) -> str:
        """Télécharge depuis S3"""
        # Parser s3://bucket/key
        parts = s3_path.replace("s3://", "").split("/", 1)
        bucket_name = parts[0] if len(parts) > 0 else (bucket or settings.S3_BUCKET_NAME)
        object_key = parts[1] if len(parts) > 1 else s3_path
        
        try:
            self.s3_client.download_file(bucket_name, object_key, local_path)
            logger.info(f"Fichier téléchargé depuis S3: {object_key}")
            return local_path
        except ClientError as e:
            logger.error(f"Erreur lors du téléchargement S3: {e}")
            raise
    
    def delete_file(self, object_name: str, bucket: Optional[str] = None) -> bool:
        """Supprime un fichier"""
        if self.use_s3 and self.s3_client and object_name.startswith("s3://"):
            return self._delete_from_s3(object_name, bucket)
        else:
            # Fichier local
            if os.path.exists(object_name):
                os.remove(object_name)
                return True
            return False
    
    def _delete_from_s3(self, s3_path: str, bucket: Optional[str]) -> bool:
        """Supprime depuis S3"""
        parts = s3_path.replace("s3://", "").split("/", 1)
        bucket_name = parts[0] if len(parts) > 0 else (bucket or settings.S3_BUCKET_NAME)
        object_key = parts[1] if len(parts) > 1 else s3_path
        
        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=object_key)
            logger.info(f"Fichier supprimé de S3: {object_key}")
            return True
        except ClientError as e:
            logger.error(f"Erreur lors de la suppression S3: {e}")
            return False


# Instance globale
storage_service = StorageService()

