"""Exemple de détection d'opportunités d'arbitrage."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sadie.data.collectors import (
    BinanceTradeCollector,
    KrakenTradeCollector,
    CoinbaseTradeCollector
)
from sadie.core.models.events import Trade

class ArbitrageDetector:
    """Détecteur d'opportunités d'arbitrage."""
    
    def __init__(
        self,
        symbols: List[str],
        min_spread: float = 0.001,  # 0.1%
        min_volume: float = 0.01,
        update_interval: float = 1.0
    ):
        """Initialise le détecteur.
        
        Args:
            symbols: Liste des symboles à suivre
            min_spread: Spread minimum pour une opportunité (en %)
            min_volume: Volume minimum pour une opportunité
            update_interval: Intervalle de mise à jour en secondes
        """
        self.symbols = symbols
        self.min_spread = min_spread
        self.min_volume = min_volume
        self.update_interval = update_interval
        
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
        self._last_prices: Dict[str, Dict[str, float]] = {}
        self._last_volumes: Dict[str, Dict[str, float]] = {}
    
    async def start(self) -> None:
        """Démarre le détecteur."""
        # Démarrage des collecteurs
        for collector in self.collectors:
            await collector.start()
            print(f"Collecteur {collector.name} démarré")
        
        self._running = True
        self._task = asyncio.create_task(self._run())
        print("Détecteur d'arbitrage démarré")
    
    async def stop(self) -> None:
        """Arrête le détecteur."""
        self._running = False
        if self._task:
            await self._task
            self._task = None
        
        # Arrêt des collecteurs
        for collector in self.collectors:
            await collector.stop()
            print(f"Collecteur {collector.name} arrêté")
        
        print("Détecteur d'arbitrage arrêté")
    
    async def _run(self) -> None:
        """Boucle principale du détecteur."""
        while self._running:
            try:
                # Mise à jour des prix et volumes
                await self._update_market_data()
                
                # Détection des opportunités
                opportunities = self._detect_opportunities()
                
                # Affichage des opportunités
                if opportunities:
                    self._print_opportunities(opportunities)
                
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                print(f"Erreur lors de la détection: {e}")
                await asyncio.sleep(1)
    
    async def _update_market_data(self) -> None:
        """Met à jour les données de marché."""
        for collector in self.collectors:
            data = await collector.collect()
            
            for symbol, symbol_data in data.items():
                # Initialisation des dictionnaires si nécessaire
                if symbol not in self._last_prices:
                    self._last_prices[symbol] = {}
                    self._last_volumes[symbol] = {}
                
                # Mise à jour des prix et volumes
                stats = symbol_data["statistics"]
                self._last_prices[symbol][collector.name] = stats["price"]["last"]
                self._last_volumes[symbol][collector.name] = stats["volume"]["total"]
    
    def _detect_opportunities(self) -> List[Dict]:
        """Détecte les opportunités d'arbitrage.
        
        Returns:
            Liste des opportunités détectées
        """
        opportunities = []
        
        for symbol in self.symbols:
            # Vérification des données disponibles
            if symbol not in self._last_prices:
                continue
            
            # Recherche des meilleurs prix d'achat et de vente
            best_bid = self._find_best_price(symbol, find_highest=False)
            best_ask = self._find_best_price(symbol, find_highest=True)
            
            if not best_bid or not best_ask:
                continue
            
            # Calcul du spread
            spread = (best_ask[1] - best_bid[1]) / best_bid[1]
            
            # Vérification des critères
            if spread > self.min_spread:
                # Vérification des volumes disponibles
                bid_volume = self._last_volumes[symbol][best_bid[0]]
                ask_volume = self._last_volumes[symbol][best_ask[0]]
                
                if bid_volume >= self.min_volume and ask_volume >= self.min_volume:
                    opportunities.append({
                        "symbol": symbol,
                        "timestamp": datetime.now(),
                        "buy": {
                            "exchange": best_bid[0],
                            "price": best_bid[1],
                            "volume": bid_volume
                        },
                        "sell": {
                            "exchange": best_ask[0],
                            "price": best_ask[1],
                            "volume": ask_volume
                        },
                        "spread": spread * 100  # Conversion en pourcentage
                    })
        
        return opportunities
    
    def _find_best_price(
        self,
        symbol: str,
        find_highest: bool = True
    ) -> Optional[Tuple[str, float]]:
        """Trouve le meilleur prix parmi les exchanges.
        
        Args:
            symbol: Symbole à analyser
            find_highest: True pour trouver le prix le plus haut,
                        False pour le plus bas
            
        Returns:
            Tuple (exchange, prix) ou None si pas de données
        """
        prices = self._last_prices.get(symbol, {})
        if not prices:
            return None
        
        best_exchange = None
        best_price = float("-inf") if find_highest else float("inf")
        
        for exchange, price in prices.items():
            if find_highest:
                if price > best_price:
                    best_price = price
                    best_exchange = exchange
            else:
                if price < best_price:
                    best_price = price
                    best_exchange = exchange
        
        return (best_exchange, best_price) if best_exchange else None
    
    def _print_opportunities(self, opportunities: List[Dict]) -> None:
        """Affiche les opportunités détectées.
        
        Args:
            opportunities: Liste des opportunités à afficher
        """
        print("\n" + "=" * 80)
        print(f"Opportunités d'arbitrage détectées - {datetime.now()}")
        print("=" * 80)
        
        for opp in opportunities:
            print(f"\n{opp['symbol']}:")
            print(f"  Spread: {opp['spread']:.2f}%")
            print(f"  Achat: {opp['buy']['exchange'].upper()} @ {opp['buy']['price']:.2f}")
            print(f"  Vente: {opp['sell']['exchange'].upper()} @ {opp['sell']['price']:.2f}")
            print(f"  Volume disponible:")
            print(f"    Achat: {opp['buy']['volume']:.8f}")
            print(f"    Vente: {opp['sell']['volume']:.8f}")
        
        print("\n" + "-" * 80)

async def main():
    """Point d'entrée principal."""
    # Configuration
    symbols = ["BTC-USD", "ETH-USD"]
    min_spread = 0.001  # 0.1%
    min_volume = 0.01
    update_interval = 1.0
    run_time = 300  # 5 minutes
    
    # Création et démarrage du détecteur
    detector = ArbitrageDetector(
        symbols=symbols,
        min_spread=min_spread,
        min_volume=min_volume,
        update_interval=update_interval
    )
    
    try:
        await detector.start()
        
        # Exécution pendant la durée spécifiée
        print(f"\nRecherche d'opportunités pendant {run_time} secondes...")
        await asyncio.sleep(run_time)
        
    finally:
        await detector.stop()

if __name__ == "__main__":
    # Configuration du logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    # Exécution
    asyncio.run(main()) 