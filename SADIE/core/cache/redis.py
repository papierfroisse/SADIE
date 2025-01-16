"""Backend de cache Redis."""

import json
from typing import Any, Optional

import aioredis

from . import CacheBackend
from ..monitoring import get_logger

logger = get_logger(__name__)

class RedisCache(CacheBackend):
    """Backend de cache Redis."""
    
    def __init__(
        self,
        url: str = "redis://localhost",
        prefix: str = "cache:",
        encoding: str = "utf-8"
    ):
        self.url = url
        self.prefix = prefix
        self.encoding = encoding
        self._redis: Optional[aioredis.Redis] = None
        self.logger = get_logger(__name__)
    
    async def connect(self) -> None:
        """Établit la connexion à Redis."""
        if self._redis is None:
            try:
                self._redis = await aioredis.from_url(
                    self.url,
                    encoding=self.encoding,
                    decode_responses=True
                )
                self.logger.info(f"Connecté à Redis: {self.url}")
            except Exception as e:
                self.logger.error(f"Erreur de connexion à Redis: {e}")
                raise
    
    async def disconnect(self) -> None:
        """Ferme la connexion à Redis."""
        if self._redis is not None:
            await self._redis.close()
            self._redis = None
            self.logger.info("Déconnecté de Redis")
    
    async def __aenter__(self):
        """Support du context manager."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ferme la connexion à la sortie du context."""
        await self.disconnect()
    
    def _get_key(self, key: str) -> str:
        """Génère la clé complète avec le préfixe."""
        return f"{self.prefix}{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache."""
        try:
            if self._redis is None:
                await self.connect()
                
            value = await self._redis.get(self._get_key(key))
            if value is not None:
                return json.loads(value)
            return None
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la lecture Redis: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """Stocke une valeur dans le cache."""
        try:
            if self._redis is None:
                await self.connect()
                
            serialized = json.dumps(value)
            if ttl is not None:
                await self._redis.setex(
                    self._get_key(key),
                    ttl,
                    serialized
                )
            else:
                await self._redis.set(
                    self._get_key(key),
                    serialized
                )
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'écriture Redis: {e}")
            raise
    
    async def delete(self, key: str) -> None:
        """Supprime une valeur du cache."""
        try:
            if self._redis is None:
                await self.connect()
                
            await self._redis.delete(self._get_key(key))
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la suppression Redis: {e}")
            raise
    
    async def exists(self, key: str) -> bool:
        """Vérifie si une clé existe dans le cache."""
        try:
            if self._redis is None:
                await self.connect()
                
            return bool(await self._redis.exists(self._get_key(key)))
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification Redis: {e}")
            return False
    
    async def clear(self) -> None:
        """Vide le cache."""
        try:
            if self._redis is None:
                await self.connect()
                
            # Supprime uniquement les clés avec notre préfixe
            cursor = 0
            while True:
                cursor, keys = await self._redis.scan(
                    cursor,
                    match=f"{self.prefix}*"
                )
                if keys:
                    await self._redis.delete(*keys)
                if cursor == 0:
                    break
                    
        except Exception as e:
            self.logger.error(f"Erreur lors du vidage Redis: {e}")
            raise 