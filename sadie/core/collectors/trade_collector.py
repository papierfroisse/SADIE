"""Module de collecte des trades."""

import asyncio
import logging
import os
import time
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta

import pandas as pd
from binance import AsyncClient
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

# Configuration du logging
logger = logging.getLogger(__name__)

class BinanceTradeCollector:
    """Collecteur de trades depuis Binance."""

    def __init__(
        self, 
        symbol: str, 
        api_key: Optional[str] = None, 
        api_secret: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: int = 5,
        connection_timeout: int = 10
    ):
        """Initialisation du collecteur.
        
        Args:
            symbol: Le symbole à collecter (ex: BTCUSDT)
            api_key: Clé API Binance (optionnelle)
            api_secret: Secret API Binance (optionnel)
            max_retries: Nombre maximum de tentatives en cas d'erreur
            retry_delay: Délai entre les tentatives en secondes
            connection_timeout: Timeout de connexion en secondes
        """
        self.symbol = symbol
        self.api_key = api_key
        self.api_secret = api_secret
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection_timeout = connection_timeout
        
        self.client = None
        self._running = False
        self._last_update = None
        self._trades = []
        self._callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self._collection_task = None
        self._rate_limit_hits = 0
        self._consecutive_errors = 0
        
    def add_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Ajoute une fonction de callback pour les trades en temps réel."""
        self._callbacks.append(callback)
        
    async def start(self):
        """Démarre la collecte des trades."""
        if self._running:
            logger.warning(f"Le collecteur pour {self.symbol} est déjà en cours d'exécution")
            return
            
        try:
            self.client = await AsyncClient.create(
                api_key=self.api_key,
                api_secret=self.api_secret,
                requests_params={'timeout': self.connection_timeout}
            )
            self._running = True
            
            # Démarrage de la collecte en temps réel
            self._collection_task = asyncio.create_task(self._collect_trades())
            logger.info(f"Collecteur démarré pour {self.symbol}")
            
        except Exception as e:
            logger.error(f"Erreur lors du démarrage du collecteur pour {self.symbol}: {str(e)}")
            if self.client:
                await self.client.close_connection()
                self.client = None
            raise
        
    async def stop(self):
        """Arrête la collecte des trades."""
        if not self._running:
            return
            
        self._running = False
        
        # Annulation de la tâche de collecte si elle existe
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
            self._collection_task = None
            
        # Fermeture de la connexion client
        if self.client:
            try:
                await self.client.close_connection()
            except Exception as e:
                logger.warning(f"Erreur lors de la fermeture de la connexion: {str(e)}")
            finally:
                self.client = None
                
        logger.info(f"Collecteur arrêté pour {self.symbol}")
        
    async def _collect_trades(self):
        """Collecte les trades en temps réel."""
        while self._running:
            try:
                # Limitation du débit des requêtes en cas d'erreurs fréquentes
                if self._rate_limit_hits > 0:
                    delay = min(60, self.retry_delay * (2 ** (self._rate_limit_hits - 1)))
                    logger.warning(f"Attente de {delay}s suite à des limites de débit")
                    await asyncio.sleep(delay)
                    self._rate_limit_hits = max(0, self._rate_limit_hits - 1)
                
                # Récupération des trades récents
                trades = await self.client.get_recent_trades(symbol=self.symbol)
                self._consecutive_errors = 0  # Réinitialisation du compteur d'erreurs
                
                for trade_data in trades:
                    trade = {
                        'symbol': self.symbol,
                        'price': float(trade_data['price']),
                        'quantity': float(trade_data['qty']),
                        'timestamp': trade_data['time'],
                        'buyer_order_id': trade_data.get('buyer_order_id', ''),
                        'seller_order_id': trade_data.get('seller_order_id', ''),
                        'trade_id': str(trade_data['id']),
                        'buyer_is_maker': trade_data.get('is_buyer_maker', False),
                        'is_best_match': trade_data.get('is_best_match', True)
                    }
                    
                    # Ajout du trade à la liste
                    self._trades.append(trade)
                    # Limitation de la taille de la liste à 1000 trades
                    if len(self._trades) > 1000:
                        self._trades.pop(0)
                    
                    # Exécution des callbacks
                    for callback in self._callbacks:
                        try:
                            callback(trade)
                        except Exception as e:
                            logger.error(f"Erreur dans le callback: {e}")
                            
                # Mise à jour du timestamp de dernière mise à jour
                self._last_update = time.time()
                
                # Attente avant la prochaine requête
                await asyncio.sleep(1)  # Attente d'une seconde entre les requêtes
                    
            except BinanceAPIException as e:
                self._consecutive_errors += 1
                
                if e.code == -1003:  # Trop de requêtes
                    self._rate_limit_hits += 1
                    logger.warning(f"Limite de débit atteinte: {e}")
                else:
                    logger.error(f"Erreur API Binance pour {self.symbol}: {e}")
                
                if not self._running:
                    break
                
                await asyncio.sleep(self.retry_delay)
                
            except BinanceRequestException as e:
                self._consecutive_errors += 1
                logger.error(f"Erreur de requête Binance pour {self.symbol}: {e}")
                
                if not self._running:
                    break
                
                # Augmentation du délai de nouvelle tentative en fonction du nombre d'erreurs consécutives
                delay = min(60, self.retry_delay * (2 ** min(self._consecutive_errors - 1, 5)))
                logger.info(f"Nouvelle tentative dans {delay}s...")
                await asyncio.sleep(delay)
                
            except asyncio.CancelledError:
                logger.info(f"Tâche de collecte annulée pour {self.symbol}")
                break
                
            except Exception as e:
                self._consecutive_errors += 1
                logger.error(f"Erreur inattendue lors de la collecte des trades pour {self.symbol}: {e}")
                
                if not self._running:
                    break
                
                # Si trop d'erreurs consécutives, arrêt temporaire puis redémarrage
                if self._consecutive_errors >= self.max_retries:
                    logger.warning(f"Trop d'erreurs consécutives, redémarrage du client pour {self.symbol}")
                    if self.client:
                        try:
                            await self.client.close_connection()
                        except:
                            pass
                        
                    try:
                        self.client = await AsyncClient.create(
                            api_key=self.api_key,
                            api_secret=self.api_secret,
                            requests_params={'timeout': self.connection_timeout}
                        )
                        self._consecutive_errors = 0
                    except Exception as create_error:
                        logger.error(f"Échec du redémarrage du client pour {self.symbol}: {create_error}")
                        
                # Pause avant nouvelle tentative
                await asyncio.sleep(self.retry_delay)
                    
    async def get_trades(self, limit: int = 1000) -> pd.DataFrame:
        """Récupère les trades récents.
        
        Args:
            limit: Nombre maximum de trades à récupérer
            
        Returns:
            DataFrame contenant les trades
            
        Raises:
            BinanceAPIException: En cas d'erreur de l'API Binance
            ConnectionError: En cas d'erreur de connexion
        """
        if not self.client:
            raise ConnectionError("Le client Binance n'est pas initialisé")
            
        retries = 0
        while retries < self.max_retries:
            try:
                trades = await self.client.get_historical_trades(
                    symbol=self.symbol,
                    limit=limit
                )
                
                df = pd.DataFrame(trades)
                df['time'] = pd.to_datetime(df['time'], unit='ms')
                df['price'] = df['price'].astype(float)
                df['qty'] = df['qty'].astype(float)
                
                return df
                
            except BinanceAPIException as e:
                if e.code == -1003:  # Trop de requêtes
                    logger.warning(f"Limite de débit atteinte: {e}")
                    await asyncio.sleep(self.retry_delay * (2 ** retries))
                else:
                    logger.error(f"Erreur API Binance lors de la récupération des trades: {e}")
                    raise
                    
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des trades: {e}")
                retries += 1
                if retries >= self.max_retries:
                    raise
                await asyncio.sleep(self.retry_delay)
        
        # Ne devrait jamais atteindre ce point grâce au raise dans la boucle
        raise ConnectionError("Échec de la récupération des trades après plusieurs tentatives")
        
    async def get_klines(self, interval: str = '1m', limit: int = 1000) -> pd.DataFrame:
        """Récupère les bougies (klines).
        
        Args:
            interval: Intervalle des bougies ('1m', '5m', '1h', etc.)
            limit: Nombre maximum de bougies à récupérer
            
        Returns:
            DataFrame contenant les bougies
        """
        if not self.client:
            raise ConnectionError("Le client Binance n'est pas initialisé")
            
        retries = 0
        while retries < self.max_retries:
            try:
                klines = await self.client.get_klines(
                    symbol=self.symbol,
                    interval=interval,
                    limit=limit
                )
                
                df = pd.DataFrame(klines, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                    'taker_buy_quote', 'ignore'
                ])
                
                # Conversion des types
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = df[col].astype(float)
                    
                return df
                
            except BinanceAPIException as e:
                if e.code == -1003:  # Trop de requêtes
                    logger.warning(f"Limite de débit atteinte: {e}")
                    await asyncio.sleep(self.retry_delay * (2 ** retries))
                else:
                    logger.error(f"Erreur API Binance lors de la récupération des klines: {e}")
                    raise
                    
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des klines: {e}")
                retries += 1
                if retries >= self.max_retries:
                    raise
                await asyncio.sleep(self.retry_delay)
                
        # Ne devrait jamais atteindre ce point grâce au raise dans la boucle
        raise ConnectionError("Échec de la récupération des klines après plusieurs tentatives")