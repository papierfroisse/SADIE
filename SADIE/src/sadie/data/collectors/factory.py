"""
Factory pour la création des collecteurs de données.
"""

from typing import Dict, Optional, Type

from sadie.data.collectors import DataCollector
from sadie.data.collectors.binance import BinanceDataCollector
from sadie.data.collectors.alpha_vantage import AlphaVantageDataCollector

class DataCollectorFactory:
    """Factory pour créer des instances de collecteurs de données."""
    
    _collectors: Dict[str, Type[DataCollector]] = {
        "binance": BinanceDataCollector,
        "alpha_vantage": AlphaVantageDataCollector
    }
    
    @classmethod
    def create(
        cls,
        source: str,
        api_key: str,
        api_secret: Optional[str] = None
    ) -> DataCollector:
        """
        Crée une instance de collecteur de données.
        
        Args:
            source: Source des données ("binance", "alpha_vantage", etc.)
            api_key: Clé API pour l'authentification
            api_secret: Secret API pour l'authentification (optionnel)
            
        Returns:
            Instance de collecteur de données
            
        Raises:
            ValueError: Si la source n'est pas supportée
        """
        collector_class = cls._collectors.get(source.lower())
        if not collector_class:
            raise ValueError(
                f"Source non supportée: {source}. "
                f"Sources disponibles: {', '.join(cls._collectors.keys())}"
            )
        
        return collector_class(api_key=api_key, api_secret=api_secret)
    
    @classmethod
    def register_collector(cls, source: str, collector_class: Type[DataCollector]) -> None:
        """
        Enregistre une nouvelle classe de collecteur de données.
        
        Args:
            source: Identifiant de la source de données
            collector_class: Classe du collecteur à enregistrer
            
        Raises:
            TypeError: Si la classe ne dérive pas de DataCollector
        """
        if not issubclass(collector_class, DataCollector):
            raise TypeError(
                f"La classe {collector_class.__name__} doit dériver de DataCollector"
            )
        
        cls._collectors[source.lower()] = collector_class 