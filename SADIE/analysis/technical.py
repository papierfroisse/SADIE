"""Module d'analyse technique pour SADIE."""

from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class TechnicalAnalyzer:
    """Classe pour l'analyse technique des données de marché."""
    
    def __init__(self, data: pd.DataFrame):
        """Initialise l'analyseur technique.
        
        Args:
            data: DataFrame avec colonnes ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        """
        self._data = data.copy()
        self._validate_data()
        
    def _validate_data(self):
        """Valide le format des données d'entrée."""
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in self._data.columns for col in required_columns):
            raise ValueError(f"Les données doivent contenir les colonnes: {required_columns}")
            
    def sma(self, period: int = 20) -> pd.Series:
        """Calcule la moyenne mobile simple.
        
        Args:
            period: Période pour la moyenne mobile
            
        Returns:
            Série pandas avec les valeurs de la SMA
        """
        return self._data['close'].rolling(window=period).mean()
        
    def ema(self, period: int = 20) -> pd.Series:
        """Calcule la moyenne mobile exponentielle.
        
        Args:
            period: Période pour la moyenne mobile
            
        Returns:
            Série pandas avec les valeurs de l'EMA
        """
        return self._data['close'].ewm(span=period, adjust=False).mean()
        
    def rsi(self, period: int = 14) -> pd.Series:
        """Calcule le Relative Strength Index.
        
        Args:
            period: Période pour le RSI
            
        Returns:
            Série pandas avec les valeurs du RSI
        """
        delta = self._data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
        
    def macd(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, pd.Series]:
        """Calcule le MACD (Moving Average Convergence Divergence).
        
        Args:
            fast_period: Période pour la moyenne rapide
            slow_period: Période pour la moyenne lente
            signal_period: Période pour la ligne de signal
            
        Returns:
            Dictionnaire avec les séries 'macd', 'signal' et 'histogram'
        """
        fast_ema = self.ema(fast_period)
        slow_ema = self.ema(slow_period)
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
        
    def bollinger_bands(self, period: int = 20, std_dev: float = 2.0) -> Dict[str, pd.Series]:
        """Calcule les bandes de Bollinger.
        
        Args:
            period: Période pour la moyenne mobile
            std_dev: Nombre d'écarts-types pour les bandes
            
        Returns:
            Dictionnaire avec les séries 'upper', 'middle', 'lower'
        """
        middle = self.sma(period)
        std = self._data['close'].rolling(window=period).std()
        
        return {
            'upper': middle + (std * std_dev),
            'middle': middle,
            'lower': middle - (std * std_dev)
        }
        
    def atr(self, period: int = 14) -> pd.Series:
        """Calcule l'Average True Range.
        
        Args:
            period: Période pour l'ATR
            
        Returns:
            Série pandas avec les valeurs de l'ATR
        """
        high = self._data['high']
        low = self._data['low']
        close = self._data['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()
        
    def stochastic(self, k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """Calcule l'oscillateur stochastique.
        
        Args:
            k_period: Période pour le %K
            d_period: Période pour le %D
            
        Returns:
            Dictionnaire avec les séries 'k' et 'd'
        """
        low_min = self._data['low'].rolling(window=k_period).min()
        high_max = self._data['high'].rolling(window=k_period).max()
        
        k = 100 * ((self._data['close'] - low_min) / (high_max - low_min))
        d = k.rolling(window=d_period).mean()
        
        return {
            'k': k,
            'd': d
        }
        
    def detect_patterns(self) -> List[Dict]:
        """Détecte les patterns techniques de base.
        
        Returns:
            Liste de dictionnaires décrivant les patterns détectés
        """
        patterns = []
        close = self._data['close']
        
        # Croisements de moyennes mobiles
        sma_20 = self.sma(20)
        sma_50 = self.sma(50)
        
        # Golden Cross / Death Cross
        if (sma_20.iloc[-2] <= sma_50.iloc[-2] and sma_20.iloc[-1] > sma_50.iloc[-1]):
            patterns.append({
                'type': 'golden_cross',
                'timestamp': self._data.index[-1],
                'description': 'Croisement haussier SMA20 au-dessus SMA50'
            })
        elif (sma_20.iloc[-2] >= sma_50.iloc[-2] and sma_20.iloc[-1] < sma_50.iloc[-1]):
            patterns.append({
                'type': 'death_cross',
                'timestamp': self._data.index[-1],
                'description': 'Croisement baissier SMA20 en-dessous SMA50'
            })
            
        # Divergences RSI
        rsi_values = self.rsi()
        if len(rsi_values) >= 10:  # Vérifier sur les 10 dernières périodes
            if (close.iloc[-1] > close.iloc[-10] and rsi_values.iloc[-1] < rsi_values.iloc[-10]):
                patterns.append({
                    'type': 'bearish_divergence',
                    'timestamp': self._data.index[-1],
                    'description': 'Divergence baissière du RSI'
                })
            elif (close.iloc[-1] < close.iloc[-10] and rsi_values.iloc[-1] > rsi_values.iloc[-10]):
                patterns.append({
                    'type': 'bullish_divergence',
                    'timestamp': self._data.index[-1],
                    'description': 'Divergence haussière du RSI'
                })
                
        return patterns
        
    def support_resistance(self, window: int = 20, threshold: float = 0.02) -> Dict[str, float]:
        """Identifie les niveaux de support et résistance.
        
        Args:
            window: Fenêtre d'analyse
            threshold: Seuil de tolérance pour les niveaux
            
        Returns:
            Dictionnaire avec les niveaux identifiés
        """
        levels = []
        
        # Utiliser les plus hauts et plus bas
        highs = self._data['high'].rolling(window=window, center=True).max()
        lows = self._data['low'].rolling(window=window, center=True).min()
        
        # Identifier les niveaux potentiels
        for i in range(window, len(self._data) - window):
            if highs.iloc[i] == self._data['high'].iloc[i]:
                levels.append(self._data['high'].iloc[i])
            if lows.iloc[i] == self._data['low'].iloc[i]:
                levels.append(self._data['low'].iloc[i])
                
        # Regrouper les niveaux proches
        levels = sorted(levels)
        grouped_levels = []
        current_level = levels[0]
        
        for level in levels[1:]:
            if abs(level - current_level) / current_level <= threshold:
                current_level = (current_level + level) / 2
            else:
                grouped_levels.append(current_level)
                current_level = level
                
        grouped_levels.append(current_level)
        
        # Séparer en supports et résistances
        current_price = self._data['close'].iloc[-1]
        supports = [level for level in grouped_levels if level < current_price]
        resistances = [level for level in grouped_levels if level > current_price]
        
        return {
            'supports': supports,
            'resistances': resistances
        } 