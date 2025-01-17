"""Exemple d'utilisation des deux stockages en parallèle."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List

from sadie.core.models.events import Trade
from sadie.data.collectors import (
    BinanceTradeCollector,
    KrakenTradeCollector,
    CoinbaseTradeCollector
)
from sadie.storage import RedisStorage, TimescaleStorage

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DualStorage:
    """Classe utilitaire pour gérer les deux stockages."""
    
    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        timescale_dsn: str = "postgresql://postgres:postgres@localhost:5432/sadie"
    ):
        """Initialise les stockages.
        
        Args:
            redis_host: Hôte Redis
            redis_port: Port Redis
            redis_db: Base de données Redis
            timescale_dsn: DSN TimescaleDB
        """
        # Stockage temps réel
        self.redis = RedisStorage(
            name="redis",
            host=redis_host,
            port=redis_port,
            db=redis_db,
            max_trades=1000
        )
        
        # Stockage historique
        self.timescale = TimescaleStorage(
            name="timescale",
            dsn=timescale_dsn
        )
    
    async def connect(self) -> None:
        """Connecte les deux stockages."""
        await asyncio.gather(
            self.redis.connect(),
            self.timescale.connect()
        )
    
    async def disconnect(self) -> None:
        """Déconnecte les deux stockages."""
        await asyncio.gather(
            self.redis.disconnect(),
            self.timescale.disconnect()
        )
    
    async def store_trades(self, symbol: str, trades: List[Trade]) -> None:
        """Stocke les trades dans les deux stockages.
        
        Args:
            symbol: Symbole des trades
            trades: Liste des trades à stocker
        """
        await asyncio.gather(
            self.redis.store_trades(symbol, trades),
            self.timescale.store_trades(symbol, trades)
        )
    
    async def store_statistics(self, symbol: str, statistics: Dict) -> None:
        """Stocke les statistiques dans les deux stockages.
        
        Args:
            symbol: Symbole concerné
            statistics: Statistiques à stocker
        """
        await asyncio.gather(
            self.redis.store_statistics(symbol, statistics),
            self.timescale.store_statistics(symbol, statistics)
        )

async def main():
    """Fonction principale."""
    try:
        # Configuration du stockage dual
        storage = DualStorage()
        await storage.connect()
        
        # Liste des symboles à suivre
        symbols = ["BTC/USDT", "ETH/USDT"]
        
        # Création des collecteurs
        collectors = [
            BinanceTradeCollector(
                name="binance",
                symbols=symbols,
                storage=storage.redis  # Redis pour les données en temps réel
            ),
            KrakenTradeCollector(
                name="kraken",
                symbols=symbols,
                storage=storage.timescale  # TimescaleDB pour l'historique
            ),
            CoinbaseTradeCollector(
                name="coinbase",
                symbols=symbols,
                storage=storage  # Les deux stockages via DualStorage
            )
        ]
        
        # Démarrage des collecteurs
        await asyncio.gather(*(c.start() for c in collectors))
        logger.info("Collecteurs démarrés")
        
        # Collecte pendant 2 minutes
        await asyncio.sleep(120)
        
        # Analyse des données collectées
        for symbol in symbols:
            # Données en temps réel (Redis)
            redis_trades = await storage.redis.get_trades(symbol)
            redis_stats = await storage.redis.get_statistics(symbol)
            
            logger.info(f"Redis - {symbol}:")
            logger.info(f"  - {len(redis_trades)} trades récents")
            logger.info(f"  - Prix: {redis_stats['price']:.2f}")
            logger.info(f"  - Volume: {redis_stats['volume']:.2f}")
            logger.info(f"  - VWAP: {redis_stats['vwap']:.2f}")
            
            # Données historiques (TimescaleDB)
            start_time = datetime.now() - timedelta(minutes=5)
            timescale_trades = await storage.timescale.get_trades(
                symbol,
                start_time=start_time.timestamp()
            )
            timescale_stats = await storage.timescale.get_statistics(symbol)
            
            logger.info(f"TimescaleDB - {symbol}:")
            logger.info(f"  - {len(timescale_trades)} trades sur 5 minutes")
            logger.info(f"  - Prix: {timescale_stats['price']:.2f}")
            logger.info(f"  - Volume: {timescale_stats['volume']:.2f}")
            logger.info(f"  - VWAP: {timescale_stats['vwap']:.2f}")
            
            # Comparaison des données
            price_diff = abs(redis_stats["price"] - timescale_stats["price"])
            logger.info(f"Différence de prix: {price_diff:.2f}")
        
        # Arrêt des collecteurs
        await asyncio.gather(*(c.stop() for c in collectors))
        logger.info("Collecteurs arrêtés")
        
        # Déconnexion des stockages
        await storage.disconnect()
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        raise

if __name__ == "__main__":
    # Exécution de l'exemple
    asyncio.run(main()) 