"""Module de cache pour SADIE."""

from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Callable, Optional, TypeVar

from ..monitoring import get_logger

logger = get_logger(__name__)

T = TypeVar('T')

class CacheBackend(ABC):
    """Interface abstraite pour les backends de cache."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache."""
        pass
    
    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """Stocke une valeur dans le cache."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Supprime une valeur du cache."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Vérifie si une clé existe dans le cache."""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Vide le cache."""
        pass

class Cache:
    """Gestionnaire de cache principal."""
    
    def __init__(self, backend: CacheBackend):
        self.backend = backend
        self.logger = get_logger(__name__)
    
    async def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache."""
        try:
            value = await self.backend.get(key)
            if value is not None:
                self.logger.debug(f"Cache hit pour la clé: {key}")
            else:
                self.logger.debug(f"Cache miss pour la clé: {key}")
            return value
        except Exception as e:
            self.logger.error(f"Erreur lors de la lecture du cache: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[timedelta] = None
    ) -> None:
        """Stocke une valeur dans le cache."""
        try:
            ttl_seconds = int(ttl.total_seconds()) if ttl else None
            await self.backend.set(key, value, ttl_seconds)
            self.logger.debug(
                f"Valeur mise en cache pour la clé: {key}"
                + (f" (TTL: {ttl})" if ttl else "")
            )
        except Exception as e:
            self.logger.error(f"Erreur lors de l'écriture dans le cache: {e}")
    
    async def delete(self, key: str) -> None:
        """Supprime une valeur du cache."""
        try:
            await self.backend.delete(key)
            self.logger.debug(f"Valeur supprimée du cache pour la clé: {key}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la suppression du cache: {e}")
    
    async def exists(self, key: str) -> bool:
        """Vérifie si une clé existe dans le cache."""
        try:
            return await self.backend.exists(key)
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification du cache: {e}")
            return False
    
    async def clear(self) -> None:
        """Vide le cache."""
        try:
            await self.backend.clear()
            self.logger.debug("Cache vidé")
        except Exception as e:
            self.logger.error(f"Erreur lors du vidage du cache: {e}")
    
    async def get_or_set(
        self,
        key: str,
        default_func: Callable[[], T],
        ttl: Optional[timedelta] = None
    ) -> T:
        """Récupère une valeur du cache ou la calcule si absente."""
        value = await self.get(key)
        if value is None:
            value = default_func()
            await self.set(key, value, ttl)
        return value 