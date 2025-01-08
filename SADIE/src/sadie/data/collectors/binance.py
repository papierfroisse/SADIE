"""
Collecteur de données pour l'API Binance.
"""

import datetime
from typing import Dict, List, Optional, Union

from binance.client import Client

from sadie.data.collectors import DataCollector

class BinanceDataCollector(DataCollector):
    """Collecteur de données utilisant l'API Binance."""
    
    INTERVAL_MAP = {
        "1m": Client.KLINE_INTERVAL_1MINUTE,
        "3m": Client.KLINE_INTERVAL_3MINUTE,
        "5m": Client.KLINE_INTERVAL_5MINUTE,
        "15m": Client.KLINE_INTERVAL_15MINUTE,
        "30m": Client.KLINE_INTERVAL_30MINUTE,
        "1h": Client.KLINE_INTERVAL_1HOUR,
        "2h": Client.KLINE_INTERVAL_2HOUR,
        "4h": Client.KLINE_INTERVAL_4HOUR,
        "6h": Client.KLINE_INTERVAL_6HOUR,
        "8h": Client.KLINE_INTERVAL_8HOUR,
        "12h": Client.KLINE_INTERVAL_12HOUR,
        "1d": Client.KLINE_INTERVAL_1DAY,
        "3d": Client.KLINE_INTERVAL_3DAY,
        "1w": Client.KLINE_INTERVAL_1WEEK,
        "1M": Client.KLINE_INTERVAL_1MONTH
    }
    
    def _initialize_client(self) -> None:
        """Initialise le client Binance."""
        self.client = Client(self.api_key, self.api_secret)
    
    def _format_symbol(self, symbol: str) -> str:
        """
        Formate le symbole pour l'API Binance.
        
        Args:
            symbol: Symbole au format "BTC/USDT"
            
        Returns:
            Symbole au format "BTCUSDT"
        """
        return symbol.replace("/", "")
    
    def get_historical_data(
        self,
        symbol: str,
        interval: str,
        start_time: datetime.datetime,
        end_time: Optional[datetime.datetime] = None
    ) -> List[Dict[str, Union[float, int]]]:
        """
        Récupère les données historiques depuis Binance.
        
        Args:
            symbol: Symbole de la paire de trading (ex: "BTC/USDT")
            interval: Intervalle de temps (ex: "1h", "1d")
            start_time: Date de début
            end_time: Date de fin (optionnel, par défaut jusqu'à maintenant)
            
        Returns:
            Liste de dictionnaires contenant les données OHLCV
        
        Raises:
            ValueError: Si l'intervalle n'est pas supporté
        """
        if interval not in self.INTERVAL_MAP:
            raise ValueError(f"Intervalle non supporté: {interval}")
        
        binance_symbol = self._format_symbol(symbol)
        binance_interval = self.INTERVAL_MAP[interval]
        
        klines = self.client.get_historical_klines(
            symbol=binance_symbol,
            interval=binance_interval,
            start_str=int(start_time.timestamp() * 1000),
            end_str=int(end_time.timestamp() * 1000) if end_time else None
        )
        
        return [
            {
                "timestamp": kline[0] / 1000,  # Conversion en secondes
                "open": float(kline[1]),
                "high": float(kline[2]),
                "low": float(kline[3]),
                "close": float(kline[4]),
                "volume": float(kline[5]),
                "close_time": kline[6] / 1000,
                "quote_volume": float(kline[7]),
                "trades": int(kline[8]),
                "taker_buy_base": float(kline[9]),
                "taker_buy_quote": float(kline[10])
            }
            for kline in klines
        ]
    
    def get_current_price(self, symbol: str) -> float:
        """
        Récupère le prix actuel depuis Binance.
        
        Args:
            symbol: Symbole de la paire de trading (ex: "BTC/USDT")
            
        Returns:
            Prix actuel
        """
        binance_symbol = self._format_symbol(symbol)
        ticker = self.client.get_symbol_ticker(symbol=binance_symbol)
        return float(ticker["price"])
    
    def get_order_book(
        self,
        symbol: str,
        limit: Optional[int] = None
    ) -> Dict[str, Union[int, List[List[float]]]]:
        """
        Récupère le carnet d'ordres depuis Binance.
        
        Args:
            symbol: Symbole de la paire de trading (ex: "BTC/USDT")
            limit: Nombre maximum d'ordres à récupérer (optionnel)
            
        Returns:
            Dictionnaire contenant le carnet d'ordres
        """
        binance_symbol = self._format_symbol(symbol)
        depth = self.client.get_order_book(
            symbol=binance_symbol,
            limit=limit
        )
        
        return {
            "timestamp": depth["lastUpdateId"],
            "bids": [[float(price), float(qty)] for price, qty in depth["bids"]],
            "asks": [[float(price), float(qty)] for price, qty in depth["asks"]]
        } 