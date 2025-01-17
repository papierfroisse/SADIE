"""Module de stockage Redis."""

import json
import logging
from typing import Any, Dict, List, Optional

import redis.asyncio as redis
from redis.asyncio.client import Redis

from sadie.core.models.events import Trade
from .base import BaseStorage

class RedisStorage(BaseStorage):
    """Stockage des données dans Redis."""
    
    def __init__(
        self,
        name: str,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        max_trades: int = 1000,
        logger: Optional[logging.Logger] = None
    ):
        """Initialise le stockage Redis.
        
        Args:
            name: Nom du stockage
            host: Hôte Redis
            port: Port Redis
            db: Base de données Redis
            password: Mot de passe Redis (optionnel)
            max_trades: Nombre maximum de trades à conserver par symbole
            logger: Logger optionnel
        """
        super().__init__(name, logger)
        
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.max_trades = max_trades
        
        self._redis: Optional[Redis] = None
    
    async def connect(self) -> None:
        """Établit la connexion à Redis."""
        if self._redis:
            return
            
        self._redis = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=True
        )
        
        # Test de la connexion
        await self._redis.ping()
        self.logger.info(f"Connecté à Redis: {self.host}:{self.port}/{self.db}")
    
    async def disconnect(self) -> None:
        """Ferme la connexion à Redis."""
        if self._redis:
            await self._redis.close()
            self._redis = None
            self.logger.info("Déconnecté de Redis")
    
    async def store_trades(self, symbol: str, trades: List[Trade]) -> None:
        """Stocke une liste de trades.
        
        Args:
            symbol: Symbole des trades
            trades: Liste des trades à stocker
        """
        if not self._redis:
            raise RuntimeError("Non connecté à Redis")
            
        # Clé pour la liste des trades du symbole
        key = f"trades:{symbol}"
        
        # Conversion des trades en JSON
        trades_json = [
            json.dumps({
                "exchange": t.exchange,
                "symbol": t.symbol,
                "price": t.price,
                "amount": t.amount,
                "timestamp": t.timestamp.timestamp(),
                "side": t.side,
                "trade_id": t.trade_id
            })
            for t in trades
        ]
        
        # Ajout des trades à la liste
        async with self._redis.pipeline() as pipe:
            # Ajout des nouveaux trades
            await pipe.rpush(key, *trades_json)
            # Limitation de la taille de la liste
            await pipe.ltrim(key, -self.max_trades, -1)
            await pipe.execute()
    
    async def get_trades(
        self,
        symbol: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: Optional[int] = None
    ) -> List[Trade]:
        """Récupère les trades stockés.
        
        Args:
            symbol: Symbole des trades
            start_time: Timestamp de début (optionnel)
            end_time: Timestamp de fin (optionnel)
            limit: Nombre maximum de trades à retourner (optionnel)
            
        Returns:
            Liste des trades correspondants aux critères
        """
        if not self._redis:
            raise RuntimeError("Non connecté à Redis")
            
        # Clé pour la liste des trades du symbole
        key = f"trades:{symbol}"
        
        # Récupération de tous les trades
        trades_json = await self._redis.lrange(key, 0, -1)
        
        # Conversion des trades JSON en objets Trade
        trades = []
        for trade_json in trades_json:
            data = json.loads(trade_json)
            trade = Trade(
                exchange=data["exchange"],
                symbol=data["symbol"],
                price=data["price"],
                amount=data["amount"],
                timestamp=data["timestamp"],
                side=data["side"],
                trade_id=data["trade_id"]
            )
            
            # Filtrage par timestamp
            if start_time and trade.timestamp < start_time:
                continue
            if end_time and trade.timestamp > end_time:
                continue
                
            trades.append(trade)
        
        # Limitation du nombre de trades
        if limit:
            trades = trades[-limit:]
            
        return trades
    
    async def store_statistics(self, symbol: str, statistics: Dict[str, Any]) -> None:
        """Stocke les statistiques d'un symbole.
        
        Args:
            symbol: Symbole concerné
            statistics: Statistiques à stocker
        """
        if not self._redis:
            raise RuntimeError("Non connecté à Redis")
            
        # Clé pour les statistiques du symbole
        key = f"stats:{symbol}"
        
        # Stockage des statistiques en JSON
        await self._redis.set(key, json.dumps(statistics))
    
    async def get_statistics(
        self,
        symbol: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """Récupère les statistiques stockées.
        
        Args:
            symbol: Symbole concerné
            start_time: Timestamp de début (optionnel)
            end_time: Timestamp de fin (optionnel)
            
        Returns:
            Statistiques correspondant aux critères
        """
        if not self._redis:
            raise RuntimeError("Non connecté à Redis")
            
        # Clé pour les statistiques du symbole
        key = f"stats:{symbol}"
        
        # Récupération des statistiques
        stats_json = await self._redis.get(key)
        if not stats_json:
            return {}
            
        return json.loads(stats_json) 