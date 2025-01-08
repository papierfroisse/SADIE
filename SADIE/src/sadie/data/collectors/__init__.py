"""
Module de base pour les collecteurs de données.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import datetime

class DataCollector(ABC):
    """Classe de base abstraite pour les collecteurs de données."""
    
    def __init__(self, api_key: str, api_secret: Optional[str] = None):
        """
        Initialise le collecteur de données.
        
        Args:
            api_key: Clé API pour l'authentification
            api_secret: Secret API pour l'authentification (optionnel)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self) -> None:
        """Initialise le client API."""
        pass
    
    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        interval: str,
        start_time: datetime.datetime,
        end_time: Optional[datetime.datetime] = None
    ) -> List[Dict[str, Union[float, int]]]:
        """
        Récupère les données historiques pour un symbole donné.
        
        Args:
            symbol: Symbole de la paire de trading (ex: "BTC/USDT")
            interval: Intervalle de temps (ex: "1h", "1d")
            start_time: Date de début
            end_time: Date de fin (optionnel, par défaut jusqu'à maintenant)
            
        Returns:
            Liste de dictionnaires contenant les données OHLCV
            [
                {
                    "timestamp": 1623456789,
                    "open": 50000.0,
                    "high": 51000.0,
                    "low": 49000.0,
                    "close": 50500.0,
                    "volume": 100.0
                },
                ...
            ]
        """
        pass
    
    @abstractmethod
    def get_current_price(self, symbol: str) -> float:
        """
        Récupère le prix actuel pour un symbole donné.
        
        Args:
            symbol: Symbole de la paire de trading (ex: "BTC/USDT")
            
        Returns:
            Prix actuel
        """
        pass
    
    @abstractmethod
    def get_order_book(
        self,
        symbol: str,
        limit: Optional[int] = None
    ) -> Dict[str, Union[int, List[List[float]]]]:
        """
        Récupère le carnet d'ordres pour un symbole donné.
        
        Args:
            symbol: Symbole de la paire de trading (ex: "BTC/USDT")
            limit: Nombre maximum d'ordres à récupérer (optionnel)
            
        Returns:
            Dictionnaire contenant le carnet d'ordres
            {
                "timestamp": 1623456789,
                "bids": [[prix, quantité], ...],
                "asks": [[prix, quantité], ...]
            }
        """
        pass 