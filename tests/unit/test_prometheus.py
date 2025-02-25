"""Tests unitaires pour l'exportation Prometheus des métriques."""

import pytest
from unittest.mock import patch, MagicMock, call

from sadie.core.monitoring.prometheus_exporter import (
    PrometheusExporter,
    COLLECTOR_THROUGHPUT,
    COLLECTOR_LATENCY,
    COLLECTOR_ERROR_RATE,
    COLLECTOR_HEALTH,
    COLLECTOR_TOTAL_MESSAGES,
    COLLECTOR_TOTAL_ERRORS,
    COLLECTOR_INFO
)


@pytest.fixture
def prometheus_exporter():
    """Fixture pour l'exportateur Prometheus."""
    with patch('sadie.core.monitoring.prometheus_exporter.start_http_server') as mock_start:
        exporter = PrometheusExporter(port=9090, refresh_interval=15)
        yield exporter


class TestPrometheusExporter:
    """Tests pour l'exportateur Prometheus."""
    
    def test_init(self, prometheus_exporter):
        """Test de l'initialisation de l'exportateur."""
        assert prometheus_exporter.port == 9090
        assert prometheus_exporter.refresh_interval == 15
        assert prometheus_exporter.running is False
        assert prometheus_exporter.thread is None
        assert prometheus_exporter._collector_info_exported == set()
    
    def test_start_stop(self, prometheus_exporter):
        """Test du démarrage et de l'arrêt de l'exportateur."""
        with patch('sadie.core.monitoring.prometheus_exporter.threading.Thread') as mock_thread:
            # Test du démarrage
            prometheus_exporter.start()
            
            assert prometheus_exporter.running is True
            mock_thread.assert_called_once()
            
            # Test du démarrage lorsque déjà démarré
            prometheus_exporter.start()
            assert mock_thread.call_count == 1  # Pas d'appel supplémentaire
            
            # Test de l'arrêt
            prometheus_exporter.stop()
            
            assert prometheus_exporter.running is False
            prometheus_exporter.thread.join.assert_called_once_with(timeout=5.0)
            
            # Test de l'arrêt lorsque déjà arrêté
            prometheus_exporter.thread = None
            prometheus_exporter.stop()
            # Ne devrait pas lever d'exception
    
    @patch('sadie.core.monitoring.prometheus_exporter.time.sleep')
    def test_refresh_metrics_loop(self, mock_sleep, prometheus_exporter):
        """Test de la boucle de rafraîchissement des métriques."""
        # Configuration du mock pour _refresh_metrics
        prometheus_exporter._refresh_metrics = MagicMock()
        
        # Configurer une exécution unique
        mock_sleep.side_effect = [None, Exception("Stop loop")]
        
        prometheus_exporter.running = True
        
        # Exécution de la boucle (qui s'arrêtera après 2 itérations)
        try:
            prometheus_exporter._refresh_metrics_loop()
        except Exception as e:
            assert str(e) == "Stop loop"
        
        # Vérifications
        assert prometheus_exporter._refresh_metrics.call_count == 1
        mock_sleep.assert_called_once_with(15)
    
    @pytest.mark.asyncio
    async def test_update_prometheus_metrics(self, prometheus_exporter):
        """Test de la mise à jour des métriques Prometheus."""
        # Création de métriques de test
        mock_metric1 = MagicMock()
        mock_metric1.name = "test_collector"
        mock_metric1.exchange = "binance"
        mock_metric1.symbols = ["BTC/USD"]
        mock_metric1.metric_type = "throughput"
        mock_metric1.value = 100.5
        mock_metric1.timestamp.isoformat.return_value = "2024-05-01T10:00:00"
        
        mock_metric2 = MagicMock()
        mock_metric2.name = "test_collector"
        mock_metric2.exchange = "binance"
        mock_metric2.symbols = ["BTC/USD"]
        mock_metric2.metric_type = "latency"
        mock_metric2.value = 5.2
        mock_metric2.timestamp.isoformat.return_value = "2024-05-01T10:00:00"
        
        mock_metric3 = MagicMock()
        mock_metric3.name = "test_collector"
        mock_metric3.exchange = "binance"
        mock_metric3.symbols = ["BTC/USD"]
        mock_metric3.metric_type = "error_rate"
        mock_metric3.value = 2.5
        mock_metric3.metadata = {"throughput_value": 100.0}
        mock_metric3.timestamp.isoformat.return_value = "2024-05-01T10:00:00"
        
        mock_metric4 = MagicMock()
        mock_metric4.name = "test_collector"
        mock_metric4.exchange = "binance"
        mock_metric4.symbols = ["BTC/USD"]
        mock_metric4.metric_type = "health"
        mock_metric4.value = 1.0
        mock_metric4.timestamp.isoformat.return_value = "2024-05-01T10:00:00"
        
        metrics = [mock_metric1, mock_metric2, mock_metric3, mock_metric4]
        
        # Patching des métriques Prometheus
        with patch('sadie.core.monitoring.prometheus_exporter.COLLECTOR_THROUGHPUT') as mock_throughput, \
             patch('sadie.core.monitoring.prometheus_exporter.COLLECTOR_LATENCY') as mock_latency, \
             patch('sadie.core.monitoring.prometheus_exporter.COLLECTOR_ERROR_RATE') as mock_error_rate, \
             patch('sadie.core.monitoring.prometheus_exporter.COLLECTOR_HEALTH') as mock_health, \
             patch('sadie.core.monitoring.prometheus_exporter.COLLECTOR_TOTAL_MESSAGES') as mock_total_messages, \
             patch('sadie.core.monitoring.prometheus_exporter.COLLECTOR_TOTAL_ERRORS') as mock_total_errors, \
             patch('sadie.core.monitoring.prometheus_exporter.COLLECTOR_INFO') as mock_info:
            
            # Configuration des mocks pour les métriques
            mock_throughput.labels.return_value.set = MagicMock()
            mock_latency.labels.return_value.set = MagicMock()
            mock_error_rate.labels.return_value.set = MagicMock()
            mock_health.labels.return_value.set = MagicMock()
            mock_total_messages.labels.return_value.inc = MagicMock()
            mock_total_errors.labels.return_value.inc = MagicMock()
            mock_info.labels.return_value.info = MagicMock()
            
            # Exécution de la fonction à tester
            prometheus_exporter._update_prometheus_metrics(metrics)
            
            # Vérifications
            mock_throughput.labels.assert_called_once_with(
                collector_name="test_collector",
                exchange="binance",
                symbol="BTC/USD"
            )
            mock_throughput.labels.return_value.set.assert_called_once_with(100.5)
            
            mock_latency.labels.assert_called_once_with(
                collector_name="test_collector",
                exchange="binance",
                symbol="BTC/USD"
            )
            mock_latency.labels.return_value.set.assert_called_once_with(5.2)
            
            mock_error_rate.labels.assert_called_once_with(
                collector_name="test_collector",
                exchange="binance",
                symbol="BTC/USD"
            )
            mock_error_rate.labels.return_value.set.assert_called_once_with(2.5)
            
            mock_health.labels.assert_called_once_with(
                collector_name="test_collector",
                exchange="binance",
                symbol="BTC/USD"
            )
            mock_health.labels.return_value.set.assert_called_once_with(1.0)
            
            mock_total_messages.labels.assert_called_once_with(
                collector_name="test_collector",
                exchange="binance",
                symbol="BTC/USD"
            )
            mock_total_messages.labels.return_value.inc.assert_called_once_with(100)
            
            mock_total_errors.labels.assert_called_once_with(
                collector_name="test_collector",
                exchange="binance",
                symbol="BTC/USD"
            )
            mock_total_errors.labels.return_value.inc.assert_called_once_with(2)
            
            mock_info.labels.assert_called_once_with(
                collector_name="test_collector",
                exchange="binance"
            )
            mock_info.labels.return_value.info.assert_called_once_with({
                'collector_name': "test_collector",
                'exchange': "binance",
                'symbols': "BTC/USD",
                'first_seen': "2024-05-01T10:00:00"
            })


