"""Module de base pour le stockage des données."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from sadie.core.monitoring import get_logger
from sadie.core.models.events import Trade

class BaseStorage(ABC):
    """Classe de base pour le stockage des données."""
    
    def __init__(
        self,
        name: str,
        logger: Optional[logging.Logger] = None
    ):
        """Initialise le stockage.
        
        Args:
            name: Nom du stockage
            logger: Logger optionnel
        """
        self.name = name
        self.logger = logger or get_logger(f"{self.__class__.__name__}_{name}")
    
    @abstractmethod
    async def connect(self) -> None:
        """Établit la connexion au stockage."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Ferme la connexion au stockage."""
        pass
    
    @abstractmethod
    async def store_trades(self, symbol: str, trades: List[Trade]) -> None:
        """Stocke une liste de trades.
        
        Args:
            symbol: Symbole des trades
            trades: Liste des trades à stocker
        """
        pass
    
    @abstractmethod
    async def get_trades(
        self,
        symbol: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: Optional[int] = None
    ) -> List[Trade]:
        """Récupère les trades stockés.
        
        Args:
            symbol: Symbole des trades
            start_time: Timestamp de début (optionnel)
            end_time: Timestamp de fin (optionnel)
            limit: Nombre maximum de trades à retourner (optionnel)
            
        Returns:
            Liste des trades correspondants aux critères
        """
        pass
    
    @abstractmethod
    async def store_statistics(self, symbol: str, statistics: Dict[str, Any]) -> None:
        """Stocke les statistiques d'un symbole.
        
        Args:
            symbol: Symbole concerné
            statistics: Statistiques à stocker
        """
        pass
    
    @abstractmethod
    async def get_statistics(
        self,
        symbol: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """Récupère les statistiques stockées.
        
        Args:
            symbol: Symbole concerné
            start_time: Timestamp de début (optionnel)
            end_time: Timestamp de fin (optionnel)
            
        Returns:
            Statistiques correspondant aux critères
        """
        pass 