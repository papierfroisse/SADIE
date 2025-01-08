"""
Collecteur de données tick par tick pour SADIE.
"""

import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Callable, Any

from .base import BaseCollector
from .exceptions import CollectorError
from ..cache import Cache

logger = logging.getLogger(__name__)

class TickCollector(BaseCollector):
    """Collecteur spécialisé pour les données tick par tick."""
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        symbols: List[str],
        cache_size: int = 1000000,  # Cache 1M ticks par défaut
        batch_size: int = 1000      # Taille des lots pour le traitement
    ):
        """Initialise le collecteur de ticks.
        
        Args:
            api_key: Clé API Binance
            api_secret: Secret API Binance
            symbols: Liste des paires de trading à surveiller
            cache_size: Taille du cache en nombre de ticks
            batch_size: Taille des lots pour le traitement par lots
        """
        super().__init__(api_key, api_secret)
        self.symbols = symbols
        self.cache = Cache(max_size=cache_size)
        self.batch_size = batch_size
        
        self._callbacks: Dict[str, List[Callable]] = {}
        self._streams: Dict[str, asyncio.Task] = {}
        self._batch_processors: Dict[str, asyncio.Task] = {}
        self._running = False
        
    async def start(self) -> None:
        """Démarre la collecte des données tick par tick."""
        if self._running:
            return
            
        try:
            self._running = True
            
            # Démarrer les flux pour chaque symbole
            for symbol in self.symbols:
                self._streams[symbol] = asyncio.create_task(
                    self._maintain_tick_stream(symbol)
                )
                self._batch_processors[symbol] = asyncio.create_task(
                    self._process_tick_batches(symbol)
                )
                
            logger.info(f"Démarrage de la collecte tick pour {len(self.symbols)} symboles")
            
        except Exception as e:
            self._running = False
            raise CollectorError(f"Erreur au démarrage du collecteur tick: {str(e)}")
            
    async def stop(self) -> None:
        """Arrête la collecte des données tick par tick."""
        if not self._running:
            return
            
        try:
            self._running = False
            
            # Arrêter tous les flux
            for task in self._streams.values():
                task.cancel()
            
            # Arrêter les processeurs de lots
            for task in self._batch_processors.values():
                task.cancel()
                
            # Attendre la fin des tâches
            await asyncio.gather(
                *self._streams.values(),
                *self._batch_processors.values(),
                return_exceptions=True
            )
            
            self._streams.clear()
            self._batch_processors.clear()
            
            logger.info("Arrêt de la collecte tick")
            
        except Exception as e:
            raise CollectorError(f"Erreur à l'arrêt du collecteur tick: {str(e)}")
            
    def register_callback(
        self,
        symbol: str,
        callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """Enregistre un callback pour les mises à jour tick.
        
        Args:
            symbol: Paire de trading
            callback: Fonction à appeler pour chaque tick
        """
        if symbol not in self._callbacks:
            self._callbacks[symbol] = []
        self._callbacks[symbol].append(callback)
        
    def unregister_callback(
        self,
        symbol: str,
        callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """Désenregistre un callback.
        
        Args:
            symbol: Paire de trading
            callback: Fonction à désenregistrer
        """
        if symbol in self._callbacks:
            self._callbacks[symbol].remove(callback)
            
    async def get_latest_ticks(
        self,
        symbol: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Récupère les derniers ticks pour un symbole.
        
        Args:
            symbol: Paire de trading
            limit: Nombre de ticks à récupérer
            
        Returns:
            Liste des derniers ticks
        """
        return self.cache.get_latest(f"ticks:{symbol}", limit)
        
    async def _maintain_tick_stream(self, symbol: str) -> None:
        """Maintient le flux de données tick pour un symbole."""
        while self._running:
            try:
                uri = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@trade"
                async with self.websocket_connect(uri) as ws:
                    logger.info(f"Connecté au flux tick pour {symbol}")
                    
                    async for message in ws:
                        if not self._running:
                            break
                            
                        tick = self._parse_tick_message(message)
                        await self._handle_tick(symbol, tick)
                            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur flux tick {symbol}: {str(e)}")
                await asyncio.sleep(5)  # Attente avant reconnexion
                
    async def _process_tick_batches(self, symbol: str) -> None:
        """Traite les ticks par lots pour un symbole."""
        batch: List[Dict[str, Any]] = []
        
        while self._running:
            try:
                # Attendre d'avoir assez de ticks
                if len(batch) < self.batch_size:
                    await asyncio.sleep(0.1)
                    continue
                    
                # Traiter le lot
                await self._process_batch(symbol, batch)
                batch.clear()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur traitement lot {symbol}: {str(e)}")
                await asyncio.sleep(1)
                
    async def _handle_tick(self, symbol: str, tick: Dict[str, Any]) -> None:
        """Gère un nouveau tick.
        
        Args:
            symbol: Paire de trading
            tick: Données du tick
        """
        # Ajouter au cache
        self.cache.add(f"ticks:{symbol}", tick)
        
        # Notifier les callbacks
        if symbol in self._callbacks:
            for callback in self._callbacks[symbol]:
                try:
                    callback(tick)
                except Exception as e:
                    logger.error(f"Erreur callback {symbol}: {str(e)}")
                    
    async def _process_batch(
        self,
        symbol: str,
        batch: List[Dict[str, Any]]
    ) -> None:
        """Traite un lot de ticks.
        
        Args:
            symbol: Paire de trading
            batch: Liste de ticks à traiter
        """
        # Calcul de statistiques sur le lot
        stats = self._compute_batch_stats(batch)
        
        # Mise en cache des statistiques
        self.cache.add(f"stats:{symbol}", stats)
        
    def _parse_tick_message(self, message: str) -> Dict[str, Any]:
        """Parse un message tick du websocket.
        
        Args:
            message: Message brut du websocket
            
        Returns:
            Tick parsé et normalisé
        """
        data = eval(message)
        return {
            "timestamp": int(data["T"]) / 1000,  # Conversion en secondes
            "price": Decimal(str(data["p"])),
            "quantity": Decimal(str(data["q"])),
            "buyer_maker": bool(data["m"]),
            "trade_id": str(data["t"])
        }
        
    def _compute_batch_stats(
        self,
        batch: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calcule des statistiques sur un lot de ticks.
        
        Args:
            batch: Liste de ticks
            
        Returns:
            Statistiques calculées
        """
        if not batch:
            return {}
            
        prices = [tick["price"] for tick in batch]
        quantities = [tick["quantity"] for tick in batch]
        
        return {
            "timestamp": batch[-1]["timestamp"],
            "price_min": min(prices),
            "price_max": max(prices),
            "price_mean": sum(prices) / len(prices),
            "volume": sum(quantities),
            "trades": len(batch),
            "buyer_maker_ratio": sum(1 for t in batch if t["buyer_maker"]) / len(batch)
        } 