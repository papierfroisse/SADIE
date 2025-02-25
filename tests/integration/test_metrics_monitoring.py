#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests d'intégration pour les fonctionnalités de monitoring avancées.
Ces tests vérifient l'intégration entre les différentes composantes du système de métriques:
- Collecte des métriques
- Alertes basées sur les seuils
- Notification des alertes
- Exportation des métriques
- Intégration avec Prometheus
"""

import asyncio
import json
import os
import pytest
import time
from datetime import datetime, timedelta
import tempfile
import requests
from unittest.mock import patch, MagicMock, AsyncMock

# Import des modules à tester
from sadie.core.monitoring.alerts import PerformanceThreshold, PerformanceAlert, AlertManager
from sadie.core.monitoring.metrics import CollectorMetricsManager, CollectorMetric
from sadie.core.monitoring.dashboards import DashboardManager, Widget
from sadie.core.monitoring.export import MetricsExporter
from sadie.core.monitoring.prometheus_exporter import PrometheusExporter
from sadie.core.collectors.binance_collector import BinanceCollector
from sadie.core.monitoring.notification import NotificationManager, EmailChannel, WebhookChannel


@pytest.fixture
def metrics_manager():
    """Fixture pour le gestionnaire de métriques."""
    manager = CollectorMetricsManager()
    
    # Ajouter quelques métriques de test
    for i in range(10):
        timestamp = datetime.now() - timedelta(minutes=i)
        
        # Métriques pour Binance
        binance_metrics = CollectorMetric(
            collector_id="binance_collector",
            timestamp=timestamp,
            latency=100 + (i * 10),
            memory_usage=250 + i,
            cpu_usage=10 + i,
            requests_per_minute=100 - i
        )
        manager.add_metric(binance_metrics)
        
        # Métriques pour Kraken
        kraken_metrics = CollectorMetric(
            collector_id="kraken_collector",
            timestamp=timestamp,
            latency=120 + (i * 5),
            memory_usage=300 - i,
            cpu_usage=15 + i,
            requests_per_minute=80 - i
        )
        manager.add_metric(kraken_metrics)
    
    return manager


@pytest.fixture
def alert_manager():
    """Fixture pour le gestionnaire d'alertes."""
    manager = AlertManager()
    
    # Créer quelques alertes de test
    latency_alert = PerformanceAlert(
        name="Test Latence Élevée",
        description="Alerte de test pour latence élevée",
        collector_id="binance_collector",
        threshold=PerformanceThreshold('latency', '>', 150),
        severity="warning"
    )
    
    memory_alert = PerformanceAlert(
        name="Test Mémoire Élevée",
        description="Alerte de test pour utilisation mémoire élevée",
        collector_id="kraken_collector",
        threshold=PerformanceThreshold('memory_usage', '>', 290),
        severity="critical"
    )
    
    manager.add_alert(latency_alert)
    manager.add_alert(memory_alert)
    
    return manager


@pytest.fixture
def notification_manager():
    """Fixture pour le gestionnaire de notifications."""
    manager = NotificationManager()
    
    # Ajouter des canaux de notification mockés
    email_channel = EmailChannel(recipients=["admin@example.com"])
    webhook_channel = WebhookChannel(url="https://webhook.example.com/alerts")
    
    # Remplacer les méthodes d'envoi par des mocks
    email_channel.send = MagicMock(return_value=True)
    webhook_channel.send = MagicMock(return_value=True)
    
    manager.register_channel("email", email_channel)
    manager.register_channel("webhook", webhook_channel)
    
    return manager


@pytest.fixture
def prometheus_exporter():
    """Fixture pour l'exportateur Prometheus."""
    exporter = PrometheusExporter()
    return exporter


@pytest.mark.asyncio
async def test_alert_triggering_and_notification(metrics_manager, alert_manager, notification_manager):
    """Test l'intégration entre la détection d'alertes et les notifications."""
    
    # Connecter le gestionnaire d'alertes au gestionnaire de notifications
    alert_manager.notification_manager = notification_manager
    
    # Créer une métrique qui déclenchera une alerte
    trigger_metric = CollectorMetric(
        collector_id="binance_collector",
        timestamp=datetime.now(),
        latency=200,  # > 150, déclenchera l'alerte de latence
        memory_usage=280,
        cpu_usage=20,
        requests_per_minute=95
    )
    
    # Ajouter la métrique et vérifier les alertes
    metrics_manager.add_metric(trigger_metric)
    triggered_alerts = alert_manager.check_alerts(trigger_metric)
    
    # Vérifier qu'une alerte a été déclenchée
    assert len(triggered_alerts) == 1
    assert triggered_alerts[0].name == "Test Latence Élevée"
    
    # Vérifier que la notification a été envoyée
    notification_manager.channels["email"].send.assert_called_once()
    notification_manager.channels["webhook"].send.assert_called_once()
    
    # Vérifier le contenu de la notification
    call_args = notification_manager.channels["email"].send.call_args[0][0]
    assert "Test Latence Élevée" in call_args
    assert "200" in call_args  # La valeur de la métrique


@pytest.mark.asyncio
async def test_metrics_export_integration(metrics_manager):
    """Test l'intégration de l'exportation des métriques."""
    
    # Créer un exportateur
    exporter = MetricsExporter(metrics_manager)
    
    # Exporter au format JSON
    json_data = exporter.export_json(
        collector_id="binance_collector",
        start_time=datetime.now() - timedelta(minutes=15),
        end_time=datetime.now()
    )
    
    # Vérifier le format JSON
    json_result = json.loads(json_data)
    assert "collector_id" in json_result
    assert json_result["collector_id"] == "binance_collector"
    assert "metrics" in json_result
    assert len(json_result["metrics"]) > 0
    
    # Exporter au format CSV
    csv_data = exporter.export_csv(
        collector_id="kraken_collector",
        metrics=["latency", "cpu_usage"],
        start_time=datetime.now() - timedelta(minutes=15),
        end_time=datetime.now()
    )
    
    # Vérifier le format CSV
    csv_lines = csv_data.strip().split("\n")
    assert len(csv_lines) > 1  # Au moins l'en-tête et une ligne de données
    assert "timestamp,latency,cpu_usage" in csv_lines[0]


