"""
Exemple de collecte de données d'orderbook.
"""

import asyncio
import logging
from datetime import datetime

from sadie.data.collectors import OrderBookCollector
from sadie.storage import MemoryStorage
from sadie.utils.logging import setup_logging

# Configuration du logging
setup_logging(level="INFO")
logger = logging.getLogger(__name__)

async def main():
    """Fonction principale."""
    # Initialisation des composants
    collector = OrderBookCollector(
        cache_size=1000,
        prediction_window=30,
        depth_level="L2",
        update_interval=0.1
    )
    storage = MemoryStorage()
    
    try:
        # Connexion au WebSocket
        await collector.start_ws()
        await storage.connect()
        
        # Souscription aux symboles
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        for symbol in symbols:
            await collector.subscribe_symbol(symbol)
            logger.info(f"Souscrit à {symbol}")
        
        # Collecte pendant 5 minutes
        start_time = datetime.utcnow()
        while (datetime.utcnow() - start_time).total_seconds() < 300:
            for symbol in symbols:
                # Récupération des données
                orderbook = await collector.get_order_book(symbol)
                metrics = collector.get_order_book_metrics(symbol)
                
                # Stockage des données
                await storage.store({
                    "symbol": symbol,
                    "timestamp": datetime.utcnow(),
                    "orderbook": orderbook,
                    "metrics": metrics
                })
            
            # Attente avant la prochaine collecte
            await asyncio.sleep(1)
            
            # Affichage des statistiques
            if (datetime.utcnow() - start_time).total_seconds() % 60 == 0:
                stats = collector.get_cache_stats()
                for symbol in symbols:
                    if symbol in stats:
                        logger.info(f"Stats pour {symbol}: {stats[symbol]}")
    
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur: {e}")
    finally:
        # Nettoyage
        await collector.stop_ws()
        await storage.disconnect()
        logger.info("Collecte terminée")

if __name__ == "__main__":
    asyncio.run(main()) 