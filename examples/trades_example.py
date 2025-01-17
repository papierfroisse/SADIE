"""Exemple d'utilisation des collecteurs de trades."""

import asyncio
import json
import os
from typing import Dict, List

from sadie.data.collectors import (
    BinanceTradeCollector,
    KrakenTradeCollector,
    CoinbaseTradeCollector
)

async def print_trades(collector_name: str, data: Dict[str, dict]) -> None:
    """Affiche les trades collectés.
    
    Args:
        collector_name: Nom du collecteur
        data: Données collectées
    """
    print(f"\nDonnées de {collector_name}:")
    for symbol, symbol_data in data.items():
        stats = symbol_data["statistics"]
        print(f"\n{symbol}:")
        print(f"  Nombre de trades: {stats['count']}")
        print(f"  Volume total: {stats['volume']['total']:.8f}")
        print(f"  Valeur totale: {stats['value']['total']:.2f}")
        print(f"  Dernier prix: {stats['price']['last']:.2f}")
        print(f"  Variation: {stats['price']['change']:.2f}%")

async def main():
    """Point d'entrée principal."""
    # Configuration
    symbols = ["BTC-USD", "ETH-USD"]
    update_interval = 1.0
    collection_time = 30  # Durée de collecte en secondes
    
    # Création des collecteurs
    collectors = [
        BinanceTradeCollector(
            name="binance",
            symbols=symbols,
            update_interval=update_interval
        ),
        KrakenTradeCollector(
            name="kraken",
            symbols=symbols,
            update_interval=update_interval
        ),
        CoinbaseTradeCollector(
            name="coinbase",
            symbols=symbols,
            update_interval=update_interval
        )
    ]
    
    # Démarrage des collecteurs
    for collector in collectors:
        await collector.start()
        print(f"Collecteur {collector.name} démarré")
    
    try:
        # Collecte pendant la durée spécifiée
        print(f"\nCollecte des trades pendant {collection_time} secondes...")
        await asyncio.sleep(collection_time)
        
        # Affichage des résultats
        for collector in collectors:
            data = await collector.collect()
            await print_trades(collector.name, data)
            
    finally:
        # Arrêt des collecteurs
        for collector in collectors:
            await collector.stop()
            print(f"\nCollecteur {collector.name} arrêté")

if __name__ == "__main__":
    # Configuration du logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    # Exécution
    asyncio.run(main()) 