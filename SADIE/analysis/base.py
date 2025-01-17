"""
Module de base pour les analyseurs.
"""

import pandas as pd
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class Analyzer(ABC):
    """Classe de base pour tous les analyseurs."""
    
    def __init__(self, data: pd.DataFrame):
        """Initialise l'analyseur avec les données.
        
        Args:
            data: DataFrame contenant les données à analyser
        """
        self.data = data
        
    @abstractmethod
    def analyze(self, **kwargs) -> Dict[str, Any]:
        """Analyse les données.
        
        Returns:
            Dictionnaire contenant les résultats de l'analyse
        """
        pass 