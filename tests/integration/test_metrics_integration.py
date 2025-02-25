"""Tests d'intégration pour le système de métriques."""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from typing import Dict, List

from sadie.core.collectors import BinanceTradeCollector, KrakenTradeCollector
from sadie.core.monitoring.metrics import CollectorMetricsManager
from sadie.data.collectors.base import start_metrics_manager, stop_metrics_manager
from sadie.storage import RedisStorage
from sadie.web.routes.metrics import get_collectors_metrics, get_collectors_health, get_collectors_summary

# Mocking pour éviter d'utiliser les API réelles
@pytest.fixture
def mock_binance_trades():
    """Générateur de trades Binance simulés."""
    def _generate_trade(timestamp, index):
        return {
            "e": "trade",
            "E": timestamp,
            "s": "BTCUSDT",
            "t": 100000 + index,
            "p": "45000.50",
            "q": "0.001",
            "b": 200000 + index,
            "a": 300000 + index,
            "T": timestamp - 100,
            "m": False,
            "M": True
        }
    return _generate_trade

@pytest.fixture
def mock_kraken_trades():
    """Générateur de trades Kraken simulés."""
    def _generate_trade(timestamp, index):
        return [
            0,
            [
                [
                    str(100000 + index),
                    "45000.5",
                    str(timestamp / 1000),
                    "b",
                    "l",
                    "0.001",
                    "XBTUSD"
                ]
            ],
            "trade",
            "XBT/USD"
        ]
    return _generate_trade

@pytest.fixture
async def test_storage():
    """Fixture pour le stockage de test."""
    storage = RedisStorage(
        name="test_metrics_storage",
        host="localhost",
        port=6379,
        db=15,  # Utiliser une base de données spécifique pour les tests
        socket_timeout=2
    )
    try:
        await storage.connect()
        await storage.flush_db()  # Nettoyer la base de test
        yield storage
    finally:
        await storage.flush_db()
        await storage.disconnect()

@pytest.fixture
async def metrics_manager():
    """Fixture pour le gestionnaire de métriques."""
    manager = CollectorMetricsManager(retention_period=timedelta(hours=1))
    await manager.start()
    yield manager
    await manager.stop()

@pytest.fixture
async def collectors(metrics_manager, test_storage, mock_binance_trades, mock_kraken_trades):
    """Fixture qui crée des collecteurs pour les tests."""
    # Démarrage du gestionnaire de métriques global
    await start_metrics_manager()
    
    # Création des collecteurs
    binance_collector = BinanceTradeCollector(
        name="binance_test",
        symbols=["BTCUSDT", "ETHUSDT"],
        storage=test_storage,
        api_key="test_key",
        api_secret="test_secret",
        enable_metrics=True
    )
    
    kraken_collector = KrakenTradeCollector(
        name="kraken_test",
        symbols=["XBT/USD", "ETH/USD"],
        storage=test_storage,
        api_key="test_key",
        api_secret="test_secret",
        enable_metrics=True
    )
    
    # Simulation du traitement des messages sans démarrer réellement les collecteurs
    for i in range(50):
        timestamp = int(time.time() * 1000)
        
        # Simuler le traitement de messages Binance
        if binance_collector._performance_monitor:
            binance_collector._performance_monitor.messages_received += 1
            binance_collector._performance_monitor.record_processing_time(5.0 + (i % 10))
            if i % 20 == 0:
                binance_collector._performance_monitor.record_error()
            
            if i % 2 == 0:
                binance_collector._performance_monitor.increment_trades("BTCUSDT", 1)
            else:
                binance_collector._performance_monitor.increment_trades("ETHUSDT", 1)
                
            await binance_collector._performance_monitor.record_metrics(force=(i % 10 == 0))
        
        # Simuler le traitement de messages Kraken
        if kraken_collector._performance_monitor:
            kraken_collector._performance_monitor.messages_received += 1
            kraken_collector._performance_monitor.record_processing_time(7.0 + (i % 5))
            if i % 25 == 0:
                kraken_collector._performance_monitor.record_error()
            
            if i % 2 == 0:
                kraken_collector._performance_monitor.increment_trades("XBTUSD", 1)
            else:
                kraken_collector._performance_monitor.increment_trades("ETHUSD", 1)
                
            await kraken_collector._performance_monitor.record_metrics(force=(i % 10 == 0))
        
        # Attente simulée pour générer des données sur une période
        if i % 10 == 0:
            await asyncio.sleep(0.1)
    
    yield (binance_collector, kraken_collector)
    
    # Nettoyage
    await stop_metrics_manager()

