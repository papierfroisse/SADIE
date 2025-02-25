"""Module des indicateurs techniques."""

import pandas as pd
import numpy as np
from typing import Dict, Any

class TechnicalIndicators:
    """Calcul des indicateurs techniques."""
    
    @staticmethod
    def rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calcule le RSI (Relative Strength Index)."""
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def macd(data: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calcule le MACD (Moving Average Convergence Divergence)."""
        exp1 = data['close'].ewm(span=12, adjust=False).mean()
        exp2 = data['close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        return {
            'macd': macd,
            'signal': signal,
            'histogram': histogram
        }
    
    @staticmethod
    def stochastic(data: pd.DataFrame, period: int = 14) -> Dict[str, pd.Series]:
        """Calcule l'oscillateur stochastique."""
        low_min = data['low'].rolling(window=period).min()
        high_max = data['high'].rolling(window=period).max()
        k = 100 * (data['close'] - low_min) / (high_max - low_min)
        d = k.rolling(window=3).mean()
        return {
            'k': k,
            'd': d
        }
    
    @staticmethod
    def bollinger_bands(data: pd.DataFrame, period: int = 20) -> Dict[str, pd.Series]:
        """Calcule les bandes de Bollinger."""
        ma = data['close'].rolling(window=period).mean()
        std = data['close'].rolling(window=period).std()
        upper = ma + (std * 2)
        lower = ma - (std * 2)
        b_percent = (data['close'] - lower) / (upper - lower)
        return {
            'upper': upper,
            'middle': ma,
            'lower': lower,
            'b_percent': b_percent
        }

def calculate_indicators(trades: pd.DataFrame) -> Dict[str, Any]:
    """Calcule tous les indicateurs techniques."""
    # Conversion en bougies
    ohlcv = trades.resample('1min').agg({
        'price': ['first', 'max', 'min', 'last'],
        'quantity': 'sum'
    })
    ohlcv.columns = ['open', 'high', 'low', 'close', 'volume']
    
    # Calcul des indicateurs
    rsi = TechnicalIndicators.rsi(ohlcv)
    macd_data = TechnicalIndicators.macd(ohlcv)
    stoch_data = TechnicalIndicators.stochastic(ohlcv)
    bb_data = TechnicalIndicators.bollinger_bands(ohlcv)
    
    return {
        'rsi': rsi.iloc[-1],
        'macd': {
            'macd': macd_data['macd'].iloc[-1],
            'signal': macd_data['signal'].iloc[-1],
            'histogram': macd_data['histogram'].iloc[-1]
        },
        'stochastic': {
            'k': stoch_data['k'].iloc[-1],
            'd': stoch_data['d'].iloc[-1]
        },
        'bollinger_bands': {
            'upper': bb_data['upper'].iloc[-1],
            'middle': bb_data['middle'].iloc[-1],
            'lower': bb_data['lower'].iloc[-1],
            'b_percent': bb_data['b_percent'].iloc[-1]
        }
    }