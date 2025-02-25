"""Tests unitaires pour le système d'alertes de performances."""

import asyncio
import json
from datetime import datetime, timedelta
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sadie.core.monitoring.alerts import (
    PerformanceThreshold, 
    PerformanceAlert,
    PerformanceAlertManager,
    NotificationManager
)
from sadie.core.monitoring.metrics import CollectorMetric, CollectorMetricsManager


@pytest.fixture
def threshold():
    """Fixture pour un seuil d'alerte."""
    return PerformanceThreshold(
        metric_type="error_rate",
        operator=">",
        value=5.0,
        duration=60,
        cooldown=300
    )


@pytest.fixture
def sample_metric():
    """Fixture pour une métrique de collecteur."""
    return CollectorMetric(
        name="test_collector",
        exchange="binance",
        symbols=["BTC/USD"],
        metric_type="error_rate",
        value=10.0,
        unit="%"
    )


@pytest.fixture
def alert():
    """Fixture pour une alerte de performance."""
    threshold = PerformanceThreshold(
        metric_type="error_rate",
        operator=">",
        value=5.0,
        duration=60,
        cooldown=300
    )
    
    return PerformanceAlert(
        id="test-alert-001",
        name="Test Alert",
        collector_name="test_collector",
        exchange="binance",
        symbols=["BTC/USD"],
        thresholds=[threshold],
        notification_channels=["log", "console"]
    )


@pytest.fixture
def metrics_manager():
    """Fixture pour le gestionnaire de métriques."""
    return CollectorMetricsManager()


@pytest.fixture
def alert_manager(metrics_manager):
    """Fixture pour le gestionnaire d'alertes."""
    return PerformanceAlertManager(metrics_manager)


class TestPerformanceThreshold:
    """Tests pour la classe PerformanceThreshold."""
    
    def test_threshold_init(self, threshold):
        """Test de l'initialisation du seuil."""
        assert threshold.metric_type == "error_rate"
        assert threshold.operator == ">"
        assert threshold.value == 5.0
        assert threshold.duration == 60
        assert threshold.cooldown == 300
        assert threshold.enabled is True
    
    def test_threshold_to_dict(self, threshold):
        """Test de la conversion en dictionnaire."""
        data = threshold.to_dict()
        assert data["metric_type"] == "error_rate"
        assert data["operator"] == ">"
        assert data["value"] == 5.0
        assert data["duration"] == 60
        assert data["cooldown"] == 300
        assert data["enabled"] is True
    
    def test_apply_operators(self):
        """Test des différents opérateurs de seuil."""
        # Tests pour l'opérateur >
        threshold = PerformanceThreshold("throughput", ">", 100.0)
        assert threshold.apply(150.0) is True
        assert threshold.apply(50.0) is False
        
        # Tests pour l'opérateur <
        threshold = PerformanceThreshold("latency", "<", 200.0)
        assert threshold.apply(150.0) is True
        assert threshold.apply(250.0) is False
        
        # Tests pour l'opérateur >=
        threshold = PerformanceThreshold("throughput", ">=", 100.0)
        assert threshold.apply(100.0) is True
        assert threshold.apply(99.0) is False
        
        # Tests pour l'opérateur <=
        threshold = PerformanceThreshold("latency", "<=", 200.0)
        assert threshold.apply(200.0) is True
        assert threshold.apply(201.0) is False
        
        # Tests pour l'opérateur ==
        threshold = PerformanceThreshold("health", "==", 1.0)
        assert threshold.apply(1.0) is True
        assert threshold.apply(0.0) is False
        
        # Tests pour l'opérateur !=
        threshold = PerformanceThreshold("health", "!=", 0.0)
        assert threshold.apply(1.0) is True
        assert threshold.apply(0.0) is False
        
        # Test pour un opérateur inconnu
        threshold = PerformanceThreshold("health", "invalid", 1.0)
        assert threshold.apply(1.0) is False


