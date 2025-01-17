"""
Module de gestion du cache avec Redis.
"""

import json
import logging
from typing import Optional, Any, Dict
import aioredis
from datetime import datetime

logger = logging.getLogger(__name__)

class Cache:
    """Gestionnaire de cache utilisant Redis."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        prefix: str = "sadie:",
        pool_size: int = 10
    ):
        """Initialise la connexion au cache Redis.
        
        Args:
            host: Hôte Redis
            port: Port Redis
            db: Base de données Redis
            prefix: Préfixe pour les clés
            pool_size: Taille du pool de connexions
        """
        self.prefix = prefix
        self._redis: Optional[aioredis.Redis] = None
        self._pool_size = pool_size
        self._connection_params = {
            "host": host,
            "port": port,
            "db": db,
            "encoding": "utf-8",
            "decode_responses": True
        }
        
    async def connect(self) -> None:
        """Établit la connexion au serveur Redis."""
        if not self._redis:
            try:
                self._redis = await aioredis.from_url(
                    f"redis://{self._connection_params['host']}:{self._connection_params['port']}",
                    db=self._connection_params['db'],
                    encoding=self._connection_params['encoding'],
                    decode_responses=self._connection_params['decode_responses'],
                    max_connections=self._pool_size
                )
                logger.info("Connexion au cache Redis établie")
            except Exception as e:
                logger.error(f"Erreur de connexion à Redis: {str(e)}")
                raise
                
    async def disconnect(self) -> None:
        """Ferme la connexion au serveur Redis."""
        if self._redis:
            await self._redis.close()
            self._redis = None
            logger.info("Déconnexion du cache Redis effectuée")
            
    def _format_key(self, key: str) -> str:
        """Formate une clé avec le préfixe.
        
        Args:
            key: Clé à formater
            
        Returns:
            Clé formatée
        """
        return f"{self.prefix}{key}"
        
    async def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache.
        
        Args:
            key: Clé à récupérer
            
        Returns:
            Valeur associée à la clé ou None
        """
        if not self._redis:
            await self.connect()
            
        try:
            value = await self._redis.get(self._format_key(key))
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du cache: {str(e)}")
            return None
            
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """Stocke une valeur dans le cache.
        
        Args:
            key: Clé à stocker
            value: Valeur à stocker
            expire: Durée d'expiration en secondes
            
        Returns:
            True si succès, False sinon
        """
        if not self._redis:
            await self.connect()
            
        try:
            formatted_key = self._format_key(key)
            await self._redis.set(
                formatted_key,
                json.dumps(value),
                ex=expire
            )
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture dans le cache: {str(e)}")
            return False
            
    async def delete(self, key: str) -> bool:
        """Supprime une clé du cache.
        
        Args:
            key: Clé à supprimer
            
        Returns:
            True si succès, False sinon
        """
        if not self._redis:
            await self.connect()
            
        try:
            await self._redis.delete(self._format_key(key))
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du cache: {str(e)}")
            return False
            
    async def clear(self, pattern: str = "*") -> bool:
        """Nettoie le cache selon un pattern.
        
        Args:
            pattern: Pattern des clés à supprimer
            
        Returns:
            True si succès, False sinon
        """
        if not self._redis:
            await self.connect()
            
        try:
            cursor = 0
            while True:
                cursor, keys = await self._redis.scan(
                    cursor,
                    match=self._format_key(pattern),
                    count=100
                )
                if keys:
                    await self._redis.delete(*keys)
                if cursor == 0:
                    break
            return True
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage du cache: {str(e)}")
            return False
            
    async def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques du cache.
        
        Returns:
            Dictionnaire des statistiques
        """
        if not self._redis:
            await self.connect()
            
        try:
            info = await self._redis.info()
            return {
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_connections_received": info.get("total_connections_received", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0)
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats: {str(e)}")
            return {} 