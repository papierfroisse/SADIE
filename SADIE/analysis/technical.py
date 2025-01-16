"""Module d'analyse technique."""

from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from .base import Analyzer
from ..core.monitoring import get_logger

logger = get_logger(__name__)

class TechnicalAnalyzer(Analyzer):
    """Analyseur d'indicateurs techniques."""
    
    def __init__(self, name: str = "technical"):
        super().__init__(name)
        self.indicators = {}
        
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse technique des données.
        
        Args:
            data: Données à analyser
            
        Returns:
            Résultats de l'analyse
        """
        self.add_data(data)
        df = self.to_dataframe()
        if df.empty:
            return {}
            
        results = {}
        
        if "price" in df.columns:
            # RSI
            results["rsi"] = self._calculate_rsi(df["price"])
            
            # MACD
            results["macd"] = self._calculate_macd(df["price"])
            
            # Bandes de Bollinger
            results["bollinger"] = self._calculate_bollinger_bands(df["price"])
            
        self.indicators = results
        return results
        
    def _calculate_rsi(
        self,
        prices: Union[List[float], pd.Series],
        period: int = 14
    ) -> float:
        """Calcule le RSI.
        
        Args:
            prices: Série de prix
            period: Période de calcul
            
        Returns:
            Valeur du RSI
        """
        if len(prices) < period:
            return 50.0  # Valeur neutre par défaut
            
        # Calcul des variations
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].mean()
        down = -seed[seed < 0].mean()
        
        if down == 0:
            return 100.0
            
        rs = up/down
        return 100.0 - (100.0 / (1.0 + rs))
        
    def _calculate_macd(
        self,
        prices: Union[List[float], pd.Series],
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Dict[str, float]:
        """Calcule le MACD.
        
        Args:
            prices: Série de prix
            fast: Période rapide
            slow: Période lente
            signal: Période du signal
            
        Returns:
            Valeurs du MACD
        """
        if len(prices) < slow:
            return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}
            
        # Calcul des moyennes mobiles exponentielles
        ema_fast = pd.Series(prices).ewm(span=fast).mean()
        ema_slow = pd.Series(prices).ewm(span=slow).mean()
        
        # Calcul du MACD et du signal
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        
        return {
            "macd": float(macd_line.iloc[-1]),
            "signal": float(signal_line.iloc[-1]),
            "histogram": float(macd_line.iloc[-1] - signal_line.iloc[-1])
        }
        
    def _calculate_bollinger_bands(
        self,
        prices: Union[List[float], pd.Series],
        period: int = 20,
        num_std: float = 2.0
    ) -> Dict[str, float]:
        """Calcule les bandes de Bollinger.
        
        Args:
            prices: Série de prix
            period: Période de calcul
            num_std: Nombre d'écarts-types
            
        Returns:
            Valeurs des bandes
        """
        if len(prices) < period:
            return {
                "upper": float(prices[-1]),
                "middle": float(prices[-1]),
                "lower": float(prices[-1])
            }
            
        # Calcul de la moyenne mobile
        middle = pd.Series(prices).rolling(window=period).mean()
        
        # Calcul de l'écart-type
        std = pd.Series(prices).rolling(window=period).std()
        
        return {
            "upper": float(middle.iloc[-1] + (std.iloc[-1] * num_std)),
            "middle": float(middle.iloc[-1]),
            "lower": float(middle.iloc[-1] - (std.iloc[-1] * num_std))
        } 