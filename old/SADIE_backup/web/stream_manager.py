"""Gestionnaire de flux WebSocket."""

import asyncio
from typing import Dict, List, Set
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)

class StreamManager:
    """Gestionnaire des connexions WebSocket."""
    
    def __init__(self):
        """Initialisation du gestionnaire."""
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
        
    async def connect(self, websocket: WebSocket, symbol: str):
        """Connecte un client WebSocket pour un symbole."""
        await websocket.accept()
        
        if symbol not in self.active_connections:
            self.active_connections[symbol] = set()
        self.active_connections[symbol].add(websocket)
        
        logger.info(f"Nouvelle connexion WebSocket pour {symbol}")
        
    async def disconnect(self, websocket: WebSocket, symbol: str):
        """Déconnecte un client WebSocket."""
        self.active_connections[symbol].remove(websocket)
        if not self.active_connections[symbol]:
            del self.active_connections[symbol]
            if symbol in self.tasks:
                self.tasks[symbol].cancel()
                del self.tasks[symbol]
                
        logger.info(f"Déconnexion WebSocket pour {symbol}")
        
    async def broadcast(self, symbol: str, message: dict):
        """Diffuse un message à tous les clients connectés pour un symbole."""
        if symbol not in self.active_connections:
            return
            
        dead_connections = set()
        for connection in self.active_connections[symbol]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi du message: {e}")
                dead_connections.add(connection)
                
        # Nettoyage des connexions mortes
        for dead in dead_connections:
            await self.disconnect(dead, symbol)
            
    async def start_stream(self, symbol: str, collector):
        """Démarre un flux de données pour un symbole."""
        if symbol in self.tasks:
            return
            
        async def stream_data():
            while True:
                try:
                    # Récupération des données en temps réel
                    data = await collector.get_latest_data()
                    
                    # Enrichissement avec les indicateurs techniques
                    indicators = await collector.calculate_indicators(data)
                    
                    # Diffusion des données
                    await self.broadcast(symbol, {
                        "type": "market_data",
                        "symbol": symbol,
                        "data": data,
                        "indicators": indicators,
                        "timestamp": data.get("timestamp", None)
                    })
                    
                    await asyncio.sleep(1)  # Intervalle de mise à jour
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Erreur dans le flux de données: {e}")
                    await asyncio.sleep(5)  # Attente avant réessai
                    
        self.tasks[symbol] = asyncio.create_task(stream_data())
        
    def stop_stream(self, symbol: str):
        """Arrête un flux de données."""
        if symbol in self.tasks:
            self.tasks[symbol].cancel()
            del self.tasks[symbol] 