@pytest.mark.asyncio
class TestPrometheusRoutes:
    """Tests pour les routes API Prometheus."""
    
    async def test_configure_prometheus(self):
        """Test de la configuration de l'exportateur Prometheus."""
        from sadie.web.routes.prometheus import configure_prometheus
        
        # Mock des fonctions d'exportation Prometheus
        with patch('sadie.web.routes.prometheus.start_prometheus_exporter') as mock_start, \
             patch('sadie.web.routes.prometheus.stop_prometheus_exporter') as mock_stop, \
             patch('sadie.web.routes.prometheus.global_prometheus_exporter') as mock_exporter:
            
            # Configuration du mock de l'exportateur
            mock_exporter.running = False
            mock_exporter.port = 9090
            
            # Test d'activation de l'exportateur
            response = await configure_prometheus(
                config={"enabled": True, "port": 9090},
                current_user=MagicMock(is_admin=True)
            )
            
            mock_start.assert_called_once_with(port=9090)
            assert response.enabled is False  # Car le mock renvoie False
            
            # Réinitialisation des mocks
            mock_start.reset_mock()
            mock_stop.reset_mock()
            
            # Test de désactivation de l'exportateur
            mock_exporter.running = True
            
            response = await configure_prometheus(
                config={"enabled": False, "port": 9090},
                current_user=MagicMock(is_admin=True)
            )
            
            mock_stop.assert_called_once()
            assert response.enabled is True  # Car le mock renvoie True
    
    async def test_get_prometheus_status(self):
        """Test de la récupération du statut de l'exportateur Prometheus."""
        from sadie.web.routes.prometheus import get_prometheus_status
        
        # Mock de l'exportateur Prometheus
        with patch('sadie.web.routes.prometheus.global_prometheus_exporter') as mock_exporter:
            # Configuration du mock
            mock_exporter.running = True
            mock_exporter.port = 9090
            
            # Exécution de la fonction
            response = await get_prometheus_status(
                current_user=MagicMock()
            )
            
            # Vérifications
            assert response.enabled is True
            assert response.port == 9090
            
            # Test avec exportateur désactivé
            mock_exporter.running = False
            mock_exporter.port = None
            
            response = await get_prometheus_status(
                current_user=MagicMock()
            )
            
            assert response.enabled is False
            assert response.port is None 