class TestPerformanceAlert:
    """Tests pour la classe PerformanceAlert."""
    
    def test_alert_init(self, alert):
        """Test de l'initialisation de l'alerte."""
        assert alert.id == "test-alert-001"
        assert alert.name == "Test Alert"
        assert alert.collector_name == "test_collector"
        assert alert.exchange == "binance"
        assert alert.symbols == ["BTC/USD"]
        assert len(alert.thresholds) == 1
        assert alert.notification_channels == ["log", "console"]
        assert alert.trigger_count == 0
        assert alert.last_triggered is None
    
    def test_alert_to_dict(self, alert):
        """Test de la conversion en dictionnaire."""
        data = alert.to_dict()
        assert data["id"] == "test-alert-001"
        assert data["name"] == "Test Alert"
        assert data["collector_name"] == "test_collector"
        assert data["exchange"] == "binance"
        assert data["symbols"] == ["BTC/USD"]
        assert len(data["thresholds"]) == 1
        assert data["notification_channels"] == ["log", "console"]
        assert data["trigger_count"] == 0
        assert data["last_triggered"] is None
    
    def test_is_applicable(self, alert, sample_metric):
        """Test de la vérification d'applicabilité."""
        # Métrique correspondante
        assert alert.is_applicable(sample_metric) is True
        
        # Métrique avec collecteur différent
        different_collector = CollectorMetric(
            name="other_collector",
            exchange="binance",
            symbols=["BTC/USD"],
            metric_type="error_rate",
            value=10.0
        )
        assert alert.is_applicable(different_collector) is False
        
        # Métrique avec exchange différent
        different_exchange = CollectorMetric(
            name="test_collector",
            exchange="kraken",
            symbols=["BTC/USD"],
            metric_type="error_rate",
            value=10.0
        )
        assert alert.is_applicable(different_exchange) is False
        
        # Métrique avec symbole différent
        different_symbol = CollectorMetric(
            name="test_collector",
            exchange="binance",
            symbols=["ETH/USD"],
            metric_type="error_rate",
            value=10.0
        )
        assert alert.is_applicable(different_symbol) is False
        
        # Métrique avec type de métrique différent
        different_metric_type = CollectorMetric(
            name="test_collector",
            exchange="binance",
            symbols=["BTC/USD"],
            metric_type="latency",
            value=10.0
        )
        assert alert.is_applicable(different_metric_type) is False
    
    def test_should_trigger(self, alert):
        """Test de la vérification du déclenchement."""
        # Valeur dépassant le seuil
        assert alert.should_trigger(10.0, "error_rate") is True
        
        # Valeur ne dépassant pas le seuil
        assert alert.should_trigger(3.0, "error_rate") is False
        
        # Type de métrique non configuré
        assert alert.should_trigger(10.0, "latency") is False
        
        # Test du cooldown
        alert.last_triggered = datetime.utcnow() - timedelta(seconds=100)
        assert alert.should_trigger(10.0, "error_rate") is False
        
        # Après le cooldown
        alert.last_triggered = datetime.utcnow() - timedelta(seconds=350)
        assert alert.should_trigger(10.0, "error_rate") is True
    
    def test_trigger(self, alert):
        """Test du déclenchement de l'alerte."""
        data = alert.trigger()
        
        assert data["alert_id"] == "test-alert-001"
        assert data["alert_name"] == "Test Alert"
        assert "triggered_at" in data
        assert data["trigger_count"] == 1
        assert data["notification_channels"] == ["log", "console"]
        assert data["collector_name"] == "test_collector"
        assert data["exchange"] == "binance"
        assert data["symbols"] == ["BTC/USD"]
        
        assert alert.trigger_count == 1
        assert alert.last_triggered is not None


