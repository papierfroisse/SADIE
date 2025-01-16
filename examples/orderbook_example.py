"""Exemple d'utilisation du collecteur de carnets d'ordres."""

import asyncio
import json
from datetime import datetime

from SADIE.data.collectors.orderbook import OrderBookCollector
from SADIE.core.monitoring import get_logger

logger = get_logger(__name__)

async def print_orderbook(data: dict) -> None:
    """Affiche les données du carnet d'ordres.
    
    Args:
        data: Données du carnet d'ordres
    """
    for symbol, orderbook in data.items():
        print(f"\n=== {symbol} ===")
        print(f"Timestamp: {orderbook['timestamp']}")
        print("\nBids:")
        for bid in orderbook["bids"][:5]:
            print(f"  {bid[0]} @ {bid[1]}")
        print("\nAsks:")
        for ask in orderbook["asks"][:5]:
            print(f"  {ask[0]} @ {ask[1]}")
        print("-" * 40)

async def main():
    """Point d'entrée principal."""
    # Configuration du collecteur
    symbols = ["BTC-USD", "ETH-USD"]
    collector = OrderBookCollector(
        name="example",
        symbols=symbols,
        update_interval=1.0,
        depth=10
    )
    
    try:
        # Démarrage du collecteur
        await collector.start()
        logger.info("Collecteur démarré")
        
        # Collecte pendant 30 secondes
        for _ in range(30):
            data = await collector.collect()
            await print_orderbook(data)
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur: {e}")
    finally:
        # Arrêt propre du collecteur
        await collector.stop()
        logger.info("Collecteur arrêté")

if __name__ == "__main__":
    asyncio.run(main()) 