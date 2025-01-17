"""Tests unitaires pour le module d'analyse statistique."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from sadie.analysis.statistics import StatisticalAnalyzer, StatisticalSummary

@pytest.fixture
def sample_data():
    """Crée des données de test."""
    dates = pd.date_range(
        start=datetime(2023, 1, 1, tzinfo=timezone.utc),
        end=datetime(2023, 1, 10, tzinfo=timezone.utc),
        freq='D'
    )
    data = pd.DataFrame({
        'timestamp': dates,
        'close': [100.0, 101.0, 102.0, 101.5, 103.0, 102.5, 104.0, 103.5, 105.0, 104.5],
        'volume': [1000.0, 1100.0, 1200.0, 1150.0, 1300.0, 1250.0, 1400.0, 1350.0, 1500.0, 1450.0]
    })
    return data

@pytest.fixture
def analyzer(sample_data):
    """Crée une instance de l'analyseur avec les données de test."""
    return StatisticalAnalyzer(sample_data)

def test_analyzer_initialization(analyzer, sample_data):
    """Teste l'initialisation de l'analyseur."""
    assert len(analyzer._data) == len(sample_data)
    assert all(col in analyzer._data.columns for col in ['timestamp', 'close', 'volume'])

def test_validate_data():
    """Teste la validation des données d'entrée."""
    # Test avec des données valides
    valid_data = pd.DataFrame({
        'timestamp': pd.date_range(start='2023-01-01', end='2023-01-10', freq='D'),
        'close': [100.0] * 10,
        'volume': [1000.0] * 10
    })
    analyzer = StatisticalAnalyzer(valid_data)
    
    # Test avec un DataFrame vide
    with pytest.raises(ValueError):
        StatisticalAnalyzer(pd.DataFrame())
        
    # Test avec des données non-DataFrame
    with pytest.raises(ValueError):
        StatisticalAnalyzer([1, 2, 3])

def test_calculate_returns(analyzer):
    """Teste le calcul des rendements."""
    returns = analyzer.calculate_returns('close')
    
    assert isinstance(returns, pd.Series)
    assert len(returns) == 9  # Une observation de moins à cause du shift
    
    # Test avec une colonne inexistante
    with pytest.raises(ValueError):
        analyzer.calculate_returns('invalid_column')

def test_analyze_distribution(analyzer):
    """Teste l'analyse de la distribution."""
    stats = analyzer.analyze_distribution('close')
    
    assert isinstance(stats, StatisticalSummary)
    assert stats.mean == pytest.approx(102.7)
    assert stats.median == pytest.approx(102.75)
    assert stats.min_value == pytest.approx(100.0)
    assert stats.max_value == pytest.approx(105.0)
    
    # Test avec une colonne inexistante
    with pytest.raises(ValueError):
        analyzer.analyze_distribution('invalid_column')

def test_detect_outliers(analyzer):
    """Teste la détection des outliers."""
    # Test avec la méthode IQR
    outliers_iqr = analyzer.detect_outliers('close', method='iqr')
    assert isinstance(outliers_iqr, pd.Series)
    assert len(outliers_iqr) == 10
    
    # Test avec la méthode Z-score
    outliers_zscore = analyzer.detect_outliers('close', method='zscore')
    assert isinstance(outliers_zscore, pd.Series)
    assert len(outliers_zscore) == 10
    
    # Test avec une méthode invalide
    with pytest.raises(ValueError):
        analyzer.detect_outliers('close', method='invalid_method')

def test_calculate_volatility(analyzer):
    """Teste le calcul de la volatilité."""
    volatility = analyzer.calculate_volatility('close', window=5)
    
    assert isinstance(volatility, pd.Series)
    assert len(volatility) == 9  # Une observation de moins à cause des rendements
    assert all(v >= 0 for v in volatility.dropna())  # La volatilité doit être positive
    
    # Test avec une fenêtre plus grande que les données
    volatility_large_window = analyzer.calculate_volatility('close', window=20)
    assert all(pd.isna(volatility_large_window[:19]))  # Les premières valeurs doivent être NaN

def test_calculate_correlation(analyzer):
    """Teste le calcul de la corrélation."""
    correlation, p_value = analyzer.calculate_correlation('close', 'volume')
    
    assert isinstance(correlation, float)
    assert isinstance(p_value, float)
    assert -1 <= correlation <= 1
    assert 0 <= p_value <= 1
    
    # Test avec des colonnes de longueurs différentes
    analyzer._data.loc[0, 'volume'] = np.nan
    with pytest.raises(ValueError):
        analyzer.calculate_correlation('close', 'volume')

def test_calculate_beta(analyzer):
    """Teste le calcul du bêta."""
    returns = analyzer.calculate_returns('close')
    market_returns = pd.Series(np.random.normal(0.0005, 0.01, len(returns)))
    
    beta, alpha = analyzer.calculate_beta(returns, market_returns)
    
    assert isinstance(beta, float)
    assert isinstance(alpha, float)
    
    # Test avec des séries de longueurs différentes
    with pytest.raises(ValueError):
        analyzer.calculate_beta(returns, market_returns[:-1])

def test_calculate_var(analyzer):
    """Teste le calcul de la VaR."""
    returns = analyzer.calculate_returns('close')
    
    var = analyzer.calculate_var(returns, confidence_level=0.95)
    
    assert isinstance(var, float)
    assert var <= 0  # La VaR doit être négative
    
    # Test avec un niveau de confiance invalide
    with pytest.raises(ValueError):
        analyzer.calculate_var(returns, confidence_level=1.5)

def test_calculate_cvar(analyzer):
    """Teste le calcul de la CVaR."""
    returns = analyzer.calculate_returns('close')
    
    cvar = analyzer.calculate_cvar(returns, confidence_level=0.95)
    
    assert isinstance(cvar, float)
    assert cvar <= analyzer.calculate_var(returns, confidence_level=0.95)  # La CVaR doit être inférieure à la VaR
    
    # Test avec un niveau de confiance invalide
    with pytest.raises(ValueError):
        analyzer.calculate_cvar(returns, confidence_level=0)

def test_calculate_sharpe_ratio(analyzer):
    """Teste le calcul du ratio de Sharpe."""
    returns = analyzer.calculate_returns('close')
    
    sharpe = analyzer.calculate_sharpe_ratio(returns, risk_free_rate=0.02)
    
    assert isinstance(sharpe, float)
    
    # Test avec différents taux sans risque
    sharpe_zero = analyzer.calculate_sharpe_ratio(returns, risk_free_rate=0.0)
    sharpe_high = analyzer.calculate_sharpe_ratio(returns, risk_free_rate=0.10)
    assert sharpe_zero > sharpe_high  # Le ratio doit diminuer quand le taux sans risque augmente

def test_calculate_sortino_ratio(analyzer):
    """Teste le calcul du ratio de Sortino."""
    returns = analyzer.calculate_returns('close')
    
    sortino = analyzer.calculate_sortino_ratio(returns, risk_free_rate=0.02)
    
    assert isinstance(sortino, float)
    
    # Test avec des rendements tous positifs
    positive_returns = pd.Series([0.01] * len(returns))
    sortino_positive = analyzer.calculate_sortino_ratio(positive_returns)
    assert sortino_positive == float('inf')  # Pas de rendements négatifs = ratio infini 