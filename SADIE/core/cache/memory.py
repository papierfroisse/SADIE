"""Backend de cache en mémoire."""

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from . import CacheBackend
from ..monitoring import get_logger

logger = get_logger(__name__)

class CacheEntry:
    """Entrée de cache avec support de TTL."""
    
    def __init__(self, value: Any, ttl: Optional[int] = None):
        self.value = value
        self.timestamp = time.time()
        self.ttl = ttl
    
    def is_expired(self) -> bool:
        """Vérifie si l'entrée est expirée."""
        if self.ttl is None:
            return False
        return time.time() > (self.timestamp + self.ttl)

class MemoryCache(CacheBackend):
    """Backend de cache en mémoire avec support de TTL."""
    
    def __init__(self, cleanup_interval: int = 60):
        self._cache: Dict[str, CacheEntry] = {}
        self._cleanup_interval = cleanup_interval
        self._cleanup_task: Optional[asyncio.Task] = None
        self.logger = get_logger(__name__)
        
    async def __aenter__(self):
        """Démarre le nettoyage périodique."""
        await self.start_cleanup()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Arrête le nettoyage périodique."""
        await self.stop_cleanup()
    
    async def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache."""
        entry = self._cache.get(key)
        if entry is None:
            return None
            
        if entry.is_expired():
            await self.delete(key)
            return None
            
        return entry.value
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """Stocke une valeur dans le cache."""
        self._cache[key] = CacheEntry(value, ttl)
    
    async def delete(self, key: str) -> None:
        """Supprime une valeur du cache."""
        self._cache.pop(key, None)
    
    async def exists(self, key: str) -> bool:
        """Vérifie si une clé existe dans le cache."""
        entry = self._cache.get(key)
        if entry is None:
            return False
            
        if entry.is_expired():
            await self.delete(key)
            return False
            
        return True
    
    async def clear(self) -> None:
        """Vide le cache."""
        self._cache.clear()
    
    async def start_cleanup(self) -> None:
        """Démarre le nettoyage périodique des entrées expirées."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            self.logger.debug("Nettoyage périodique démarré")
    
    async def stop_cleanup(self) -> None:
        """Arrête le nettoyage périodique."""
        if self._cleanup_task is not None:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            self.logger.debug("Nettoyage périodique arrêté")
    
    async def _cleanup_loop(self) -> None:
        """Boucle de nettoyage des entrées expirées."""
        while True:
            try:
                # Copie des clés pour éviter les modifications pendant l'itération
                keys = list(self._cache.keys())
                for key in keys:
                    entry = self._cache.get(key)
                    if entry and entry.is_expired():
                        await self.delete(key)
                        self.logger.debug(f"Entrée expirée supprimée: {key}")
                
                await asyncio.sleep(self._cleanup_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Erreur pendant le nettoyage: {e}")
                # Continue malgré l'erreur
                await asyncio.sleep(self._cleanup_interval) 