"""Tests unitaires pour le système de métriques de performance."""

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from sadie.core.monitoring.metrics import (
    CollectorMetric,
    CollectorMetricsManager,
    CollectorPerformanceMonitor
)

@pytest.fixture
def metrics_manager():
    """Fixture pour le gestionnaire de métriques."""
    return CollectorMetricsManager(retention_period=timedelta(hours=1))

@pytest.fixture
def performance_monitor(metrics_manager):
    """Fixture pour le moniteur de performance."""
    return CollectorPerformanceMonitor(
        collector_name="test_collector",
        exchange="test_exchange",
        symbols=["BTC/USD", "ETH/USD"],
        metrics_manager=metrics_manager
    )

class TestCollectorMetric:
    """Tests pour la classe CollectorMetric."""
    
    def test_metric_init(self):
        """Test l'initialisation d'une métrique."""
        metric = CollectorMetric(
            name="test_collector",
            exchange="binance",
            symbols=["BTCUSDT"],
            metric_type="throughput",
            value=42.0,
            unit="tps"
        )
        
        assert metric.name == "test_collector"
        assert metric.exchange == "binance"
        assert metric.symbols == ["BTCUSDT"]
        assert metric.metric_type == "throughput"
        assert metric.value == 42.0
        assert metric.unit == "tps"
        assert isinstance(metric.timestamp, datetime)
    
    def test_metric_to_dict(self):
        """Test la conversion d'une métrique en dictionnaire."""
        timestamp = datetime.utcnow()
        metric = CollectorMetric(
            name="test_collector",
            exchange="binance",
            symbols=["BTCUSDT"],
            metric_type="latency",
            value=5.2,
            timestamp=timestamp,
            unit="ms",
            labels={"priority": "high"}
        )
        
        metric_dict = metric.to_dict()
        assert metric_dict["name"] == "test_collector"
        assert metric_dict["exchange"] == "binance"
        assert metric_dict["symbols"] == ["BTCUSDT"]
        assert metric_dict["type"] == "latency"
        assert metric_dict["value"] == 5.2
        assert metric_dict["timestamp"] == timestamp.isoformat()
        assert metric_dict["unit"] == "ms"
        assert metric_dict["labels"] == {"priority": "high"}

@pytest.mark.asyncio
class TestCollectorMetricsManager:
    """Tests pour la classe CollectorMetricsManager."""
    
    async def test_add_get_metrics(self, metrics_manager):
        """Test l'ajout et la récupération de métriques."""
        # Ajout de métriques
        metric1 = CollectorMetric(
            name="test_collector",
            exchange="binance",
            symbols=["BTCUSDT"],
            metric_type="throughput",
            value=10.0
        )
        
        metric2 = CollectorMetric(
            name="test_collector",
            exchange="binance",
            symbols=["ETHUSDT"],
            metric_type="latency",
            value=15.0
        )
        
        await metrics_manager.add_metric(metric1)
        await metrics_manager.add_metric(metric2)
        
        # Récupération de toutes les métriques
        all_metrics = await metrics_manager.get_metrics()
        assert len(all_metrics) == 2
        
        # Récupération filtrée par type
        throughput_metrics = await metrics_manager.get_metrics(metric_type="throughput")
        assert len(throughput_metrics) == 1
        assert throughput_metrics[0].value == 10.0
        
        # Récupération filtrée par symbole
        eth_metrics = await metrics_manager.get_metrics(symbol="ETHUSDT")
        assert len(eth_metrics) == 1
        assert eth_metrics[0].value == 15.0
    
    async def test_cleanup(self, metrics_manager):
        """Test le nettoyage des métriques obsolètes."""
        # Métrique récente
        recent_metric = CollectorMetric(
            name="test_collector",
            exchange="binance",
            symbols=["BTCUSDT"],
            metric_type="throughput",
            value=10.0,
            timestamp=datetime.utcnow()
        )
        
        # Métrique ancienne (hors période de rétention)
        old_timestamp = datetime.utcnow() - timedelta(hours=2)
        old_metric = CollectorMetric(
            name="test_collector",
            exchange="binance",
            symbols=["BTCUSDT"],
            metric_type="throughput",
            value=5.0,
            timestamp=old_timestamp
        )
        
        await metrics_manager.add_metric(recent_metric)
        await metrics_manager.add_metric(old_metric)
        
        # Vérification avant nettoyage
        all_metrics = await metrics_manager.get_metrics()
        assert len(all_metrics) == 2
        
        # Nettoyage
        await metrics_manager.cleanup()
        
        # Vérification après nettoyage
        all_metrics = await metrics_manager.get_metrics()
        assert len(all_metrics) == 1
        assert all_metrics[0].value == 10.0

