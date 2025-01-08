"""
Collecteur de données pour l'API Alpha Vantage.
"""

import datetime
from typing import Dict, List, Optional, Union

from alpha_vantage.cryptocurrencies import CryptoCurrencies
from alpha_vantage.timeseries import TimeSeries

from sadie.data.collectors import DataCollector

class AlphaVantageDataCollector(DataCollector):
    """Collecteur de données utilisant l'API Alpha Vantage."""
    
    INTERVAL_MAP = {
        "1m": "1min",
        "5m": "5min",
        "15m": "15min",
        "30m": "30min",
        "1h": "60min",
        "1d": "daily",
        "1w": "weekly",
        "1M": "monthly"
    }
    
    def _initialize_client(self) -> None:
        """Initialise les clients Alpha Vantage."""
        self.crypto_client = CryptoCurrencies(key=self.api_key)
        self.ts_client = TimeSeries(key=self.api_key)
    
    def _format_symbol(self, symbol: str) -> str:
        """
        Formate le symbole pour l'API Alpha Vantage.
        
        Args:
            symbol: Symbole au format "BTC/USDT"
            
        Returns:
            Symbole au format "BTC"
        """
        return symbol.split("/")[0]
    
    def get_historical_data(
        self,
        symbol: str,
        interval: str,
        start_time: datetime.datetime,
        end_time: Optional[datetime.datetime] = None
    ) -> List[Dict[str, Union[float, int]]]:
        """
        Récupère les données historiques depuis Alpha Vantage.
        
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
        
        av_symbol = self._format_symbol(symbol)
        av_interval = self.INTERVAL_MAP[interval]
        
        # Récupération des données
        if av_interval in ["daily", "weekly", "monthly"]:
            data, _ = self.crypto_client.get_digital_currency_daily(
                symbol=av_symbol,
                market="USD"
            )
        else:
            data, _ = self.crypto_client.get_crypto_intraday(
                symbol=av_symbol,
                market="USD",
                interval=av_interval
            )
        
        # Conversion en format standard
        result = []
        for timestamp, values in data.items():
            dt = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            if start_time <= dt and (end_time is None or dt <= end_time):
                result.append({
                    "timestamp": dt.timestamp(),
                    "open": float(values["1. open"]),
                    "high": float(values["2. high"]),
                    "low": float(values["3. low"]),
                    "close": float(values["4. close"]),
                    "volume": float(values["5. volume"])
                })
        
        return sorted(result, key=lambda x: x["timestamp"])
    
    def get_current_price(self, symbol: str) -> float:
        """
        Récupère le prix actuel depuis Alpha Vantage.
        
        Args:
            symbol: Symbole de la paire de trading (ex: "BTC/USDT")
            
        Returns:
            Prix actuel
        """
        av_symbol = self._format_symbol(symbol)
        data, _ = self.crypto_client.get_currency_exchange_rate(
            from_currency=av_symbol,
            to_currency="USD"
        )
        return float(data["5. Exchange Rate"])
    
    def get_order_book(
        self,
        symbol: str,
        limit: Optional[int] = None
    ) -> Dict[str, Union[int, List[List[float]]]]:
        """
        Récupère le carnet d'ordres depuis Alpha Vantage.
        Non supporté par l'API Alpha Vantage.
        
        Args:
            symbol: Symbole de la paire de trading (ex: "BTC/USDT")
            limit: Nombre maximum d'ordres à récupérer (optionnel)
            
        Raises:
            NotImplementedError: Cette fonctionnalité n'est pas supportée par Alpha Vantage
        """
        raise NotImplementedError(
            "La récupération du carnet d'ordres n'est pas supportée par Alpha Vantage"
        ) 