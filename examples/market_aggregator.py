"""Exemple d'agrégation de données de marché en temps réel."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List

from sadie.data.collectors import (
    BinanceTradeCollector,
    KrakenTradeCollector,
    CoinbaseTradeCollector
)
from sadie.core.models.events import Trade

class MarketAggregator:
    """Agrégateur de données de marché."""
    
    def __init__(
        self,
        symbols: List[str],
        update_interval: float = 1.0,
        window_size: int = 100
    ):
        """Initialise l'agrégateur.
        
        Args:
            symbols: Liste des symboles à suivre
            update_interval: Intervalle de mise à jour en secondes
            window_size: Taille de la fenêtre glissante pour les statistiques
        """
        self.symbols = symbols
        self.update_interval = update_interval
        self.window_size = window_size
        
        # Création des collecteurs
        self.collectors = [
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
        
        # État interne
        self._running = False
        self._task = None
    
    async def start(self) -> None:
        """Démarre l'agrégateur."""
        # Démarrage des collecteurs
        for collector in self.collectors:
            await collector.start()
            print(f"Collecteur {collector.name} démarré")
        
        self._running = True
        self._task = asyncio.create_task(self._run())
        print("Agrégateur démarré")
    
    async def stop(self) -> None:
        """Arrête l'agrégateur."""
        self._running = False
        if self._task:
            await self._task
            self._task = None
        
        # Arrêt des collecteurs
        for collector in self.collectors:
            await collector.stop()
            print(f"Collecteur {collector.name} arrêté")
        
        print("Agrégateur arrêté")
    
    async def _run(self) -> None:
        """Boucle principale de l'agrégateur."""
        while self._running:
            try:
                # Collecte et agrégation des données
                aggregated_data = await self._aggregate_data()
                
                # Affichage des résultats
                self._print_aggregated_data(aggregated_data)
                
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                print(f"Erreur lors de l'agrégation: {e}")
                await asyncio.sleep(1)
    
    async def _aggregate_data(self) -> Dict[str, dict]:
        """Agrège les données de tous les collecteurs.
        
        Returns:
            Dictionnaire contenant les données agrégées par symbole
        """
        result = {}
        
        # Collecte des données de chaque exchange
        for collector in self.collectors:
            data = await collector.collect()
            
            for symbol, symbol_data in data.items():
                if symbol not in result:
                    result[symbol] = {
                        "trades": [],
                        "exchanges": {},
                        "global": {
                            "volume": 0.0,
                            "value": 0.0,
                            "vwap": 0.0,
                            "count": 0
                        }
                    }
                
                # Ajout des statistiques par exchange
                stats = symbol_data["statistics"]
                result[symbol]["exchanges"][collector.name] = {
                    "volume": stats["volume"]["total"],
                    "value": stats["value"]["total"],
                    "price": stats["price"]["last"],
                    "count": stats["count"]
                }
                
                # Mise à jour des statistiques globales
                result[symbol]["global"]["volume"] += stats["volume"]["total"]
                result[symbol]["global"]["value"] += stats["value"]["total"]
                result[symbol]["global"]["count"] += stats["count"]
        
        # Calcul du VWAP global
        for symbol_data in result.values():
            if symbol_data["global"]["volume"] > 0:
                symbol_data["global"]["vwap"] = (
                    symbol_data["global"]["value"] / 
                    symbol_data["global"]["volume"]
                )
        
        return result
    
    def _print_aggregated_data(self, data: Dict[str, dict]) -> None:
        """Affiche les données agrégées.
        
        Args:
            data: Données agrégées à afficher
        """
        print("\n" + "=" * 80)
        print(f"Données de marché agrégées - {datetime.now()}")
        print("=" * 80)
        
        for symbol, symbol_data in data.items():
            print(f"\n{symbol}:")
            
            # Statistiques globales
            global_stats = symbol_data["global"]
            print("\nGLOBAL:")
            print(f"  Volume total: {global_stats['volume']:.8f}")
            print(f"  Valeur totale: {global_stats['value']:.2f}")
            print(f"  VWAP: {global_stats['vwap']:.2f}")
            print(f"  Nombre de trades: {global_stats['count']}")
            
            # Statistiques par exchange
            print("\nPar exchange:")
            for exchange, stats in symbol_data["exchanges"].items():
                print(f"\n  {exchange.upper()}:")
                print(f"    Volume: {stats['volume']:.8f}")
                print(f"    Valeur: {stats['value']:.2f}")
                print(f"    Prix: {stats['price']:.2f}")
                print(f"    Trades: {stats['count']}")
        
        print("\n" + "-" * 80)

async def main():
    """Point d'entrée principal."""
    # Configuration
    symbols = ["BTC-USD", "ETH-USD"]
    update_interval = 1.0
    collection_time = 60  # Durée de collecte en secondes
    
    # Création et démarrage de l'agrégateur
    aggregator = MarketAggregator(
        symbols=symbols,
        update_interval=update_interval
    )
    
    try:
        await aggregator.start()
        
        # Collecte pendant la durée spécifiée
        print(f"\nCollecte des données pendant {collection_time} secondes...")
        await asyncio.sleep(collection_time)
        
    finally:
        await aggregator.stop()

if __name__ == "__main__":
    # Configuration du logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    # Exécution
    asyncio.run(main()) 