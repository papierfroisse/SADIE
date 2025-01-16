"""Module de base pour l'analyse."""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Type, Union

import numpy as np
import pandas as pd

from ..core.monitoring import get_logger
from ..utils.decorators import log_execution

logger = get_logger(__name__)

class Analyzer(ABC):
    """Classe de base pour les analyseurs."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(f"analyzer.{name}")
        self._data: List[Dict] = []
        self._last_update = datetime.min
        
    @abstractmethod
    async def analyze(self, data: Union[Dict, List[Dict]]) -> Dict[str, Any]:
        """Analyse les données.
        
        Args:
            data: Données à analyser
            
        Returns:
            Résultats de l'analyse
        """
        pass
        
    def add_data(self, data: Union[Dict, List[Dict]]) -> None:
        """Ajoute des données à analyser.
        
        Args:
            data: Données à ajouter
        """
        if isinstance(data, dict):
            self._data.append(data)
        else:
            self._data.extend(data)
        self._last_update = datetime.utcnow()
        
    def clear_data(self) -> None:
        """Vide les données."""
        self._data.clear()
        self._last_update = datetime.min
        
    def get_data(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict]:
        """Récupère les données dans une fenêtre temporelle.
        
        Args:
            start_time: Début de la fenêtre
            end_time: Fin de la fenêtre
            
        Returns:
            Données filtrées
        """
        if not (start_time or end_time):
            return self._data.copy()
            
        filtered_data = []
        for item in self._data:
            timestamp = item.get("timestamp")
            if not timestamp:
                continue
                
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
                
            if start_time and timestamp < start_time:
                continue
            if end_time and timestamp > end_time:
                continue
                
            filtered_data.append(item)
            
        return filtered_data
        
    def to_dataframe(
        self,
        columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Convertit les données en DataFrame.
        
        Args:
            columns: Colonnes à inclure
            
        Returns:
            DataFrame pandas
        """
        df = pd.DataFrame(self._data)
        if columns:
            df = df[columns]
        return df
        
    @staticmethod
    def calculate_statistics(
        data: Union[List[float], np.ndarray]
    ) -> Dict[str, float]:
        """Calcule des statistiques de base.
        
        Args:
            data: Données numériques
            
        Returns:
            Statistiques calculées
        """
        if not data:
            return {}
            
        array = np.array(data)
        return {
            "count": len(array),
            "mean": float(np.mean(array)),
            "std": float(np.std(array)),
            "min": float(np.min(array)),
            "max": float(np.max(array)),
            "median": float(np.median(array))
        }
        
    @staticmethod
    def detect_outliers(
        data: Union[List[float], np.ndarray],
        threshold: float = 3.0
    ) -> List[int]:
        """Détecte les valeurs aberrantes.
        
        Args:
            data: Données numériques
            threshold: Seuil en écarts-types
            
        Returns:
            Indices des valeurs aberrantes
        """
        if not data:
            return []
            
        array = np.array(data)
        mean = np.mean(array)
        std = np.std(array)
        z_scores = np.abs((array - mean) / std)
        return list(np.where(z_scores > threshold)[0])
        
    @staticmethod
    def calculate_moving_average(
        data: Union[List[float], np.ndarray],
        window: int = 5
    ) -> np.ndarray:
        """Calcule la moyenne mobile.
        
        Args:
            data: Données numériques
            window: Taille de la fenêtre
            
        Returns:
            Moyenne mobile
        """
        if not data:
            return np.array([])
            
        array = np.array(data)
        return np.convolve(array, np.ones(window) / window, mode="valid")
        
    @staticmethod
    def calculate_correlation(
        x: Union[List[float], np.ndarray],
        y: Union[List[float], np.ndarray]
    ) -> float:
        """Calcule la corrélation entre deux séries.
        
        Args:
            x: Première série
            y: Deuxième série
            
        Returns:
            Coefficient de corrélation
        """
        if not (x and y) or len(x) != len(y):
            return 0.0
            
        return float(np.corrcoef(x, y)[0, 1]) 