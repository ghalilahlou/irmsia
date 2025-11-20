"""
Module de sécurité
JWT, chiffrement AES-256, hash SHA-256
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
import base64
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityManager:
    """Gestionnaire de sécurité centralisé"""
    
    def __init__(self):
        # Générer ou charger la clé de chiffrement
        self.encryption_key = self._get_encryption_key()
        self.aesgcm = AESGCM(self.encryption_key)
    
    def _get_encryption_key(self) -> bytes:
        """Récupère ou génère la clé de chiffrement AES-256"""
        key_str = settings.ENCRYPTION_KEY
        
        # Si la clé est fournie en hex, la convertir
        if len(key_str) == 64:  # 32 bytes en hex
            try:
                return bytes.fromhex(key_str)
            except ValueError:
                pass
        
        # Sinon, générer une clé à partir de la chaîne
        key_hash = hashlib.sha256(key_str.encode()).digest()
        return key_hash
    
    def hash_password(self, password: str) -> str:
        """Hash un mot de passe"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Vérifie un mot de passe"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Crée un token JWT"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Vérifie et décode un token JWT"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError as e:
            logger.warning(f"Token invalide: {e}")
            return None
    
    def encrypt_data(self, data: bytes) -> bytes:
        """Chiffre des données avec AES-256-GCM"""
        nonce = secrets.token_bytes(12)  # 96 bits pour GCM
        ciphertext = self.aesgcm.encrypt(nonce, data, None)
        # Retourner nonce + ciphertext
        return nonce + ciphertext
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Déchiffre des données avec AES-256-GCM"""
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext
    
    def encrypt_file(self, file_path: str, output_path: str) -> str:
        """Chiffre un fichier et retourne le chemin"""
        with open(file_path, "rb") as f:
            data = f.read()
        
        encrypted = self.encrypt_data(data)
        
        with open(output_path, "wb") as f:
            f.write(encrypted)
        
        return output_path
    
    def decrypt_file(self, encrypted_path: str, output_path: str) -> str:
        """Déchiffre un fichier et retourne le chemin"""
        with open(encrypted_path, "rb") as f:
            encrypted_data = f.read()
        
        decrypted = self.decrypt_data(encrypted_data)
        
        with open(output_path, "wb") as f:
            f.write(decrypted)
        
        return output_path
    
    def compute_hash(self, data: bytes) -> str:
        """Calcule le hash SHA-256 de données"""
        return hashlib.sha256(data).hexdigest()
    
    def compute_file_hash(self, file_path: str) -> str:
        """Calcule le hash SHA-256 d'un fichier"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


# Instance globale avec gestion d'erreur
try:
    security_manager = SecurityManager()
    logger.info("SecurityManager initialisé avec succès")
except Exception as e:
    logger.error(f"ERREUR CRITIQUE: Impossible d'initialiser SecurityManager: {e}")
    logger.error("Vérifiez que ENCRYPTION_KEY est défini dans .env")
    raise

