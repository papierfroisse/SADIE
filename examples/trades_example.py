"""Exemple d'utilisation du collecteur de transactions."""

import asyncio
import json
from datetime import datetime

from SADIE.data.collectors.trades import TradeCollector
from SADIE.core.monitoring import get_logger

logger = get_logger(__name__)

async def print_trades(data: dict) -> None:
    """Affiche les données de transactions.
    
    Args:
        data: Données de transactions
    """
    for symbol, trade_data in data.items():
        print(f"\n=== {symbol} ===")
        stats = trade_data["statistics"]
        
        print("Statistiques (100 dernières transactions):")
        print(f"Nombre de trades: {stats['count']}")
        print(f"Volume total: {stats['volume']['total']}")
        print(f"Valeur totale: {stats['value']['total']}")
        print(f"Prix: {stats['price']['last']} ({stats['price']['change']:.2f}%)")
        
        print("\nDernières transactions:")
        for trade in trade_data["trades"][-5:]:  # 5 dernières transactions
            print(
                f"  {trade['timestamp']} - "
                f"{trade['side'].upper()} "
                f"{trade['amount']} @ {trade['price']}"
            )
        print("-" * 40)

async def main():
    """Point d'entrée principal."""
    # Configuration du collecteur
    symbols = ["BTC-USD", "ETH-USD"]
    collector = TradeCollector(
        name="example",
        symbols=symbols,
        update_interval=1.0,
        max_trades=1000
    )
    
    try:
        # Démarrage du collecteur
        await collector.start()
        logger.info("Collecteur démarré")
        
        # Collecte pendant 30 secondes
        for _ in range(30):
            data = await collector.collect()
            await print_trades(data)
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