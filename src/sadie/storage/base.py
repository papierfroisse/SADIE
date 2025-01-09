"""
Classes de base pour le stockage des données.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..data.exceptions import StorageError

logger = logging.getLogger(__name__)

class BaseStorage(ABC):
    """Classe de base pour le stockage des données."""

    def __init__(self, **kwargs):
        """
        Initialise le stockage.

        Args:
            **kwargs: Arguments additionnels
        """
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure le logging pour le stockage."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def connect(self):
        """Établit la connexion avec le stockage."""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Ferme la connexion avec le stockage."""
        pass
    
    @abstractmethod
    async def store(self, data: Dict[str, Any], timestamp: Optional[datetime] = None):
        """
        Stocke des données.

        Args:
            data: Données à stocker
            timestamp: Horodatage des données (optionnel)
        """
        pass
    
    @abstractmethod
    async def retrieve(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Récupère des données.

        Args:
            start_time: Début de la période (optionnel)
            end_time: Fin de la période (optionnel)
            **kwargs: Critères additionnels

        Returns:
            Liste des données récupérées
        """
        pass
    
    @abstractmethod
    async def delete(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        **kwargs
    ) -> int:
        """
        Supprime des données.

        Args:
            start_time: Début de la période (optionnel)
            end_time: Fin de la période (optionnel)
            **kwargs: Critères additionnels

        Returns:
            Nombre d'éléments supprimés
        """
        pass
    
    @abstractmethod
    async def count(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        **kwargs
    ) -> int:
        """
        Compte le nombre d'éléments.

        Args:
            start_time: Début de la période (optionnel)
            end_time: Fin de la période (optionnel)
            **kwargs: Critères additionnels

        Returns:
            Nombre d'éléments
        """
        pass

class MemoryStorage(BaseStorage):
    """Stockage en mémoire pour les tests et le développement."""

    def __init__(self, **kwargs):
        """
        Initialise le stockage en mémoire.

        Args:
            **kwargs: Arguments additionnels
        """
        super().__init__(**kwargs)
        self.data: List[Dict[str, Any]] = []
    
    async def connect(self):
        """Pas de connexion nécessaire pour le stockage en mémoire."""
        pass
    
    async def disconnect(self):
        """Pas de déconnexion nécessaire pour le stockage en mémoire."""
        self.data.clear()
    
    async def store(self, data: Dict[str, Any], timestamp: Optional[datetime] = None):
        """
        Stocke des données en mémoire.

        Args:
            data: Données à stocker
            timestamp: Horodatage des données (optionnel)
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        self.data.append({"timestamp": timestamp, "data": data})
    
    async def retrieve(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Récupère des données de la mémoire.

        Args:
            start_time: Début de la période (optionnel)
            end_time: Fin de la période (optionnel)
            **kwargs: Critères additionnels

        Returns:
            Liste des données récupérées
        """
        result = []
        
        for item in self.data:
            if start_time and item["timestamp"] < start_time:
                continue
            if end_time and item["timestamp"] > end_time:
                continue
            
            match = True
            for key, value in kwargs.items():
                if key not in item["data"] or item["data"][key] != value:
                    match = False
                    break
            
            if match:
                result.append(item["data"])
        
        return result
    
    async def delete(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        **kwargs
    ) -> int:
        """
        Supprime des données de la mémoire.

        Args:
            start_time: Début de la période (optionnel)
            end_time: Fin de la période (optionnel)
            **kwargs: Critères additionnels

        Returns:
            Nombre d'éléments supprimés
        """
        initial_count = len(self.data)
        items_to_keep = []
        
        for item in self.data:
            if start_time and item["timestamp"] < start_time:
                items_to_keep.append(item)
                continue
            if end_time and item["timestamp"] > end_time:
                items_to_keep.append(item)
                continue
            
            match = True
            for key, value in kwargs.items():
                if key not in item["data"] or item["data"][key] != value:
                    match = False
                    break
            
            if not match:
                items_to_keep.append(item)
        
        self.data = items_to_keep
        return initial_count - len(self.data)
    
    async def count(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        **kwargs
    ) -> int:
        """
        Compte le nombre d'éléments en mémoire.

        Args:
            start_time: Début de la période (optionnel)
            end_time: Fin de la période (optionnel)
            **kwargs: Critères additionnels

        Returns:
            Nombre d'éléments
        """
        count = 0
        
        for item in self.data:
            if start_time and item["timestamp"] < start_time:
                continue
            if end_time and item["timestamp"] > end_time:
                continue
            
            match = True
            for key, value in kwargs.items():
                if key not in item["data"] or item["data"][key] != value:
                    match = False
                    break
            
            if match:
                count += 1
        
        return count 