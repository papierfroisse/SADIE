#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Exemple d'utilisation des fonctionnalités avancées de métriques dans SADIE.
Cet exemple montre comment:
1. Configurer et utiliser les alertes de performance
2. Créer des tableaux de bord personnalisés
3. Exporter des données de métriques
4. Configurer l'intégration avec Prometheus/Grafana
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta

# Assurez-vous que le package sadie est dans le chemin Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sadie.core.monitoring.alerts import PerformanceThreshold, PerformanceAlert, AlertManager
from sadie.core.monitoring.metrics import CollectorMetricsManager, CollectorMetric
from sadie.core.monitoring.dashboards import DashboardManager, Widget
from sadie.core.monitoring.export import MetricsExporter
from sadie.core.monitoring.prometheus_exporter import PrometheusExporter
from sadie.core.collectors.binance_collector import BinanceCollector
from sadie.core.collectors.kraken_collector import KrakenCollector


async def example_alerts():
    """Exemple de configuration et utilisation des alertes de performance."""
    print("\n=== EXEMPLE: ALERTES DE PERFORMANCE ===\n")
    
    # Initialisation du gestionnaire d'alertes
    alert_manager = AlertManager()
    
    # Création d'une alerte pour surveiller la latence du collecteur Binance
    latency_threshold = PerformanceThreshold('latency', '>', 200)  # Latence > 200ms
    binance_latency_alert = PerformanceAlert(
        name="Binance Latence Élevée",
        description="Alerte déclenchée lorsque la latence du collecteur Binance dépasse 200ms",
        collector_id="binance_collector",
        threshold=latency_threshold,
        severity="warning"
    )
    
    # Ajout de l'alerte au gestionnaire
    alert_manager.add_alert(binance_latency_alert)
    print(f"Alerte créée: {binance_latency_alert.name}")
    
    # Création d'une alerte pour surveiller la mémoire utilisée
    memory_threshold = PerformanceThreshold('memory_usage', '>', 500)  # > 500MB
    memory_alert = PerformanceAlert(
        name="Utilisation Mémoire Élevée",
        description="Alerte déclenchée lorsque l'utilisation de la mémoire dépasse 500MB",
        collector_id="*",  # Tous les collecteurs
        threshold=memory_threshold,
        severity="critical"
    )
    
    # Ajout de l'alerte au gestionnaire
    alert_manager.add_alert(memory_alert)
    print(f"Alerte créée: {memory_alert.name}")
    
    # Simuler des métriques pour tester les alertes
    simulated_metrics = CollectorMetric(
        collector_id="binance_collector",
        timestamp=datetime.now(),
        latency=250,  # Cette valeur déclenchera l'alerte de latence
        memory_usage=300,  # Cette valeur ne déclenchera pas l'alerte de mémoire
        cpu_usage=15,
        requests_per_minute=120
    )
    
    # Vérifier si des alertes sont déclenchées
    triggered_alerts = alert_manager.check_alerts(simulated_metrics)
    
    if triggered_alerts:
        print("\nAlertes déclenchées:")
        for alert in triggered_alerts:
            print(f"  - {alert.name}: {alert.description}")
            # Dans une application réelle, vous enverriez des notifications ici
    else:
        print("\nAucune alerte déclenchée")
    
    # Mise à jour d'une alerte existante
    updated_latency_alert = PerformanceAlert(
        id=binance_latency_alert.id,
        name="Binance Latence Critique",
        description="Alerte déclenchée lorsque la latence du collecteur Binance dépasse 300ms",
        collector_id="binance_collector",
        threshold=PerformanceThreshold('latency', '>', 300),
        severity="critical"
    )
    
    alert_manager.update_alert(updated_latency_alert)
    print(f"\nAlerte mise à jour: {updated_latency_alert.name}")
    
    # Suppression d'une alerte
    alert_manager.delete_alert(memory_alert.id)
    print(f"Alerte supprimée: {memory_alert.name}")
    
    return alert_manager


