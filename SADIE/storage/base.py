"""Module de base pour le stockage."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar

from ..core.monitoring import get_logger
from ..utils.decorators import log_execution, retry

logger = get_logger(__name__)

T = TypeVar('T')

class StorageBackend(ABC):
    """Interface abstraite pour les backends de stockage."""
    
    @abstractmethod
    async def connect(self) -> None:
        """Établit la connexion au stockage."""
        pass
        
    @abstractmethod
    async def disconnect(self) -> None:
        """Ferme la connexion au stockage."""
        pass
        
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur."""
        pass
        
    @abstractmethod
    async def set(self, key: str, value: Any) -> None:
        """Stocke une valeur."""
        pass
        
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Supprime une valeur."""
        pass
        
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Vérifie si une clé existe."""
        pass
        
    @abstractmethod
    async def clear(self) -> None:
        """Vide le stockage."""
        pass

class Storage:
    """Gestionnaire de stockage principal."""
    
    def __init__(self, backend: StorageBackend):
        self.backend = backend
        self.logger = get_logger(__name__)
        
    async def __aenter__(self):
        """Support du context manager."""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ferme la connexion à la sortie du context."""
        await self.disconnect()
        
    @log_execution()
    async def connect(self) -> None:
        """Établit la connexion au stockage."""
        try:
            await self.backend.connect()
            self.logger.info("Connexion au stockage établie")
        except Exception as e:
            self.logger.error(f"Erreur de connexion au stockage: {e}")
            raise
            
    @log_execution()
    async def disconnect(self) -> None:
        """Ferme la connexion au stockage."""
        try:
            await self.backend.disconnect()
            self.logger.info("Connexion au stockage fermée")
        except Exception as e:
            self.logger.error(f"Erreur lors de la déconnexion: {e}")
            raise
            
    @retry(max_attempts=3)
    async def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du stockage."""
        try:
            value = await self.backend.get(key)
            if value is not None:
                self.logger.debug(f"Valeur récupérée pour la clé: {key}")
            else:
                self.logger.debug(f"Aucune valeur trouvée pour la clé: {key}")
            return value
        except Exception as e:
            self.logger.error(f"Erreur lors de la lecture: {e}")
            raise
            
    @retry(max_attempts=3)
    async def set(self, key: str, value: Any) -> None:
        """Stocke une valeur."""
        try:
            await self.backend.set(key, value)
            self.logger.debug(f"Valeur stockée pour la clé: {key}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'écriture: {e}")
            raise
            
    @retry(max_attempts=3)
    async def delete(self, key: str) -> None:
        """Supprime une valeur."""
        try:
            await self.backend.delete(key)
            self.logger.debug(f"Valeur supprimée pour la clé: {key}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la suppression: {e}")
            raise
            
    async def exists(self, key: str) -> bool:
        """Vérifie si une clé existe."""
        try:
            return await self.backend.exists(key)
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification: {e}")
            raise
            
    async def clear(self) -> None:
        """Vide le stockage."""
        try:
            await self.backend.clear()
            self.logger.info("Stockage vidé")
        except Exception as e:
            self.logger.error(f"Erreur lors du vidage: {e}")
            raise 