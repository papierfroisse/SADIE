"""
Module de gestion des données en temps réel.
"""

import asyncio
import datetime
import json
import logging
from typing import Any, Callable, Dict, List, Optional, Set, Union

import websockets
from websockets.exceptions import ConnectionClosed

from sadie.data.collectors.exceptions import ConnectionError, ValidationError
from sadie.data.config import DataConfig

logger = logging.getLogger(__name__)

class RealtimeManager:
    """Gestionnaire de données en temps réel."""
    
    def __init__(self):
        """Initialise le gestionnaire de données en temps réel."""
        self.subscriptions: Dict[str, Set[str]] = {}
        self.callbacks: Dict[str, List[Callable]] = {}
        self.connections: Dict[str, websockets.WebSocketClientProtocol] = {}
        self.running = False
    
    async def start(self) -> None:
        """Démarre le gestionnaire de données en temps réel."""
        if self.running:
            return
        
        self.running = True
        await self._connect_all()
    
    async def stop(self) -> None:
        """Arrête le gestionnaire de données en temps réel."""
        self.running = False
        
        # Fermeture des connexions
        for source, ws in self.connections.items():
            try:
                await ws.close()
            except Exception as e:
                logger.error(f"Erreur lors de la fermeture de la connexion {source}: {e}")
        
        self.connections.clear()
        self.subscriptions.clear()
    
    async def subscribe(
        self,
        source: str,
        symbol: str,
        callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        S'abonne aux données en temps réel.
        
        Args:
            source: Source des données
            symbol: Symbole
            callback: Fonction de rappel pour les données
            
        Raises:
            ValidationError: Si la source ou le symbole n'est pas valide
            ConnectionError: Si la connexion échoue
        """
        # Validation des paramètres
        if not DataConfig.get_source_config(source):
            raise ValidationError(f"Source non supportée: {source}")
        if not DataConfig.validate_symbol(symbol):
            raise ValidationError(f"Symbole non supporté: {symbol}")
        
        # Initialisation des structures
        if source not in self.subscriptions:
            self.subscriptions[source] = set()
            self.callbacks[source] = []
        
        # Ajout de la souscription
        self.subscriptions[source].add(symbol)
        self.callbacks[source].append(callback)
        
        # Connexion si nécessaire
        if source not in self.connections and self.running:
            await self._connect(source)
    
    async def unsubscribe(
        self,
        source: str,
        symbol: str,
        callback: Optional[Callable] = None
    ) -> None:
        """
        Se désabonne des données en temps réel.
        
        Args:
            source: Source des données
            symbol: Symbole
            callback: Fonction de rappel spécifique (optionnel)
        """
        if source in self.subscriptions:
            # Suppression du symbole
            self.subscriptions[source].discard(symbol)
            
            # Suppression du callback
            if callback and source in self.callbacks:
                self.callbacks[source].remove(callback)
            
            # Fermeture de la connexion si plus de souscriptions
            if not self.subscriptions[source] and source in self.connections:
                await self.connections[source].close()
                del self.connections[source]
    
    async def _connect_all(self) -> None:
        """Établit toutes les connexions nécessaires."""
        for source in self.subscriptions:
            if source not in self.connections:
                await self._connect(source)
    
    async def _connect(self, source: str) -> None:
        """
        Établit une connexion pour une source.
        
        Args:
            source: Source des données
            
        Raises:
            ConnectionError: Si la connexion échoue
        """
        config = DataConfig.get_source_config(source)
        if not config:
            raise ConnectionError(f"Configuration manquante pour {source}")
        
        try:
            if source == "binance":
                await self._connect_binance()
            elif source == "alpha_vantage":
                logger.warning("Alpha Vantage ne supporte pas les données en temps réel")
            else:
                raise ConnectionError(f"Source non supportée: {source}")
        except Exception as e:
            raise ConnectionError(f"Erreur de connexion à {source}: {str(e)}")
    
    async def _connect_binance(self) -> None:
        """Établit une connexion WebSocket avec Binance."""
        ws_url = "wss://stream.binance.com:9443/ws"
        
        try:
            # Connexion
            ws = await websockets.connect(ws_url)
            self.connections["binance"] = ws
            
            # Souscription aux flux
            symbols = self.subscriptions.get("binance", set())
            if symbols:
                streams = []
                for symbol in symbols:
                    formatted_symbol = symbol.replace("/", "").lower()
                    streams.extend([
                        f"{formatted_symbol}@trade",
                        f"{formatted_symbol}@depth"
                    ])
                
                subscribe_msg = {
                    "method": "SUBSCRIBE",
                    "params": streams,
                    "id": 1
                }
                await ws.send(json.dumps(subscribe_msg))
            
            # Démarrage de la boucle de réception
            asyncio.create_task(self._receive_binance(ws))
            
        except Exception as e:
            raise ConnectionError(f"Erreur de connexion à Binance: {str(e)}")
    
    async def _receive_binance(self, ws: websockets.WebSocketClientProtocol) -> None:
        """
        Reçoit les données de Binance.
        
        Args:
            ws: Connexion WebSocket
        """
        try:
            while self.running:
                try:
                    message = await ws.recv()
                    data = json.loads(message)
                    
                    # Traitement des données de trade
                    if "e" in data and data["e"] == "trade":
                        trade_data = {
                            "type": "trade",
                            "symbol": data["s"],
                            "timestamp": data["T"] / 1000,
                            "price": float(data["p"]),
                            "quantity": float(data["q"]),
                            "buyer_maker": data["m"]
                        }
                        
                        # Appel des callbacks
                        for callback in self.callbacks.get("binance", []):
                            try:
                                callback(trade_data)
                            except Exception as e:
                                logger.error(f"Erreur dans le callback: {e}")
                    
                    # Traitement des données de profondeur
                    elif "e" in data and data["e"] == "depthUpdate":
                        depth_data = {
                            "type": "depth",
                            "symbol": data["s"],
                            "timestamp": data["T"] / 1000,
                            "first_update_id": data["U"],
                            "final_update_id": data["u"],
                            "bids": [[float(p), float(q)] for p, q in data["b"]],
                            "asks": [[float(p), float(q)] for p, q in data["a"]]
                        }
                        
                        # Appel des callbacks
                        for callback in self.callbacks.get("binance", []):
                            try:
                                callback(depth_data)
                            except Exception as e:
                                logger.error(f"Erreur dans le callback: {e}")
                
                except ConnectionClosed:
                    logger.warning("Connexion Binance fermée, tentative de reconnexion...")
                    await asyncio.sleep(5)
                    await self._connect_binance()
                    break
                
                except Exception as e:
                    logger.error(f"Erreur lors de la réception des données: {e}")
                    await asyncio.sleep(1)
        
        finally:
            if "binance" in self.connections:
                del self.connections["binance"] 