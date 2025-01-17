"""Exemple d'utilisation du système de stockage."""

import asyncio
import logging
from datetime import datetime, timedelta

from sadie.data.collectors import BinanceTradeCollector
from sadie.storage import RedisStorage, TimescaleStorage

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Fonction principale."""
    try:
        # Configuration du stockage Redis pour les données en temps réel
        redis = RedisStorage(
            name="redis",
            host="localhost",
            port=6379,
            db=0,
            max_trades=1000
        )
        
        # Configuration du stockage TimescaleDB pour l'historique
        timescale = TimescaleStorage(
            name="timescale",
            dsn="postgresql://postgres:postgres@localhost:5432/sadie"
        )
        
        # Connexion aux stockages
        await redis.connect()
        await timescale.connect()
        
        # Création du collecteur avec Redis pour le temps réel
        collector = BinanceTradeCollector(
            name="binance",
            symbols=["BTC/USDT", "ETH/USDT"],
            storage=redis
        )
        
        # Démarrage de la collecte
        await collector.start()
        logger.info("Collecte démarrée")
        
        # Collecte pendant 1 minute
        await asyncio.sleep(60)
        
        # Récupération des données en temps réel depuis Redis
        for symbol in collector.symbols:
            # Trades récents
            trades = await redis.get_trades(symbol)
            logger.info(f"Redis - {symbol}: {len(trades)} trades récents")
            
            # Statistiques en temps réel
            stats = await redis.get_statistics(symbol)
            logger.info(f"Redis - {symbol} stats: prix={stats['price']:.2f}, "
                       f"volume={stats['volume']:.2f}, trades={stats['trades']}")
        
        # Change le stockage pour TimescaleDB
        collector.storage = timescale
        logger.info("Changement vers TimescaleDB")
        
        # Collecte pendant 1 minute supplémentaire
        await asyncio.sleep(60)
        
        # Récupération des données historiques depuis TimescaleDB
        for symbol in collector.symbols:
            # Trades des 5 dernières minutes
            start_time = datetime.now() - timedelta(minutes=5)
            trades = await timescale.get_trades(
                symbol,
                start_time=start_time.timestamp()
            )
            logger.info(f"TimescaleDB - {symbol}: {len(trades)} trades sur 5 minutes")
            
            # Statistiques
            stats = await timescale.get_statistics(symbol)
            logger.info(f"TimescaleDB - {symbol} stats: prix={stats['price']:.2f}, "
                       f"volume={stats['volume']:.2f}, trades={stats['trades']}")
        
        # Arrêt du collecteur
        await collector.stop()
        logger.info("Collecte arrêtée")
        
        # Déconnexion des stockages
        await redis.disconnect()
        await timescale.disconnect()
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        raise

if __name__ == "__main__":
    # Exécution de l'exemple
    asyncio.run(main()) 