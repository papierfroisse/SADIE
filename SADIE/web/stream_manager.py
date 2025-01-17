"""Gestionnaire de flux de données pour la visualisation web."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import WebSocket

from ..core.collectors.trade_collector import TradeCollector
from ..core.models.events import Symbol

logger = logging.getLogger(__name__)

class StreamManager:
    """Gère les flux de données pour la visualisation web."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.collectors: Dict[str, TradeCollector] = {}
        self.running = False
        self._tasks = []
        
    async def connect(self, websocket: WebSocket):
        """Ajoute une nouvelle connexion WebSocket."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Nouvelle connexion WebSocket établie. Total: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        """Supprime une connexion WebSocket."""
        self.active_connections.remove(websocket)
        logger.info(f"Connexion WebSocket fermée. Restantes: {len(self.active_connections)}")
        
    async def broadcast(self, message: dict):
        """Envoie un message à toutes les connexions actives."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi du message: {e}")
                disconnected.append(connection)
                
        # Nettoyage des connexions mortes
        for connection in disconnected:
            self.disconnect(connection)
            
    async def start_collector(self, symbol: str):
        """Démarre un collecteur pour un symbole."""
        if symbol not in self.collectors:
            collector = TradeCollector(
                name=f"web_{symbol}",
                symbols=[symbol],
                max_trades_per_symbol=1000,
                cache_enabled=True
            )
            await collector.connect("binance")
            self.collectors[symbol] = collector
            logger.info(f"Collecteur démarré pour {symbol}")
            
    async def stop_collector(self, symbol: str):
        """Arrête un collecteur."""
        if symbol in self.collectors:
            collector = self.collectors[symbol]
            await collector.disconnect()
            del self.collectors[symbol]
            logger.info(f"Collecteur arrêté pour {symbol}")
            
    async def process_trades(self):
        """Traite les trades et met à jour les visualisations."""
        while self.running:
            try:
                for symbol, collector in self.collectors.items():
                    trades = collector.get_trades(symbol, limit=1)
                    if trades:
                        latest_trade = trades[-1]
                        message = {
                            "timestamp": latest_trade["timestamp"],
                            "symbol": symbol,
                            "price": float(latest_trade["price"]),
                            "volume": float(latest_trade["amount"]),
                            "side": latest_trade["side"]
                        }
                        await self.broadcast(message)
                        
            except Exception as e:
                logger.error(f"Erreur lors du traitement des trades: {e}")
                
            await asyncio.sleep(0.1)  # Évite de surcharger le CPU
            
    async def start(self, symbols: Optional[List[str]] = None):
        """Démarre le gestionnaire de flux."""
        if symbols is None:
            symbols = [Symbol.BTC_USDT.value]
            
        self.running = True
        
        # Démarrage des collecteurs
        for symbol in symbols:
            await self.start_collector(symbol)
            
        # Démarrage du traitement des trades
        process_task = asyncio.create_task(self.process_trades())
        self._tasks.append(process_task)
        
        logger.info("Gestionnaire de flux démarré")
        
    async def stop(self):
        """Arrête le gestionnaire de flux."""
        self.running = False
        
        # Arrêt des collecteurs
        for symbol in list(self.collectors.keys()):
            await self.stop_collector(symbol)
            
        # Annulation des tâches
        for task in self._tasks:
            task.cancel()
            
        # Fermeture des connexions WebSocket
        for connection in self.active_connections:
            await connection.close()
            
        self.active_connections.clear()
        logger.info("Gestionnaire de flux arrêté") 