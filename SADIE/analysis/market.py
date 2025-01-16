"""Module d'analyse des données de marché."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from .base import Analyzer
from ..core.monitoring import get_logger

logger = get_logger(__name__)

class MarketAnalyzer(Analyzer):
    """Analyseur de données de marché."""
    
    def __init__(self, name: str = "market"):
        super().__init__(name)
        self.metrics = {}
        
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse les données de marché.
        
        Args:
            data: Données à analyser
            
        Returns:
            Résultats de l'analyse
        """
        self.add_data(data)
        
        # Conversion en DataFrame pour l'analyse
        df = self.to_dataframe()
        if df.empty:
            return {}
            
        results = {}
        
        # Analyse des prix
        if "price" in df.columns:
            price_stats = self.calculate_statistics(df["price"])
            results["price_analysis"] = price_stats
            
            # Détection des anomalies de prix
            outliers = self.detect_outliers(df["price"])
            results["price_outliers"] = len(outliers)
            
            # Moyenne mobile des prix
            ma = self.calculate_moving_average(df["price"], window=5)
            results["price_ma"] = ma.tolist()
            
        # Analyse du volume
        if "volume" in df.columns:
            volume_stats = self.calculate_statistics(df["volume"])
            results["volume_analysis"] = volume_stats
            
            # Corrélation prix-volume
            if "price" in df.columns:
                correlation = self.calculate_correlation(
                    df["price"],
                    df["volume"]
                )
                results["price_volume_correlation"] = correlation
                
        # Métriques de liquidité
        if "bid" in df.columns and "ask" in df.columns:
            spread = df["ask"] - df["bid"]
            results["spread_analysis"] = self.calculate_statistics(spread)
            
        self.metrics = results
        return results 