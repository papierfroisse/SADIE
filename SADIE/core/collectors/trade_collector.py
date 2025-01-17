"""
Module de collecte des données de trades depuis les exchanges.
"""

import asyncio
import ccxt.async_support as ccxt
import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from collections import deque
import logging
from concurrent.futures import ThreadPoolExecutor
import time

from SADIE.core.models.events import Exchange, Symbol, Timeframe, Trade
from ..cache.redis_cache import RedisCache
from ..metrics import (
    TRADES_PROCESSED,
    TRADE_PROCESSING_TIME,
    TRADE_BUFFER_SIZE,
    ERRORS,
    NETWORK_LATENCY,
    NETWORK_ERRORS,
    MEMORY_USAGE,
    CPU_USAGE
)

logger = logging.getLogger(__name__)

class TradeCollector:
    """Collecteur de données de trades avec optimisation mémoire et performances."""
    
    def __init__(
        self,
        name: str,
        symbols: List[str],
        max_trades_per_symbol: int = 10000,
        connection_pool_size: int = 5,
        cache_enabled: bool = True,
        cache_host: str = "localhost",
        cache_port: int = 6379,
        cache_db: int = 0,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """Initialise le collecteur avec des paramètres optimisés.
        
        Args:
            name: Nom du collecteur
            symbols: Liste des symboles à collecter
            max_trades_per_symbol: Nombre maximum de trades par symbole en mémoire
            connection_pool_size: Taille du pool de connexions
            cache_enabled: Active le cache Redis
            cache_host: Hôte Redis
            cache_port: Port Redis
            cache_db: Base de données Redis
            max_retries: Nombre maximum de tentatives de reconnexion
            retry_delay: Délai initial entre les tentatives (en secondes)
        """
        self.name = name
        self.symbols = symbols
        self.exchanges: Dict[str, Any] = {}
        self.trades_buffer: Dict[str, deque] = {}
        self.max_trades_per_symbol = max_trades_per_symbol
        self.connection_pool = ThreadPoolExecutor(max_workers=connection_pool_size)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._retry_counts: Dict[str, int] = {}
        self._buffer_locks: Dict[str, asyncio.Lock] = {}
        
        if cache_enabled:
            try:
                self.cache = RedisCache(
                    host=cache_host,
                    port=cache_port,
                    db=cache_db,
                    prefix=f"trades:{self.name}:"
                )
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation du cache: {str(e)}")
                self.cache = None
        else:
            self.cache = None
        
        self._connection_semaphore = asyncio.Semaphore(connection_pool_size)
        
        self._setup_metrics_labels()
        
    def _setup_metrics_labels(self):
        """Setup common labels for metrics."""
        self.labels = {'exchange': self.name}
        for symbol in self.symbols:
            TRADE_BUFFER_SIZE.labels(exchange=self.name, symbol=symbol).set(0)
        
    async def connect(self, exchange_id: str = "binance") -> None:
        """Connecte à un exchange avec gestion des erreurs et retry.
        
        Args:
            exchange_id: Identifiant de l'exchange
        """
        if exchange_id not in self.exchanges:
            async with self._connection_semaphore:
                retry_count = 0
                last_error = None
                
                while retry_count < self.max_retries:
                    try:
                        start_time = time.time()
                        exchange_class = getattr(ccxt, exchange_id)
                        self.exchanges[exchange_id] = exchange_class({
                            'enableRateLimit': True,
                            'timeout': 30000,
                            'enableLastTradesCache': True,
                            'verbose': False
                        })
                        logger.info(f"Connecté à l'exchange {exchange_id}")
                        self._retry_counts[exchange_id] = 0
                        NETWORK_LATENCY.labels(exchange=exchange_id, endpoint='connect').observe(
                            time.time() - start_time
                        )
                        return
                        
                    except Exception as e:
                        retry_count += 1
                        self._retry_counts[exchange_id] = retry_count
                        last_error = e
                        
                        if retry_count < self.max_retries:
                            delay = self.retry_delay * (2 ** (retry_count - 1))
                            logger.warning(
                                f"Tentative {retry_count}/{self.max_retries} "
                                f"échouée pour {exchange_id}: {str(e)}. "
                                f"Nouvelle tentative dans {delay:.1f}s"
                            )
                            await asyncio.sleep(delay)
                        else:
                            logger.error(
                                f"Échec de connexion à {exchange_id} "
                                f"après {self.max_retries} tentatives: {str(e)}"
                            )
                            NETWORK_ERRORS.labels(exchange=exchange_id, type='connect').inc()
                            ERRORS.labels(type='connection', exchange=exchange_id).inc()
                            
                if last_error:
                    raise last_error
            
    async def disconnect(self) -> None:
        """Déconnecte proprement de tous les exchanges."""
        try:
            for exchange in self.exchanges.values():
                try:
                    await exchange.close()
                except Exception as e:
                    logger.warning(f"Erreur lors de la fermeture d'un exchange: {str(e)}")
                    
            self.exchanges.clear()
            self.connection_pool.shutdown(wait=True)
            logger.info("Déconnexion propre effectuée")
            
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion: {str(e)}")
            raise
            
    def _init_symbol_buffer(self, symbol: str) -> None:
        """Initialise le buffer pour un symbole."""
        if symbol not in self.trades_buffer:
            self.trades_buffer[symbol] = deque(maxlen=self.max_trades_per_symbol)
            self._buffer_locks[symbol] = asyncio.Lock()
            
    def _get_buffer_lock(self, symbol: str) -> asyncio.Lock:
        """Retourne le verrou pour un symbole, en le créant si nécessaire."""
        if symbol not in self._buffer_locks:
            self._buffer_locks[symbol] = asyncio.Lock()
        return self._buffer_locks[symbol]
            
    async def get_historical_data(
        self,
        exchange: Exchange,
        symbol: Symbol,
        timeframe: Timeframe,
        limit: int = 1000,
        since: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Récupère les données historiques avec cache et optimisation.
        
        Args:
            exchange: Exchange à utiliser
            symbol: Symbole à récupérer
            timeframe: Timeframe des données
            limit: Nombre de bougies à récupérer
            since: Date de début (optionnel)
            
        Returns:
            DataFrame avec les données OHLCV
        """
        cache_key = f"{exchange.value}_{symbol.value}_{timeframe.value}_{limit}_{since}"
        
        # Vérifier le cache
        if self.cache:
            try:
                cached_data = await self.cache.get(cache_key)
                if cached_data is not None:
                    logger.debug(f"Données trouvées dans le cache pour {cache_key}")
                    return pd.DataFrame(cached_data)
            except Exception as e:
                logger.warning(f"Erreur lors de la lecture du cache: {str(e)}")
        
        retry_count = 0
        last_error = None
        
        while retry_count < self.max_retries:
            try:
                # Connexion si nécessaire
                await self.connect(exchange.value)
                exchange_instance = self.exchanges[exchange.value]
                
                # Chargement des marchés si nécessaire
                if not exchange_instance.markets:
                    await exchange_instance.load_markets()
                    
                # Récupération des données
                ohlcv = await exchange_instance.fetch_ohlcv(
                    symbol=symbol.value,
                    timeframe=timeframe.value,
                    limit=limit,
                    since=int(since.timestamp() * 1000) if since else None
                )
                
                # Conversion en DataFrame optimisée
                df = pd.DataFrame(
                    ohlcv,
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                
                # Optimisation des types de données
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = pd.to_numeric(df[col], downcast='float')
                
                df.set_index('timestamp', inplace=True)
                
                # Mise en cache
                if self.cache:
                    try:
                        await self.cache.set(cache_key, df.to_dict('records'), expire=3600)
                    except Exception as e:
                        logger.warning(f"Erreur lors de l'écriture dans le cache: {str(e)}")
                
                return df
                
            except Exception as e:
                retry_count += 1
                last_error = e
                
                if retry_count < self.max_retries:
                    delay = self.retry_delay * (2 ** (retry_count - 1))
                    logger.warning(
                        f"Tentative {retry_count}/{self.max_retries} "
                        f"échouée: {str(e)}. "
                        f"Nouvelle tentative dans {delay:.1f}s"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"Échec de récupération des données "
                        f"après {self.max_retries} tentatives: {str(e)}"
                    )
                    
        if last_error:
            raise last_error
            
    async def process_trade(self, symbol: str, trade: Dict[str, Any]) -> None:
        """Traite un nouveau trade avec gestion optimisée de la mémoire.
        
        Args:
            symbol: Symbole du trade
            trade: Données du trade
            
        Raises:
            KeyError: Si le trade ne contient pas les champs requis
            ValueError: Si les données du trade sont invalides
        """
        try:
            start_time = time.time()
            
            # Validation des champs requis
            required_fields = ["trade_id", "symbol", "price", "amount", "side", "timestamp"]
            for field in required_fields:
                if field not in trade:
                    raise KeyError(f"Champ requis manquant : {field}")
            
            # Validation du timestamp
            timestamp = datetime.fromisoformat(trade["timestamp"])
            
            self._init_symbol_buffer(symbol)
            
            # Acquisition du verrou pour le symbole
            async with self._get_buffer_lock(symbol):
                # Ajout du trade au buffer
                self.trades_buffer[symbol].append(trade)
                
                # Tri du buffer par timestamp
                trades_list = list(self.trades_buffer[symbol])
                trades_list.sort(key=lambda x: datetime.fromisoformat(x["timestamp"]))
                self.trades_buffer[symbol].clear()
                self.trades_buffer[symbol].extend(trades_list)
            
            # Mise en cache si activé
            if self.cache:
                try:
                    cache_key = f"latest_trade:{symbol}"
                    await self.cache.set(cache_key, trade, expire=3600)
                except Exception as e:
                    logger.warning(f"Erreur lors de la mise en cache du trade: {str(e)}")
                    
            # Update metrics
            TRADES_PROCESSED.labels(exchange=self.name, symbol=symbol).inc()
            TRADE_PROCESSING_TIME.labels(exchange=self.name, symbol=symbol).observe(
                time.time() - start_time
            )
            TRADE_BUFFER_SIZE.labels(exchange=self.name, symbol=symbol).set(
                len(self.trades_buffer[symbol])
            )

        except Exception as e:
            ERRORS.labels(type='processing', exchange=self.name).inc()
            logger.error(f"Erreur lors du traitement du trade: {str(e)}")
            raise
        
    def get_trades(self, symbol: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Récupère les trades en mémoire pour un symbole.
        
        Args:
            symbol: Symbole des trades
            limit: Nombre maximum de trades à retourner
            
        Returns:
            Liste des trades
        """
        if symbol not in self.trades_buffer:
            return []
        
        trades = list(self.trades_buffer[symbol])
        if limit:
            return trades[-limit:]
        return trades 