"""Module pour l'exportation des métriques au format Prometheus."""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from prometheus_client import start_http_server, Gauge, Counter, Info

from sadie.core.monitoring.metrics import global_metrics_manager, PerformanceMetric

logger = logging.getLogger(__name__)

# Métriques Prometheus
COLLECTOR_THROUGHPUT = Gauge(
    'sadie_collector_throughput',
    'Débit du collecteur en messages par seconde',
    ['collector_name', 'exchange', 'symbol']
)

COLLECTOR_LATENCY = Gauge(
    'sadie_collector_latency',
    'Latence du collecteur en millisecondes',
    ['collector_name', 'exchange', 'symbol']
)

COLLECTOR_ERROR_RATE = Gauge(
    'sadie_collector_error_rate',
    'Taux d\'erreurs du collecteur en pourcentage',
    ['collector_name', 'exchange', 'symbol']
)

COLLECTOR_HEALTH = Gauge(
    'sadie_collector_health',
    'Santé du collecteur (1: sain, 0: défaillant)',
    ['collector_name', 'exchange', 'symbol']
)

COLLECTOR_TOTAL_MESSAGES = Counter(
    'sadie_collector_total_messages',
    'Nombre total de messages traités par le collecteur',
    ['collector_name', 'exchange', 'symbol']
)

COLLECTOR_TOTAL_ERRORS = Counter(
    'sadie_collector_total_errors',
    'Nombre total d\'erreurs rencontrées par le collecteur',
    ['collector_name', 'exchange', 'symbol']
)

COLLECTOR_INFO = Info(
    'sadie_collector',
    'Informations sur le collecteur',
    ['collector_name', 'exchange']
)

class PrometheusExporter:
    """Classe pour exporter les métriques au format Prometheus."""
    
    def __init__(self, port: int = 9090, refresh_interval: int = 15):
        """
        Initialise l'exportateur Prometheus.
        
        Args:
            port: Port sur lequel exposer les métriques Prometheus
            refresh_interval: Intervalle de rafraîchissement des métriques en secondes
        """
        self.port = port
        self.refresh_interval = refresh_interval
        self.running = False
        self.thread = None
        self._collector_info_exported = set()
    
    def start(self):
        """Démarre l'exportateur Prometheus."""
        if self.running:
            return
        
        logger.info(f"Démarrage de l'exportateur Prometheus sur le port {self.port}")
        try:
            start_http_server(self.port)
            self.running = True
            self.thread = threading.Thread(target=self._refresh_metrics_loop, daemon=True)
            self.thread.start()
            logger.info("Exportateur Prometheus démarré avec succès")
        except Exception as e:
            logger.error(f"Erreur lors du démarrage de l'exportateur Prometheus: {e}")
    
    def stop(self):
        """Arrête l'exportateur Prometheus."""
        if not self.running:
            return
        
        logger.info("Arrêt de l'exportateur Prometheus")
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)
        logger.info("Exportateur Prometheus arrêté")
    
    def _refresh_metrics_loop(self):
        """Boucle de rafraîchissement des métriques."""
        while self.running:
            try:
                self._refresh_metrics()
            except Exception as e:
                logger.error(f"Erreur lors du rafraîchissement des métriques Prometheus: {e}")
            
            # Attente avant le prochain rafraîchissement
            time.sleep(self.refresh_interval)
    
    async def _refresh_metrics(self):
        """Rafraîchit les métriques Prometheus avec les données les plus récentes."""
        # Récupération des métriques des dernières 5 minutes
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=5)
        
        metrics = await global_metrics_manager.get_metrics(
            start_time=start_time,
            end_time=end_time
        )
        
        # Mise à jour des métriques Prometheus
        self._update_prometheus_metrics(metrics)
    
    def _update_prometheus_metrics(self, metrics: List[PerformanceMetric]):
        """Met à jour les métriques Prometheus avec les données les plus récentes."""
        collector_totals = {}
        
        # Traitement des métriques
        for metric in metrics:
            collector_name = metric.name
            exchange = metric.exchange
            
            # Export des informations du collecteur (une seule fois par collecteur/exchange)
            collector_key = f"{collector_name}_{exchange}"
            if collector_key not in self._collector_info_exported:
                COLLECTOR_INFO.labels(
                    collector_name=collector_name,
                    exchange=exchange
                ).info({
                    'collector_name': collector_name,
                    'exchange': exchange,
                    'symbols': ','.join(metric.symbols) if metric.symbols else '',
                    'first_seen': metric.timestamp.isoformat()
                })
                self._collector_info_exported.add(collector_key)
            
            # Agrégation pour les compteurs totaux
            for symbol in (metric.symbols or [""]):
                key = (collector_name, exchange, symbol or "all")
                if key not in collector_totals:
                    collector_totals[key] = {"messages": 0, "errors": 0}
                
                # Mise à jour des métriques selon leur type
                if metric.metric_type == "throughput":
                    COLLECTOR_THROUGHPUT.labels(
                        collector_name=collector_name,
                        exchange=exchange,
                        symbol=symbol or "all"
                    ).set(metric.value)
                    
                    # Estimation du nombre de messages
                    collector_totals[key]["messages"] += int(metric.value)
                
                elif metric.metric_type == "latency":
                    COLLECTOR_LATENCY.labels(
                        collector_name=collector_name,
                        exchange=exchange,
                        symbol=symbol or "all"
                    ).set(metric.value)
                
                elif metric.metric_type == "error_rate":
                    COLLECTOR_ERROR_RATE.labels(
                        collector_name=collector_name,
                        exchange=exchange,
                        symbol=symbol or "all"
                    ).set(metric.value)
                    
                    # Estimation du nombre d'erreurs
                    if "throughput_value" in metric.metadata:
                        throughput = metric.metadata["throughput_value"]
                        errors = int(throughput * (metric.value / 100.0))
                        collector_totals[key]["errors"] += errors
                
                elif metric.metric_type == "health":
                    COLLECTOR_HEALTH.labels(
                        collector_name=collector_name,
                        exchange=exchange,
                        symbol=symbol or "all"
                    ).set(1.0 if metric.value > 0.5 else 0.0)
        
        # Mise à jour des compteurs totaux
        for (collector_name, exchange, symbol), totals in collector_totals.items():
            if totals["messages"] > 0:
                COLLECTOR_TOTAL_MESSAGES.labels(
                    collector_name=collector_name,
                    exchange=exchange,
                    symbol=symbol
                ).inc(totals["messages"])
            
            if totals["errors"] > 0:
                COLLECTOR_TOTAL_ERRORS.labels(
                    collector_name=collector_name,
                    exchange=exchange,
                    symbol=symbol
                ).inc(totals["errors"])


# Instance globale de l'exportateur Prometheus
global_prometheus_exporter = PrometheusExporter()

def start_prometheus_exporter(port: int = 9090):
    """Démarre l'exportateur Prometheus global."""
    global global_prometheus_exporter
    global_prometheus_exporter = PrometheusExporter(port=port)
    global_prometheus_exporter.start()

def stop_prometheus_exporter():
    """Arrête l'exportateur Prometheus global."""
    if global_prometheus_exporter:
        global_prometheus_exporter.stop() 