@pytest.mark.asyncio
async def test_metrics_collection_and_retrieval(collectors, metrics_manager):
    """Teste la collecte et la récupération des métriques d'intégration."""
    binance_collector, kraken_collector = collectors
    
    # Attendre que les métriques soient enregistrées
    await asyncio.sleep(0.5)
    
    # Récupérer les métriques via l'API
    all_metrics = await metrics_manager.get_metrics()
    
    # Vérifier qu'il y a des métriques
    assert len(all_metrics) > 0
    
    # Vérifier les métriques spécifiques
    binance_metrics = [m for m in all_metrics if m.name == "binance_test"]
    kraken_metrics = [m for m in all_metrics if m.name == "kraken_test"]
    
    assert len(binance_metrics) > 0
    assert len(kraken_metrics) > 0
    
    # Vérifier les types de métriques
    metric_types = set(m.metric_type for m in all_metrics)
    assert "throughput" in metric_types
    assert "latency" in metric_types
    assert "error_rate" in metric_types

@pytest.mark.asyncio
async def test_performance_monitors(collectors):
    """Teste les moniteurs de performance des collecteurs."""
    binance_collector, kraken_collector = collectors
    
    # Vérifier les rapports de performance
    binance_report = await binance_collector.get_performance_metrics()
    kraken_report = await kraken_collector.get_performance_metrics()
    
    # Vérifier les informations de base
    assert binance_report["collector"]["name"] == "binance_test"
    assert binance_report["collector"]["exchange"] == "binance"
    assert kraken_report["collector"]["name"] == "kraken_test"
    assert kraken_report["collector"]["exchange"] == "kraken"
    
    # Vérifier les statistiques
    assert binance_report["metrics"]["messages_received"] >= 50
    assert binance_report["metrics"]["trades_processed"] >= 25
    assert kraken_report["metrics"]["messages_received"] >= 50
    assert kraken_report["metrics"]["trades_processed"] >= 25
    
    # Vérifier les trades par symbole
    assert binance_report["trades"]["BTCUSDT"] >= 12
    assert binance_report["trades"]["ETHUSDT"] >= 12
    assert kraken_report["trades"]["XBTUSD"] >= 12
    assert kraken_report["trades"]["ETHUSD"] >= 12

@pytest.mark.asyncio
async def test_api_endpoints(collectors, metrics_manager):
    """Teste les endpoints API pour les métriques."""
    # Simuler un utilisateur authentifié
    mock_user = type('User', (), {'username': 'test_user', 'scopes': ['read:data']})()
    
    # Tester l'endpoint métriques des collecteurs
    metrics_response = await get_collectors_metrics(
        collector_name=None,
        exchange=None,
        metric_type=None,
        symbol=None,
        timeframe="1h",
        aggregation="avg",
        current_user=mock_user
    )
    
    # Vérifier la structure de la réponse
    assert "binance_test" in metrics_response
    assert "kraken_test" in metrics_response
    
    for collector_name in ["binance_test", "kraken_test"]:
        collector_data = metrics_response[collector_name]
        assert "throughput" in collector_data
        assert "latency" in collector_data
        assert "error_rate" in collector_data
    
    # Tester l'endpoint santé des collecteurs
    health_response = await get_collectors_health(
        collector_name=None,
        exchange=None,
        current_user=mock_user
    )
    
    # Vérifier la structure de la réponse
    assert "collectors" in health_response
    assert len(health_response["collectors"]) >= 2
    
    for collector in health_response["collectors"]:
        assert "name" in collector
        assert "status" in collector
        assert "last_update" in collector
    
    # Tester l'endpoint résumé des collecteurs
    summary_response = await get_collectors_summary(current_user=mock_user)
    
    # Vérifier la structure de la réponse
    assert "summary" in summary_response
    assert "collectors" in summary_response
    assert "timestamp" in summary_response
    
    assert len(summary_response["collectors"]) >= 2
    assert "total_trades" in summary_response["summary"]
    assert "avg_latency" in summary_response["summary"]
    assert "error_rate" in summary_response["summary"] 