@pytest.mark.asyncio
async def test_prometheus_integration(metrics_manager, prometheus_exporter):
    """Test l'intégration avec Prometheus."""
    
    # Simuler des collecteurs
    binance_collector = MagicMock()
    binance_collector.__class__.__name__ = "BinanceCollector"
    binance_collector.collector_id = "binance_collector"
    
    kraken_collector = MagicMock()
    kraken_collector.__class__.__name__ = "KrakenCollector"
    kraken_collector.collector_id = "kraken_collector"
    
    # Enregistrer les collecteurs auprès de l'exportateur Prometheus
    prometheus_exporter.register_collector(binance_collector)
    prometheus_exporter.register_collector(kraken_collector)
    
    # Récupérer les dernières métriques pour chaque collecteur
    binance_metrics = None
    kraken_metrics = None
    for metric in metrics_manager.get_metrics():
        if metric.collector_id == "binance_collector" and (binance_metrics is None or metric.timestamp > binance_metrics.timestamp):
            binance_metrics = metric
        elif metric.collector_id == "kraken_collector" and (kraken_metrics is None or metric.timestamp > kraken_metrics.timestamp):
            kraken_metrics = metric
    
    # Mise à jour des métriques Prometheus
    prometheus_exporter.update_metrics(binance_metrics)
    prometheus_exporter.update_metrics(kraken_metrics)
    
    # Récupérer les métriques au format Prometheus
    metrics_output = prometheus_exporter.get_metrics()
    
    # Vérifier le format des métriques Prometheus
    assert "sadie_collector_latency_milliseconds" in metrics_output
    assert "sadie_collector_memory_usage_bytes" in metrics_output
    assert "sadie_collector_cpu_usage_percent" in metrics_output
    assert "binance_collector" in metrics_output
    assert "kraken_collector" in metrics_output


@pytest.mark.asyncio
async def test_dashboard_integration(metrics_manager):
    """Test l'intégration des tableaux de bord avec les métriques."""
    
    # Créer un gestionnaire de tableaux de bord
    dashboard_manager = DashboardManager()
    
    # Créer un tableau de bord
    dashboard = dashboard_manager.create_dashboard(
        name="Test Dashboard",
        description="Dashboard for testing",
        collector_id="binance_collector"
    )
    
    # Ajouter des widgets
    latency_widget = Widget(
        name="Latency Chart",
        widget_type="line_chart",
        metric="latency",
        time_range=timedelta(hours=1)
    )
    
    # Ajouter le widget au tableau de bord
    dashboard_manager.add_widget(dashboard.id, latency_widget)
    
    # Récupérer les données du widget
    widget_data = dashboard_manager.get_widget_data(
        dashboard.id,
        latency_widget.id,
        metrics_manager
    )
    
    # Vérifier que les données du widget sont correctes
    assert widget_data is not None
    assert "metric" in widget_data
    assert widget_data["metric"] == "latency"
    assert "data" in widget_data
    assert len(widget_data["data"]) > 0


@pytest.mark.asyncio
async def test_end_to_end_monitoring_flow(metrics_manager, alert_manager, notification_manager, prometheus_exporter):
    """Test du flux complet de monitoring de bout en bout."""
    
    # 1. Configurer l'intégration entre les composants
    alert_manager.notification_manager = notification_manager
    
    # 2. Créer un collecteur simulé avec des performances qui se dégradent
    for i in range(5):
        timestamp = datetime.now() - timedelta(minutes=5-i)
        
        # Les métriques se dégradent progressivement
        degrading_metrics = CollectorMetric(
            collector_id="binance_collector",
            timestamp=timestamp,
            latency=100 + (i * 20),  # Augmente jusqu'à dépasser le seuil
            memory_usage=250 + (i * 15),
            cpu_usage=10 + (i * 5),
            requests_per_minute=100 - i
        )
        
        # 3. Ajouter les métriques au gestionnaire
        metrics_manager.add_metric(degrading_metrics)
        
        # 4. Mettre à jour l'exportateur Prometheus
        prometheus_exporter.update_metrics(degrading_metrics)
        
        # 5. Vérifier les alertes
        triggered_alerts = alert_manager.check_alerts(degrading_metrics)
        
        # La dernière métrique devrait déclencher l'alerte de latence (100 + 4*20 = 180 > 150)
        if i == 4:
            assert len(triggered_alerts) == 1
            assert triggered_alerts[0].name == "Test Latence Élevée"
            assert notification_manager.channels["email"].send.called
        else:
            assert len(triggered_alerts) == 0
    
    # 6. Exporter les données finales
    exporter = MetricsExporter(metrics_manager)
    json_data = exporter.export_json(
        collector_id="binance_collector",
        start_time=datetime.now() - timedelta(minutes=10),
        end_time=datetime.now()
    )
    
    # Vérifier que les données exportées contiennent toutes les métriques
    json_result = json.loads(json_data)
    assert len(json_result["metrics"]) >= 5  # Au moins nos 5 métriques ajoutées
    
    # 7. Vérifier les métriques Prometheus
    metrics_output = prometheus_exporter.get_metrics()
    assert "sadie_collector_latency_milliseconds{collector=\"binance_collector\"}" in metrics_output
    assert "180" in metrics_output  # La dernière valeur de latence 