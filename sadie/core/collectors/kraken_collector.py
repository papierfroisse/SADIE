"""Module de collecte des trades Kraken."""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import krakenex
from pykrakenapi import KrakenAPI
import websockets
import json
from websockets.exceptions import ConnectionClosed, ConnectionClosedError, ConnectionClosedOK
import random

from sadie.data.collectors.base import BaseCollector

logger = logging.getLogger(__name__)

class KrakenTradeCollector(BaseCollector):
    """Collecteur de trades Kraken avec gestion avancée des erreurs et de la sécurité."""
    
    def __init__(
        self,
        name: str,
        symbols: List[str],
        storage: Optional[object] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: int = 5,
        update_interval: float = 1.0,
        connection_timeout: int = 15,
        logger: Optional[logging.Logger] = None
    ):
        """Initialisation du collecteur.
        
        Args:
            name: Nom du collecteur
            symbols: Liste des symboles (ex: ["XBT/USD", "ETH/USD"])
            storage: Stockage des données
            api_key: Clé API Kraken
            api_secret: Secret API Kraken
            max_retries: Nombre maximum de tentatives de reconnexion
            retry_delay: Délai entre les tentatives en secondes
            update_interval: Intervalle de mise à jour en secondes
            connection_timeout: Timeout de connexion en secondes
            logger: Logger optionnel
        """
        # Initialisation de la classe parente
        super().__init__(name, symbols, update_interval, logger)
        
        # Propriétés spécifiques à Kraken
        self.storage = storage
        self.api_key = api_key
        self.api_secret = api_secret
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection_timeout = connection_timeout
        
        # Conversion des symboles au format Kraken
        self.kraken_symbols = [s.replace("/", "") for s in symbols]
        
        # État de la connexion
        self.kraken = None
        self.ws = None
        self.subscription_status = {}
        self.last_trade = None
        self.last_heartbeat = 0
        self.consecutive_errors = 0
        self.ws_reconnect_count = 0
        self.ping_task = None
        
    async def start(self):
        """Démarre la collecte des trades."""
        logger.info(f"Démarrage du collecteur Kraken {self.name}")
        await super().start()
            
    async def stop(self):
        """Arrête la collecte des trades."""
        if not self._running:
            return
            
        logger.info(f"Arrêt du collecteur Kraken {self.name}")
        
        # Annulation de la tâche de ping
        if self.ping_task:
            self.ping_task.cancel()
            try:
                await self.ping_task
            except asyncio.CancelledError:
                pass
        
        # Fermeture de la connexion WebSocket
        if self.ws:
            try:
                await self.ws.close()
            except Exception as e:
                logger.warning(f"Erreur lors de la fermeture du WebSocket: {e}")
            self.ws = None
            
        # Arrêt de la classe parente (annule la tâche principale)
        await super().stop()
        logger.info(f"Collecteur Kraken {self.name} arrêté") 
            
    async def _run(self):
        """Méthode principale d'exécution du collecteur."""
        try:
            # S'assurer que la connexion est établie
            if not self.kraken:
                await self._connect_api()
                
            if not self.ws or self.ws.closed:
                await self._connect_websocket()
                self.ping_task = asyncio.create_task(self._keep_alive())
                
            # Vérifier l'état de santé de la connexion
            if time.time() - self.last_heartbeat > 30:  # Plus de 30s sans message
                logger.warning(f"Pas de données reçues depuis 30s, reconnexion WebSocket")
                await self._reconnect_websocket()
                return
                
            # Traitement des messages
            try:
                message = await asyncio.wait_for(
                    self.ws.recv(), 
                    timeout=self.connection_timeout
                )
                self.last_heartbeat = time.time()
                self.consecutive_errors = 0  # Réinitialisation du compteur d'erreurs
                
                # Traitement des données
                await self._process_message(message)
                    
            except asyncio.TimeoutError:
                logger.warning(f"Timeout en attente de message WebSocket")
                # Une notification occasionnelle est normale, pas besoin de reconnecter immédiatement
                pass
                
        except ConnectionClosed as e:
            self.consecutive_errors += 1
            logger.warning(f"Connexion WebSocket fermée: {e}, tentative de reconnexion ({self.consecutive_errors}/{self.max_retries})")
            await self._reconnect_websocket()
            
        except Exception as e:
            self.consecutive_errors += 1
            logger.error(f"Erreur dans l'exécution du collecteur: {e}")
            
            if self.consecutive_errors >= self.max_retries:
                logger.warning(f"Trop d'erreurs consécutives ({self.consecutive_errors}), reconnexion complète")
                await self._reconnect_full()
            else:
                # Pause progressive avant nouvelle tentative
                delay = min(60, self.retry_delay * (1 + self.consecutive_errors))
                await asyncio.sleep(delay)
                    
    async def _keep_alive(self):
        """Maintient la connexion WebSocket active."""
        while self._running and self.ws:
            try:
                # Envoi d'un ping toutes les 30 secondes
                if self.ws and not self.ws.closed:
                    ping_message = {"op": "ping"}
                    await self.ws.send(json.dumps(ping_message))
                    logger.debug("Ping envoyé à Kraken WebSocket")
            except Exception as e:
                logger.warning(f"Erreur lors de l'envoi du ping: {e}")
                
            # Attente avant le prochain ping
            await asyncio.sleep(30)
                
    async def _connect_api(self):
        """Établit la connexion à l'API REST Kraken."""
        logger.info("Connexion à l'API REST Kraken")
        retries = 0
        
        while retries < self.max_retries:
            try:
                # Connexion à l'API REST
                api = krakenex.API(key=self.api_key, secret=self.api_secret)
                self.kraken = KrakenAPI(api)
                
                # Vérification de la connexion
                self.kraken.get_server_time()
                logger.info("Connexion à l'API Kraken établie avec succès")
                return
                
            except Exception as e:
                retries += 1
                logger.error(f"Erreur de connexion à l'API Kraken: {str(e)}")
                
                if retries >= self.max_retries:
                    raise
                else:
                    # Attente avec backoff exponentiel
                    delay = self.retry_delay * (2 ** (retries - 1))
                    logger.info(f"Nouvelle tentative de connexion dans {delay}s ({retries}/{self.max_retries})")
                    await asyncio.sleep(delay)
                    
        raise ConnectionError("Impossible de se connecter à l'API Kraken après plusieurs tentatives")
            
    async def _connect_websocket(self):
        """Établit la connexion WebSocket à Kraken."""
        websocket_url = "wss://ws.kraken.com"
        logger.info(f"Connexion au WebSocket Kraken: {websocket_url}")
        
        try:
            # Fermeture de l'ancienne connexion si elle existe
            if self.ws and not self.ws.closed:
                await self.ws.close()
                
            # Nouvelle connexion
            self.ws = await websockets.connect(
                websocket_url,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=5
            )
            
            # Souscription aux canaux de trades
            subscribe_message = {
                "name": "subscribe",
                "reqid": int(time.time() * 1000),  # Identifiant unique
                "pair": self.kraken_symbols,
                "subscription": {
                    "name": "trade"
                }
            }
            
            logger.debug(f"Envoi de la souscription: {subscribe_message}")
            await self.ws.send(json.dumps(subscribe_message))
            
            # Attente des messages de confirmation
            confirmation_count = 0
            max_wait = 10  # Attente maximale de 10 secondes
            start_time = time.time()
            
            while time.time() - start_time < max_wait and confirmation_count < len(self.kraken_symbols):
                try:
                    response = await asyncio.wait_for(self.ws.recv(), timeout=5)
                    data = json.loads(response)
                    
                    # Traitement des réponses de souscription
                    if isinstance(data, dict) and data.get("event") == "subscriptionStatus":
                        pair = data.get("pair", "")
                        status = data.get("status", "")
                        
                        if status == "subscribed":
                            confirmation_count += 1
                            logger.info(f"Souscription confirmée pour {pair}")
                            self.subscription_status[pair] = True
                        elif status == "error":
                            logger.error(f"Erreur de souscription pour {pair}: {data.get('errorMessage', 'Inconnu')}")
                            self.subscription_status[pair] = False
                            
                except asyncio.TimeoutError:
                    logger.warning("Timeout en attente de confirmation de souscription")
                    break
                    
            self.last_heartbeat = time.time()
            logger.info(f"Connexion WebSocket établie avec {confirmation_count} souscriptions confirmées")
            
            # Si aucune souscription n'a été confirmée, lever une exception
            if confirmation_count == 0:
                raise ConnectionError("Aucune souscription confirmée")
                
            # Réinitialisation du compteur de reconnexions en cas de succès
            self.ws_reconnect_count = 0
                
        except Exception as e:
            logger.error(f"Erreur lors de la connexion WebSocket: {str(e)}")
            raise
            
    async def _reconnect_websocket(self):
        """Reconnecte le WebSocket en cas de perte de connexion."""
        self.ws_reconnect_count += 1
        
        # Calcul du délai avec jitter pour éviter les tempêtes de reconnexion
        jitter = random.uniform(0, 1)
        delay = min(60, self.retry_delay * (2 ** min(self.ws_reconnect_count - 1, 4)) + jitter)
        
        logger.info(f"Tentative de reconnexion WebSocket dans {delay:.2f}s ({self.ws_reconnect_count})")
        await asyncio.sleep(delay)
        
        try:
            await self._connect_websocket()
        except Exception as e:
            logger.error(f"Échec de la reconnexion WebSocket: {e}")
            # La prochaine itération de _run() tentera une nouvelle connexion
            
    async def _reconnect_full(self):
        """Effectue une reconnexion complète (API + WebSocket)."""
        logger.warning("Reconnexion complète du collecteur Kraken")
        
        # Fermeture des connexions existantes
        if self.ws and not self.ws.closed:
            try:
                await self.ws.close()
            except:
                pass
        self.ws = None
        self.kraken = None
        
        # Réinitialisation des compteurs
        self.consecutive_errors = 0
        self.ws_reconnect_count = 0
        
        # Nouvelle connexion
        try:
            await self._connect_api()
            await self._connect_websocket()
            logger.info("Reconnexion complète réussie")
        except Exception as e:
            logger.error(f"Échec de la reconnexion complète: {e}")
            # La prochaine itération de _run() tentera une nouvelle connexion
            
    async def _process_message(self, message):
        """Traite un message WebSocket reçu."""
        try:
            data = json.loads(message)
            
            # Les messages de heartbeat
            if isinstance(data, dict) and data.get("event") == "heartbeat":
                logger.debug("Heartbeat reçu de Kraken")
                return
                
            # Les messages de trades
            if isinstance(data, list) and len(data) > 1:
                pair = data[-1]  # Dernier élément = paire
                trades = data[1]  # Deuxième élément = liste de trades
                
                if not trades:
                    return
                    
                for trade in trades:
                    # Format Kraken: [price, volume, time, side, type, misc]
                    if len(trade) >= 6:  # Vérification de la structure
                        self.last_trade = trade
                        
                        # Mise à jour des données internes
                        symbol = self._get_original_symbol(pair)
                        if symbol in self._data:
                            self._data[symbol]["price"] = float(trade[0])
                            self._data[symbol]["volume"] = float(trade[1])
                            self._data[symbol]["high"] = max(self._data[symbol]["high"], float(trade[0]))
                            self._data[symbol]["low"] = min(self._data[symbol]["low"], float(trade[0]))
                            self._data[symbol]["timestamp"] = float(trade[2])
                            self._data[symbol]["side"] = "buy" if trade[3] == "b" else "sell"
                        
                        # Stockage des données si un stockage est configuré
                        if self.storage:
                            trade_data = {
                                "symbol": symbol,
                                "price": float(trade[0]),
                                "amount": float(trade[1]),
                                "timestamp": datetime.fromtimestamp(float(trade[2])).isoformat(),
                                "side": "buy" if trade[3] == "b" else "sell",
                                "trade_id": f"{pair}-{trade[2]}-{trade[0]}-{trade[1]}"
                            }
                            try:
                                await self.storage.store_trade(symbol, trade_data)
                                logger.debug(f"Trade stocké pour {symbol}")
                            except Exception as e:
                                logger.error(f"Erreur lors du stockage du trade: {e}")
                        
        except json.JSONDecodeError:
            logger.warning(f"Message invalide reçu: {message[:100]}...")
        except Exception as e:
            logger.error(f"Erreur de traitement du message: {e}")
            
    def _get_original_symbol(self, kraken_symbol: str) -> str:
        """Convertit un symbole format Kraken en format original.
        
        Args:
            kraken_symbol: Symbole au format Kraken (ex: XBTUSD)
            
        Returns:
            Symbole au format d'origine (ex: XBT/USD)
        """
        # Recherche du symbole d'origine correspondant au format Kraken
        for orig, kraken in zip(self.symbols, self.kraken_symbols):
            if kraken == kraken_symbol:
                return orig
                
        # Si pas trouvé, tentative de reconstruction
        if len(kraken_symbol) >= 6:
            return f"{kraken_symbol[:3]}/{kraken_symbol[3:]}"
        else:
            return kraken_symbol
            
    async def get_historical_trades(self, symbol: str, since: Optional[int] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """Récupère les trades historiques pour un symbole.
        
        Args:
            symbol: Symbole au format d'origine (ex: XBT/USD)
            since: Timestamp de départ (optionnel)
            limit: Nombre maximum de trades à récupérer
            
        Returns:
            Liste des trades historiques
        """
        if not self.kraken:
            await self._connect_api()
            
        kraken_symbol = symbol.replace("/", "")
        retries = 0
        
        while retries < self.max_retries:
            try:
                trades, last = self.kraken.get_recent_trades(
                    pair=kraken_symbol,
                    since=since,
                    count=limit
                )
                
                # Conversion du format
                result = []
                for idx, row in trades.iterrows():
                    trade = {
                        "symbol": symbol,
                        "price": float(row["price"]),
                        "volume": float(row["volume"]),
                        "timestamp": int(row["time"].timestamp() * 1000),
                        "side": "buy" if row["buy_sell"] == "b" else "sell",
                        "market_limit": "market" if row["market_limit"] == "m" else "limit",
                        "trade_id": f"{symbol}-{int(row['time'].timestamp())}-{idx}"
                    }
                    result.append(trade)
                    
                return result
                
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des trades historiques pour {symbol}: {e}")
                retries += 1
                
                if retries >= self.max_retries:
                    raise
                    
                await asyncio.sleep(self.retry_delay * (2 ** (retries - 1)))
                
        return [] 