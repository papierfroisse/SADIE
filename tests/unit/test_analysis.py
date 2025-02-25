"""Tests unitaires pour les modules d'analyse technique."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from sadie.analysis.indicators import TechnicalIndicators
from sadie.analysis.harmonic_patterns import HarmonicAnalyzer, PatternType, TrendType
from sadie.analysis.visualization import ChartVisualizer

@pytest.fixture
def sample_data():
    """Crée un DataFrame de test avec des données OHLCV."""
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
    data = {
        'open': np.random.normal(100, 10, 100),
        'high': np.random.normal(105, 10, 100),
        'low': np.random.normal(95, 10, 100),
        'close': np.random.normal(100, 10, 100),
        'volume': np.random.normal(1000, 100, 100)
    }
    
    # Correction des high/low pour assurer high >= low
    data['high'] = np.maximum(
        data['high'],
        np.maximum(data['open'], data['close'])
    )
    data['low'] = np.minimum(
        data['low'],
        np.minimum(data['open'], data['close'])
    )
    
    df = pd.DataFrame(data, index=dates)
    return df

def test_technical_indicators(sample_data):
    """Teste le calcul des indicateurs techniques."""
    indicators = TechnicalIndicators(sample_data)
    
    # Test des Bandes de Bollinger
    bb_mid, bb_up, bb_low, bb_b = indicators.bollinger_bands()
    assert len(bb_mid) == len(sample_data)
    assert all(bb_up >= bb_mid)
    assert all(bb_low <= bb_mid)
    assert all((bb_b >= 0) & (bb_b <= 1))
    
    # Test du MACD
    macd, signal, hist = indicators.macd()
    assert len(macd) == len(sample_data)
    assert len(signal) == len(sample_data)
    assert len(hist) == len(sample_data)
    assert np.allclose(hist, macd - signal)
    
    # Test du Stochastique
    k, d = indicators.stochastic()
    assert len(k) == len(sample_data)
    assert len(d) == len(sample_data)
    assert all((k >= 0) & (k <= 100))
    assert all((d >= 0) & (d <= 100))
    
    # Test du RSI
    rsi = indicators.rsi()
    assert len(rsi) == len(sample_data)
    assert all((rsi >= 0) & (rsi <= 100))
    
    # Test de l'ATR
    atr = indicators.atr()
    assert len(atr) == len(sample_data)
    assert all(atr >= 0)

def test_harmonic_analyzer(sample_data):
    """Teste l'analyseur de patterns harmoniques."""
    analyzer = HarmonicAnalyzer(sample_data)
    
    # Test de la détection des points pivots
    swing_points = analyzer._find_swing_points()
    assert len(swing_points) > 0
    
    # Test du calcul des ratios
    points = [(0, 100), (1, 110), (2, 105), (3, 108)]
    ratios = analyzer._calculate_ratios(points)
    assert len(ratios) == 3
    assert all(r >= 0 for r in ratios)
    
    # Test de la validation des ratios
    valid = analyzer._check_pattern_ratios(
        ratios,
        PatternType.GARTLEY,
        TrendType.BULLISH
    )
    assert isinstance(valid, bool)
    
    # Test de l'identification des patterns
    patterns = analyzer.identify_patterns()
    for pattern in patterns:
        assert hasattr(pattern, 'pattern_type')
        assert hasattr(pattern, 'trend')
        assert hasattr(pattern, 'points')
        assert hasattr(pattern, 'confidence')
        assert hasattr(pattern, 'potential_reversal_zone')
        assert 0 <= pattern.confidence <= 1
        assert len(pattern.potential_reversal_zone) == 2

def test_chart_visualizer(sample_data):
    """Teste le visualiseur de graphiques."""
    visualizer = ChartVisualizer(sample_data)
    
    # Test de la création du graphique complet
    fig = visualizer.create_chart(
        show_volume=True,
        show_bb=True,
        show_macd=True,
        show_stoch=True,
        show_patterns=True
    )
    assert fig is not None
    
    # Test des sous-graphiques
    assert len(fig.data) > 0  # Au moins le graphique principal
    
    # Test sans indicateurs
    fig = visualizer.create_chart(
        show_volume=False,
        show_bb=False,
        show_macd=False,
        show_stoch=False,
        show_patterns=False
    )
    assert fig is not None
    assert len(fig.data) == 1  # Uniquement le graphique principal
    
    # Test des couleurs personnalisées
    custom_colors = visualizer.colors.copy()
    custom_colors['up'] = '#00ff00'
    custom_colors['down'] = '#ff0000'
    visualizer.colors = custom_colors
    
    fig = visualizer.create_chart()
    assert fig is not None 