async def example_dashboards():
    """Exemple de création de tableaux de bord personnalisés."""
    print("\n=== EXEMPLE: TABLEAUX DE BORD PERSONNALISÉS ===\n")
    
    # Initialisation du gestionnaire de tableaux de bord
    dashboard_manager = DashboardManager()
    
    # Création d'un tableau de bord pour les métriques Binance
    binance_dashboard = dashboard_manager.create_dashboard(
        name="Tableau de Bord Binance",
        description="Surveillance des performances du collecteur Binance",
        collector_id="binance_collector"
    )
    print(f"Tableau de bord créé: {binance_dashboard.name}")
    
    # Ajout de widgets au tableau de bord
    latency_widget = Widget(
        name="Latence",
        widget_type="line_chart",
        metric="latency",
        time_range=timedelta(hours=24),
        refresh_interval=60  # Rafraîchir toutes les 60 secondes
    )
    
    cpu_widget = Widget(
        name="Utilisation CPU",
        widget_type="gauge",
        metric="cpu_usage",
        min_value=0,
        max_value=100,
        thresholds=[
            {"value": 70, "color": "yellow"},
            {"value": 90, "color": "red"}
        ]
    )
    
    requests_widget = Widget(
        name="Requêtes par minute",
        widget_type="counter",
        metric="requests_per_minute",
        time_range=timedelta(minutes=5)
    )
    
    # Ajout des widgets au tableau de bord
    dashboard_manager.add_widget(binance_dashboard.id, latency_widget)
    dashboard_manager.add_widget(binance_dashboard.id, cpu_widget)
    dashboard_manager.add_widget(binance_dashboard.id, requests_widget)
    
    print(f"Widgets ajoutés au tableau de bord {binance_dashboard.name}:")
    print(f"  - {latency_widget.name} ({latency_widget.widget_type})")
    print(f"  - {cpu_widget.name} ({cpu_widget.widget_type})")
    print(f"  - {requests_widget.name} ({requests_widget.widget_type})")
    
    # Création d'un tableau de bord multi-collecteurs
    overview_dashboard = dashboard_manager.create_dashboard(
        name="Vue d'ensemble des collecteurs",
        description="Vue d'ensemble des performances de tous les collecteurs",
        collector_id="*"  # Tous les collecteurs
    )
    
    memory_widget = Widget(
        name="Utilisation mémoire par collecteur",
        widget_type="bar_chart",
        metric="memory_usage",
        group_by="collector_id"
    )
    
    dashboard_manager.add_widget(overview_dashboard.id, memory_widget)
    print(f"\nTableau de bord créé: {overview_dashboard.name}")
    print(f"Widget ajouté: {memory_widget.name} ({memory_widget.widget_type})")
    
    return dashboard_manager


async def example_export():
    """Exemple d'exportation des données de métriques."""
    print("\n=== EXEMPLE: EXPORTATION DES DONNÉES ===\n")
    
    # Initialisation du gestionnaire de métriques
    metrics_manager = CollectorMetricsManager()
    
    # Simulation de collecte de métriques pour deux collecteurs
    start_time = datetime.now() - timedelta(hours=1)
    
    # Générer des métriques simulées pour les dernières heures
    for i in range(60):  # Une métrique par minute
        timestamp = start_time + timedelta(minutes=i)
        
        # Métriques pour Binance
        binance_metric = CollectorMetric(
            collector_id="binance_collector",
            timestamp=timestamp,
            latency=100 + (i % 20),  # Variation de la latence
            memory_usage=250 + i,
            cpu_usage=10 + (i % 15),
            requests_per_minute=100 + (i % 50)
        )
        metrics_manager.add_metric(binance_metric)
        
        # Métriques pour Kraken
        kraken_metric = CollectorMetric(
            collector_id="kraken_collector",
            timestamp=timestamp,
            latency=120 + (i % 30),
            memory_usage=200 + (i % 100),
            cpu_usage=15 + (i % 10),
            requests_per_minute=80 + (i % 40)
        )
        metrics_manager.add_metric(kraken_metric)
    
    print(f"Métriques simulées générées: {len(metrics_manager.get_metrics())} entrées")
    
    # Exportation au format JSON
    exporter = MetricsExporter(metrics_manager)
    json_data = exporter.export_json(
        collector_id="binance_collector",
        start_time=start_time,
        end_time=datetime.now()
    )
    
    # Ecriture du JSON dans un fichier
    with open("binance_metrics_export.json", "w") as f:
        f.write(json_data)
    
    print(f"Données exportées en JSON: binance_metrics_export.json")
    
    # Exportation au format CSV
    csv_data = exporter.export_csv(
        collector_id="kraken_collector",
        metrics=["latency", "cpu_usage"],
        start_time=start_time,
        end_time=datetime.now()
    )
    
    # Ecriture du CSV dans un fichier
    with open("kraken_metrics_export.csv", "w") as f:
        f.write(csv_data)
    
    print(f"Données exportées en CSV: kraken_metrics_export.csv")
    
    return metrics_manager


