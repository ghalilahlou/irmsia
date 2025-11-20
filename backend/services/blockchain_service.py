"""
Service blockchain
Hyperledger Fabric ou IPFS + Smart Contract
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

from backend.core.config import settings
from backend.models.dto import BlockchainRecord, AccessLog

logger = logging.getLogger(__name__)


class BlockchainService:
    """Service blockchain pour stockage de hash et logs d'accès"""
    
    def __init__(self):
        self.blockchain_type = settings.BLOCKCHAIN_TYPE
        self._initialize_blockchain()
    
    def _initialize_blockchain(self):
        """Initialise la connexion blockchain"""
        if self.blockchain_type == "ipfs":
            self._init_ipfs()
        elif self.blockchain_type == "fabric":
            self._init_fabric()
        elif self.blockchain_type == "mock":
            logger.info("Mode blockchain: MOCK (developpement/test)")
            self.blockchain_type = "mock"
        else:
            logger.warning(f"Type blockchain inconnu: {self.blockchain_type}, utilisation du mode mock")
            self.blockchain_type = "mock"
    
    def _init_ipfs(self):
        """Initialise la connexion IPFS"""
        try:
            from ipfshttpclient import connect
            self.ipfs_client = connect(f"/ip4/{settings.IPFS_HOST}/tcp/{settings.IPFS_PORT}/http")
            logger.info(f"Connexion IPFS établie: {settings.IPFS_HOST}:{settings.IPFS_PORT}")
        except Exception as e:
            logger.error(f"Erreur lors de la connexion IPFS: {e}")
            logger.info("Basculement en mode mock")
            self.blockchain_type = "mock"
    
    def _init_fabric(self):
        """Initialise la connexion Hyperledger Fabric"""
        try:
            # Ici, vous devriez charger la configuration Fabric
            # Pour l'instant, mode mock
            logger.warning("Hyperledger Fabric non encore implémenté, utilisation du mode mock")
            self.blockchain_type = "mock"
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation Fabric: {e}")
            self.blockchain_type = "mock"
    
    def register_hash(
        self,
        image_id: str,
        file_hash: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> BlockchainRecord:
        """
        Enregistre un hash sur la blockchain
        
        Args:
            image_id: Identifiant de l'image
            file_hash: Hash SHA-256 du fichier chiffré
            metadata: Métadonnées optionnelles
            
        Returns:
            Enregistrement blockchain
        """
        try:
            if self.blockchain_type == "ipfs":
                return self._register_hash_ipfs(image_id, file_hash, metadata)
            elif self.blockchain_type == "fabric":
                return self._register_hash_fabric(image_id, file_hash, metadata)
            else:
                return self._register_hash_mock(image_id, file_hash, metadata)
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du hash: {e}")
            return self._register_hash_mock(image_id, file_hash, metadata)
    
    def _register_hash_ipfs(
        self,
        image_id: str,
        file_hash: str,
        metadata: Optional[Dict[str, Any]]
    ) -> BlockchainRecord:
        """Enregistre le hash sur IPFS"""
        try:
            # Créer un document JSON avec les informations
            document = {
                "image_id": image_id,
                "file_hash": file_hash,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # Ajouter à IPFS
            document_json = json.dumps(document)
            ipfs_hash = self.ipfs_client.add_str(document_json)
            
            # Si Ethereum est configuré, enregistrer le hash IPFS dans un smart contract
            if settings.ETHEREUM_RPC_URL and settings.CONTRACT_ADDRESS:
                transaction_id = self._register_on_ethereum(image_id, ipfs_hash, file_hash)
            else:
                transaction_id = None
            
            return BlockchainRecord(
                image_id=image_id,
                hash=file_hash,
                timestamp=datetime.now(),
                transaction_id=transaction_id,
                ipfs_hash=ipfs_hash
            )
            
        except Exception as e:
            logger.error(f"Erreur IPFS: {e}")
            return self._register_hash_mock(image_id, file_hash, metadata)
    
    def _register_hash_fabric(
        self,
        image_id: str,
        file_hash: str,
        metadata: Optional[Dict[str, Any]]
    ) -> BlockchainRecord:
        """Enregistre le hash sur Hyperledger Fabric"""
        # TODO: Implémenter avec Fabric SDK
        return self._register_hash_mock(image_id, file_hash, metadata)
    
    def _register_hash_mock(
        self,
        image_id: str,
        file_hash: str,
        metadata: Optional[Dict[str, Any]]
    ) -> BlockchainRecord:
        """Mode mock pour tests"""
        return BlockchainRecord(
            image_id=image_id,
            hash=file_hash,
            timestamp=datetime.now(),
            transaction_id=f"mock_tx_{image_id}",
            ipfs_hash=None
        )
    
    def _register_on_ethereum(
        self,
        image_id: str,
        ipfs_hash: str,
        file_hash: str
    ) -> Optional[str]:
        """Enregistre le hash sur un smart contract Ethereum"""
        try:
            from web3 import Web3
            
            w3 = Web3(Web3.HTTPProvider(settings.ETHEREUM_RPC_URL))
            
            # Charger le contrat (simplifié)
            # En production, vous devriez charger l'ABI du contrat
            contract_address = settings.CONTRACT_ADDRESS
            
            # Ici, vous appelleriez votre fonction de contrat
            # transaction = contract.functions.registerHash(image_id, ipfs_hash, file_hash).transact()
            # return transaction.hex()
            
            logger.info(f"Hash enregistré sur Ethereum (mock): {image_id}")
            return f"eth_tx_{image_id}"
            
        except Exception as e:
            logger.error(f"Erreur Ethereum: {e}")
            return None
    
    def log_access(
        self,
        image_id: str,
        user_id: str,
        action: str,
        ip_address: Optional[str] = None
    ) -> AccessLog:
        """
        Enregistre un log d'accès sur la blockchain
        
        Args:
            image_id: Identifiant de l'image
            user_id: Identifiant de l'utilisateur
            action: Action effectuée ("view", "analyze", "download")
            ip_address: Adresse IP (optionnel)
            
        Returns:
            Log d'accès
        """
        try:
            access_log = AccessLog(
                image_id=image_id,
                user_id=user_id,
                action=action,
                timestamp=datetime.now(),
                ip_address=ip_address,
                transaction_id=None
            )
            
            if self.blockchain_type == "ipfs":
                # Enregistrer le log sur IPFS
                log_document = {
                    "image_id": image_id,
                    "user_id": user_id,
                    "action": action,
                    "timestamp": access_log.timestamp.isoformat(),
                    "ip_address": ip_address
                }
                log_json = json.dumps(log_document)
                ipfs_hash = self.ipfs_client.add_str(log_json)
                access_log.transaction_id = ipfs_hash
                
            elif self.blockchain_type == "fabric":
                # Enregistrer sur Fabric
                # TODO: Implémenter
                access_log.transaction_id = f"fabric_tx_{image_id}_{datetime.now().timestamp()}"
            else:
                # Mode mock
                access_log.transaction_id = f"mock_access_{image_id}_{datetime.now().timestamp()}"
            
            return access_log
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du log d'accès: {e}")
            return AccessLog(
                image_id=image_id,
                user_id=user_id,
                action=action,
                timestamp=datetime.now(),
                ip_address=ip_address,
                transaction_id=None
            )
    
    def get_hash_record(self, image_id: str) -> Optional[BlockchainRecord]:
        """Récupère l'enregistrement blockchain d'une image"""
        # TODO: Implémenter la récupération depuis la blockchain
        return None
    
    def get_access_logs(self, image_id: str, limit: int = 100) -> List[AccessLog]:
        """Récupère les logs d'accès d'une image"""
        # TODO: Implémenter la récupération depuis la blockchain
        return []


# Instance globale
blockchain_service = BlockchainService()

