"""Module de stockage Redis."""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
import redis.asyncio as redis
from .base import BaseStorage

class RedisStorage(BaseStorage):
    """Stockage des données dans Redis."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None
    ):
        """Initialise la connexion Redis.
        
        Args:
            host: Hôte Redis
            port: Port Redis
            db: Base de données Redis
            password: Mot de passe Redis optionnel
        """
        self.redis_url = f"redis://{host}:{port}/{db}"
        self.password = password
        self.client = None
        
    async def connect(self) -> None:
        """Établit la connexion à Redis."""
        self.client = redis.from_url(
            self.redis_url,
            password=self.password,
            decode_responses=True
        )
        await self.client.ping()
        
    async def disconnect(self) -> None:
        """Ferme la connexion Redis."""
        if self.client:
            await self.client.close()
            self.client = None
            
    async def store_trades(self, trades: List[Dict[str, Any]]) -> None:
        """Stocke une liste de trades dans Redis.
        
        Args:
            trades: Liste des trades à stocker
        """
        if not self.client:
            raise ConnectionError("Not connected to Redis")
            
        pipe = self.client.pipeline()
        for trade in trades:
            # Utilise le timestamp comme score pour le tri
            score = trade.get("timestamp", datetime.now().timestamp())
            # Stocke le trade dans un sorted set par symbole
            symbol = trade.get("symbol", "unknown")
            key = f"trades:{symbol}"
            pipe.zadd(key, {json.dumps(trade): score})
        await pipe.execute()
        
    async def get_trades(
        self,
        symbol: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Récupère les trades pour un symbole donné.
        
        Args:
            symbol: Le symbole à récupérer
            start_time: Timestamp de début optionnel
            end_time: Timestamp de fin optionnel
            
        Returns:
            Liste des trades correspondants
        """
        if not self.client:
            raise ConnectionError("Not connected to Redis")
            
        key = f"trades:{symbol}"
        min_score = start_time.timestamp() if start_time else "-inf"
        max_score = end_time.timestamp() if end_time else "+inf"
        
        # Récupère les trades triés par timestamp
        trade_data = await self.client.zrangebyscore(
            key,
            min_score,
            max_score
        )
        
        return [json.loads(trade) for trade in trade_data]
        
    async def store_statistics(self, symbol: str, stats: Dict[str, Any]) -> None:
        """Stocke les statistiques pour un symbole.
        
        Args:
            symbol: Le symbole concerné
            stats: Les statistiques à stocker
        """
        if not self.client:
            raise ConnectionError("Not connected to Redis")
            
        key = f"stats:{symbol}"
        await self.client.set(key, json.dumps(stats))
        
    async def get_statistics(self, symbol: str) -> Dict[str, Any]:
        """Récupère les statistiques pour un symbole.
        
        Args:
            symbol: Le symbole concerné
            
        Returns:
            Les statistiques du symbole
        """
        if not self.client:
            raise ConnectionError("Not connected to Redis")
            
        key = f"stats:{symbol}"
        data = await self.client.get(key)
        return json.loads(data) if data else {} 