@pytest.mark.asyncio
class TestPerformanceAlertManager:
    """Tests pour le gestionnaire d'alertes."""
    
    async def test_add_get_alerts(self, alert_manager, alert):
        """Test d'ajout et de récupération d'alertes."""
        # Ajout d'une alerte
        alert_id = alert_manager.add_alert(alert)
        assert alert_id == "test-alert-001"
        
        # Récupération de toutes les alertes
        alerts = alert_manager.get_alerts()
        assert len(alerts) == 1
        assert alerts[0].id == "test-alert-001"
        
        # Récupération d'une alerte spécifique
        specific_alert = alert_manager.get_alert("test-alert-001")
        assert specific_alert is not None
        assert specific_alert.id == "test-alert-001"
        assert specific_alert.name == "Test Alert"
        
        # Récupération d'une alerte inexistante
        nonexistent_alert = alert_manager.get_alert("nonexistent")
        assert nonexistent_alert is None
    
    async def test_update_alert(self, alert_manager, alert):
        """Test de mise à jour d'une alerte."""
        # Ajout d'une alerte
        alert_manager.add_alert(alert)
        
        # Mise à jour de l'alerte
        updated = alert_manager.update_alert("test-alert-001", {
            "name": "Updated Alert Name",
            "notification_channels": ["log", "console", "email"]
        })
        assert updated is True
        
        # Vérification de la mise à jour
        updated_alert = alert_manager.get_alert("test-alert-001")
        assert updated_alert.name == "Updated Alert Name"
        assert updated_alert.notification_channels == ["log", "console", "email"]
        assert updated_alert.collector_name == "test_collector"  # Non modifié
        
        # Mise à jour d'une alerte inexistante
        updated = alert_manager.update_alert("nonexistent", {
            "name": "Will Not Update"
        })
        assert updated is False
    
    async def test_delete_alert(self, alert_manager, alert):
        """Test de suppression d'une alerte."""
        # Ajout d'une alerte
        alert_manager.add_alert(alert)
        
        # Suppression de l'alerte
        deleted = alert_manager.delete_alert("test-alert-001")
        assert deleted is True
        
        # Vérification que l'alerte a été supprimée
        alerts = alert_manager.get_alerts()
        assert len(alerts) == 0
        
        # Suppression d'une alerte inexistante
        deleted = alert_manager.delete_alert("nonexistent")
        assert deleted is False
    
    @patch('sadie.core.monitoring.alerts.NotificationManager.send_notification')
    async def test_check_alerts(self, mock_send_notification, alert_manager, alert, sample_metric):
        """Test de la vérification des alertes."""
        # Configuration du gestionnaire de métriques
        metrics_manager = alert_manager._metrics_manager
        await metrics_manager.add_metric(sample_metric)
        
        # Ajout d'une alerte
        alert_manager.add_alert(alert)
        
        # Vérification des alertes
        await alert_manager._check_alerts()
        
        # Vérification que la notification a été envoyée
        assert mock_send_notification.call_count == 2  # Une fois pour chaque canal ("log", "console")
        
        # Vérification de l'historique des alertes
        history = alert_manager.get_alert_history()
        assert len(history) == 1
        assert history[0]["alert_id"] == "test-alert-001"
        assert history[0]["alert_name"] == "Test Alert"


class TestNotificationManager:
    """Tests pour le gestionnaire de notifications."""
    
    def test_register_channel(self):
        """Test d'enregistrement d'un canal de notification."""
        mock_handler = MagicMock()
        manager = NotificationManager()
        
        # Enregistrement d'un nouveau canal
        manager.register_channel("test_channel", mock_handler)
        
        # Vérification que le canal a été enregistré
        assert "test_channel" in manager._channels
        assert manager._channels["test_channel"] == mock_handler
    
    @patch('sadie.core.monitoring.alerts.logger.info')
    def test_send_notification(self, mock_logger, alert):
        """Test d'envoi de notification."""
        manager = NotificationManager()
        alert_data = alert.trigger()
        
        # Test du canal "log"
        manager.send_notification("log", alert_data)
        mock_logger.assert_called_once()
        
        # Test d'un canal non enregistré
        manager.send_notification("unknown_channel", alert_data)
        # Pas d'erreur mais pas d'action non plus 