@pytest.mark.asyncio
class TestCollectorPerformanceMonitor:
    """Tests pour la classe CollectorPerformanceMonitor."""
    
    async def test_record_processing_time(self, performance_monitor):
        """Test l'enregistrement des temps de traitement."""
        # Enregistrement de quelques temps de traitement
        performance_monitor.record_processing_time(10.5)
        performance_monitor.record_processing_time(15.2)
        performance_monitor.record_processing_time(12.3)
        
        assert len(performance_monitor.processing_times) == 3
        assert performance_monitor.processing_times[0] == 10.5
        assert performance_monitor.processing_times[1] == 15.2
        assert performance_monitor.processing_times[2] == 12.3
    
    async def test_record_error(self, performance_monitor):
        """Test l'enregistrement des erreurs et l'impact sur le statut de santé."""
        assert performance_monitor.health_status == "initializing"
        
        # Enregistrement de quelques erreurs
        performance_monitor.record_error()
        performance_monitor.record_error()
        performance_monitor.record_error()
        
        assert performance_monitor.errors_count == 3
        assert performance_monitor.health_status == "initializing"
        
        # Une erreur supplémentaire devrait dégrader le statut
        performance_monitor.record_error()
        assert performance_monitor.errors_count == 4
        assert performance_monitor.health_status == "degraded"
        
        # Beaucoup d'erreurs devraient rendre le statut unhealthy
        for _ in range(7):
            performance_monitor.record_error()
        
        assert performance_monitor.errors_count == 11
        assert performance_monitor.health_status == "unhealthy"
    
    async def test_increment_trades(self, performance_monitor):
        """Test l'incrémentation des compteurs de trades."""
        performance_monitor.increment_trades("BTC/USD", 5)
        performance_monitor.increment_trades("ETH/USD", 3)
        
        assert performance_monitor.trades_processed == 8
        assert performance_monitor.trades_per_symbol["BTC/USD"] == 5
        assert performance_monitor.trades_per_symbol["ETH/USD"] == 3
        assert "BTC/USD" in performance_monitor.last_trades
        assert "ETH/USD" in performance_monitor.last_trades
    
    @patch('sadie.core.monitoring.metrics.CollectorMetricsManager.add_metric')
    async def test_record_metrics(self, mock_add_metric, performance_monitor):
        """Test l'enregistrement des métriques dans le gestionnaire."""
        # Configuration initiale
        performance_monitor.messages_received = 100
        performance_monitor.trades_processed = 80
        performance_monitor.errors_count = 2
        performance_monitor.record_processing_time(5.0)
        performance_monitor.record_processing_time(10.0)
        performance_monitor.record_processing_time(15.0)
        
        # Forcer l'enregistrement des métriques
        await performance_monitor.record_metrics(force=True)
        
        # Vérifier que add_metric a été appelé plusieurs fois
        assert mock_add_metric.call_count >= 4  # Au moins 4 métriques différentes
    
    async def test_get_performance_report(self, performance_monitor):
        """Test la génération du rapport de performance."""
        # Configuration initiale
        performance_monitor.messages_received = 100
        performance_monitor.trades_processed = 80
        performance_monitor.errors_count = 2
        performance_monitor.record_processing_time(5.0)
        performance_monitor.record_processing_time(10.0)
        performance_monitor.record_processing_time(15.0)
        performance_monitor.increment_trades("BTC/USD", 50)
        performance_monitor.increment_trades("ETH/USD", 30)
        
        # Génération du rapport
        report = await performance_monitor.get_performance_report()
        
        # Vérification du contenu du rapport
        assert "collector" in report
        assert "metrics" in report
        assert "trades" in report
        
        assert report["collector"]["name"] == "test_collector"
        assert report["collector"]["exchange"] == "test_exchange"
        assert report["collector"]["symbols"] == ["BTC/USD", "ETH/USD"]
        
        assert report["metrics"]["messages_received"] == 100
        assert report["metrics"]["trades_processed"] == 80
        assert report["metrics"]["errors_count"] == 2
        assert "avg_processing_time" in report["metrics"]
        
        assert report["trades"]["BTC/USD"] == 50
        assert report["trades"]["ETH/USD"] == 30 