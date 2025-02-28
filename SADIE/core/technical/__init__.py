"""Module d'analyse technique pour SADIE.

Ce module fournit des fonctionnalités d'analyse technique pour les données de marché,
incluant des indicateurs, des patterns et des signaux de trading.
"""

from .indicators import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_ema, calculate_sma, calculate_stochastic
)

from .patterns import (
    detect_patterns, identify_candlestick_patterns,
    detect_support_resistance
)

__all__ = [
    'calculate_rsi', 'calculate_macd', 'calculate_bollinger_bands',
    'calculate_ema', 'calculate_sma', 'calculate_stochastic',
    'detect_patterns', 'identify_candlestick_patterns',
    'detect_support_resistance'
] 