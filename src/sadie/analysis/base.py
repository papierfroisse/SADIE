"""
Classes de base pour l'analyse des données.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from ..data.exceptions import DataProcessingError

logger = logging.getLogger(__name__)

class BaseAnalyzer(ABC):
    """Classe de base pour l'analyse des données."""

    def __init__(self, **kwargs):
        """
        Initialise l'analyseur.

        Args:
            **kwargs: Arguments additionnels
        """
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure le logging pour l'analyseur."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def process(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Traite les données.

        Args:
            data: Données à traiter

        Returns:
            Résultats de l'analyse
        """
        pass
    
    @abstractmethod
    async def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyse les données.

        Args:
            data: DataFrame à analyser

        Returns:
            Résultats de l'analyse
        """
        pass

class TimeSeriesAnalyzer(BaseAnalyzer):
    """Analyseur de séries temporelles."""

    def __init__(self, window_size: int = 20, **kwargs):
        """
        Initialise l'analyseur de séries temporelles.

        Args:
            window_size: Taille de la fenêtre glissante
            **kwargs: Arguments additionnels
        """
        super().__init__(**kwargs)
        self.window_size = window_size
    
    async def process(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Traite les données.

        Args:
            data: Données à traiter

        Returns:
            Résultats de l'analyse
        """
        try:
            if isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                df = pd.DataFrame(data)
            
            if "timestamp" in df.columns:
                df.set_index("timestamp", inplace=True)
            
            return await self.analyze(df)
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement des données: {e}")
            raise DataProcessingError(str(e))
    
    async def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyse les données.

        Args:
            data: DataFrame à analyser

        Returns:
            Résultats de l'analyse
        """
        results = {}
        
        try:
            # Statistiques de base
            results["mean"] = data.mean().to_dict()
            results["std"] = data.std().to_dict()
            results["min"] = data.min().to_dict()
            results["max"] = data.max().to_dict()
            
            # Moyennes mobiles
            if len(data) >= self.window_size:
                rolling = data.rolling(window=self.window_size)
                results["rolling_mean"] = rolling.mean().iloc[-1].to_dict()
                results["rolling_std"] = rolling.std().iloc[-1].to_dict()
            
            # Tendance
            if len(data) >= 2:
                results["trend"] = {}
                for column in data.select_dtypes(include=[np.number]).columns:
                    slope = np.polyfit(range(len(data)), data[column], 1)[0]
                    results["trend"][column] = "up" if slope > 0 else "down"
            
            return results
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse des données: {e}")
            raise DataProcessingError(str(e))

class StatisticalAnalyzer(BaseAnalyzer):
    """Analyseur statistique."""

    def __init__(self, confidence_level: float = 0.95, **kwargs):
        """
        Initialise l'analyseur statistique.

        Args:
            confidence_level: Niveau de confiance pour les tests statistiques
            **kwargs: Arguments additionnels
        """
        super().__init__(**kwargs)
        self.confidence_level = confidence_level
    
    async def process(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Traite les données.

        Args:
            data: Données à traiter

        Returns:
            Résultats de l'analyse
        """
        try:
            if isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                df = pd.DataFrame(data)
            
            return await self.analyze(df)
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement des données: {e}")
            raise DataProcessingError(str(e))
    
    async def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyse les données.

        Args:
            data: DataFrame à analyser

        Returns:
            Résultats de l'analyse
        """
        results = {}
        
        try:
            # Statistiques descriptives
            results["describe"] = data.describe().to_dict()
            
            # Tests de normalité
            for column in data.select_dtypes(include=[np.number]).columns:
                if len(data[column]) >= 3:  # Minimum requis pour le test
                    from scipy import stats
                    stat, p_value = stats.normaltest(data[column].dropna())
                    results[f"{column}_normal_test"] = {
                        "statistic": stat,
                        "p_value": p_value,
                        "is_normal": p_value > (1 - self.confidence_level)
                    }
            
            # Corrélations
            if len(data.columns) > 1:
                results["correlations"] = data.corr().to_dict()
            
            return results
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse des données: {e}")
            raise DataProcessingError(str(e)) 