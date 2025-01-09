"""
Tests unitaires pour l'analyse des données.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from sadie.analysis import BaseAnalyzer, StatisticalAnalyzer, TimeSeriesAnalyzer
from sadie.data.exceptions import DataProcessingError

@pytest.fixture
def time_series_data():
    """Fixture pour les données de séries temporelles."""
    dates = pd.date_range(start="2024-01-01", periods=100, freq="H")
    data = {
        "price": np.random.normal(100, 10, 100),
        "volume": np.random.exponential(50, 100)
    }
    return pd.DataFrame(data, index=dates)

@pytest.fixture
def statistical_data():
    """Fixture pour les données statistiques."""
    return pd.DataFrame({
        "values": np.random.normal(0, 1, 1000),
        "groups": np.random.choice(["A", "B", "C"], 1000)
    })

@pytest.mark.asyncio
async def test_time_series_analyzer_init():
    """Teste l'initialisation de l'analyseur de séries temporelles."""
    analyzer = TimeSeriesAnalyzer(window_size=20)
    assert analyzer.window_size == 20

@pytest.mark.asyncio
async def test_time_series_analyzer_process(time_series_data):
    """Teste le traitement des séries temporelles."""
    analyzer = TimeSeriesAnalyzer(window_size=20)
    results = await analyzer.process(time_series_data.reset_index().to_dict("records"))
    
    assert "mean" in results
    assert "std" in results
    assert "rolling_mean" in results
    assert "trend" in results
    
    assert isinstance(results["mean"], dict)
    assert "price" in results["mean"]
    assert "volume" in results["mean"]

@pytest.mark.asyncio
async def test_time_series_analyzer_analyze(time_series_data):
    """Teste l'analyse des séries temporelles."""
    analyzer = TimeSeriesAnalyzer(window_size=20)
    results = await analyzer.analyze(time_series_data)
    
    assert "trend" in results
    assert all(trend in ["up", "down"] for trend in results["trend"].values())
    
    assert "rolling_mean" in results
    assert isinstance(results["rolling_mean"], dict)
    assert all(isinstance(v, float) for v in results["rolling_mean"].values())

@pytest.mark.asyncio
async def test_statistical_analyzer_init():
    """Teste l'initialisation de l'analyseur statistique."""
    analyzer = StatisticalAnalyzer(confidence_level=0.95)
    assert analyzer.confidence_level == 0.95

@pytest.mark.asyncio
async def test_statistical_analyzer_process(statistical_data):
    """Teste le traitement des données statistiques."""
    analyzer = StatisticalAnalyzer()
    results = await analyzer.process(statistical_data.to_dict("records"))
    
    assert "describe" in results
    assert isinstance(results["describe"], dict)
    assert "values" in results["describe"]
    
    assert "values_normal_test" in results
    assert "statistic" in results["values_normal_test"]
    assert "p_value" in results["values_normal_test"]
    assert "is_normal" in results["values_normal_test"]

@pytest.mark.asyncio
async def test_statistical_analyzer_analyze(statistical_data):
    """Teste l'analyse statistique."""
    analyzer = StatisticalAnalyzer()
    results = await analyzer.analyze(statistical_data)
    
    assert "describe" in results
    assert all(stat in results["describe"]["values"] 
              for stat in ["count", "mean", "std", "min", "max"])
    
    # Test de normalité
    assert "values_normal_test" in results
    assert isinstance(results["values_normal_test"]["is_normal"], bool)

@pytest.mark.asyncio
async def test_analyzer_error_handling():
    """Teste la gestion des erreurs d'analyse."""
    analyzer = TimeSeriesAnalyzer()
    
    with pytest.raises(DataProcessingError):
        await analyzer.process({"invalid": "data"})
    
    with pytest.raises(DataProcessingError):
        await analyzer.process([])
    
    with pytest.raises(DataProcessingError):
        await analyzer.analyze(pd.DataFrame()) 