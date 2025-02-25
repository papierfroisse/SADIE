"""Module de base pour le stockage."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

class BaseStorage(ABC):
    """Classe de base pour le stockage des données."""
    
    @abstractmethod
    async def connect(self) -> None:
        """Établit la connexion au stockage."""
        pass
        
    @abstractmethod
    async def disconnect(self) -> None:
        """Ferme la connexion au stockage."""
        pass
        
    @abstractmethod
    async def store_trades(self, trades: List[Dict[str, Any]]) -> None:
        """Stocke une liste de trades.
        
        Args:
            trades: Liste des trades à stocker
        """
        pass
        
    @abstractmethod
    async def get_trades(
        self,
        symbol: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Récupère les trades pour un symbole donné.
        
        Args:
            symbol: Le symbole à récupérer
            start_time: Timestamp de début optionnel
            end_time: Timestamp de fin optionnel
            
        Returns:
            Liste des trades correspondants
        """
        pass
        
    @abstractmethod
    async def store_statistics(self, symbol: str, stats: Dict[str, Any]) -> None:
        """Stocke les statistiques pour un symbole.
        
        Args:
            symbol: Le symbole concerné
            stats: Les statistiques à stocker
        """
        pass
        
    @abstractmethod
    async def get_statistics(self, symbol: str) -> Dict[str, Any]:
        """Récupère les statistiques pour un symbole.
        
        Args:
            symbol: Le symbole concerné
            
        Returns:
            Les statistiques du symbole
        """
        pass 