async def example_prometheus():
    """Exemple d'intégration avec Prometheus."""
    print("\n=== EXEMPLE: INTÉGRATION PROMETHEUS ===\n")
    
    # Initialisation de l'exportateur Prometheus
    prometheus_exporter = PrometheusExporter()
    
    # Simulation de collecteurs
    binance_collector = BinanceCollector(api_key="dummy", api_secret="dummy")
    kraken_collector = KrakenCollector(api_key="dummy", api_secret="dummy")
    
    # Enregistrement des collecteurs auprès de l'exportateur Prometheus
    prometheus_exporter.register_collector(binance_collector)
    prometheus_exporter.register_collector(kraken_collector)
    
    print("Collecteurs enregistrés pour l'exposition Prometheus:")
    print(f"  - {binance_collector.__class__.__name__}")
    print(f"  - {kraken_collector.__class__.__name__}")
    
    # Simuler des métriques pour les collecteurs
    binance_metrics = CollectorMetric(
        collector_id="binance_collector",
        timestamp=datetime.now(),
        latency=120,
        memory_usage=320,
        cpu_usage=12,
        requests_per_minute=150
    )
    
    kraken_metrics = CollectorMetric(
        collector_id="kraken_collector",
        timestamp=datetime.now(),
        latency=140,
        memory_usage=280,
        cpu_usage=18,
        requests_per_minute=90
    )
    
    # Mise à jour des métriques Prometheus
    prometheus_exporter.update_metrics(binance_metrics)
    prometheus_exporter.update_metrics(kraken_metrics)
    
    # Récupération des métriques au format Prometheus
    metrics_output = prometheus_exporter.get_metrics()
    
    print("\nExemple de sortie Prometheus:")
    print(metrics_output[:500] + "...\n")  # Affiche les 500 premiers caractères
    
    print("Configuration de Prometheus dans prometheus.yml:")
    print("""
    scrape_configs:
      - job_name: 'sadie'
        scrape_interval: 15s
        static_configs:
          - targets: ['localhost:8000']
        metrics_path: '/metrics'
    """)
    
    print("\nConfiguration Grafana:")
    print("1. Ajouter Prometheus comme source de données")
    print("2. Créer un nouveau tableau de bord")
    print("3. Ajouter des panneaux avec les requêtes:")
    print("   - rate(sadie_collector_requests_total{collector=\"binance_collector\"}[5m])")
    print("   - sadie_collector_latency_milliseconds{collector=\"kraken_collector\"}")
    
    return prometheus_exporter


async def run_all_examples():
    """Exécute tous les exemples."""
    try:
        await example_alerts()
        await example_dashboards()
        await example_export()
        await example_prometheus()
        
        print("\n=== TOUS LES EXEMPLES ONT ÉTÉ EXÉCUTÉS AVEC SUCCÈS ===\n")
        
    except Exception as e:
        print(f"Erreur lors de l'exécution des exemples: {e}")


if __name__ == "__main__":
    asyncio.run(run_all_examples()) 