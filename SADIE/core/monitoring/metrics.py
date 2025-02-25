"""Module de métriques pour le monitoring des performances des collecteurs."""

import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import statistics
import asyncio
import json

logger = logging.getLogger(__name__)

@dataclass
class CollectorMetric:
    """Métrique pour un collecteur spécifique."""
    
    name: str  # Nom du collecteur
    exchange: str  # Exchange associé
    symbols: List[str]  # Symboles suivis
    metric_type: str  # Type de métrique (throughput, latency, health, etc.)
    value: float  # Valeur de la métrique
    timestamp: datetime = field(default_factory=datetime.utcnow)
    unit: str = ""  # Unité de la métrique (ms, tps, %, etc.)
    labels: Dict[str, str] = field(default_factory=dict)  # Labels additionnels
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la métrique en dictionnaire."""
        return {
            "name": self.name,
            "exchange": self.exchange,
            "symbols": self.symbols,
            "type": self.metric_type,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "unit": self.unit,
            "labels": self.labels
        }
    
    def to_json(self) -> str:
        """Convertit la métrique en JSON."""
        return json.dumps(self.to_dict())

class CollectorMetricsManager:
    """Gestionnaire des métriques de performance pour les collecteurs."""
    
    def __init__(self, retention_period: timedelta = timedelta(hours=24)):
        """Initialise le gestionnaire de métriques.
        
        Args:
            retention_period: Période de rétention des métriques
        """
        self.metrics: List[CollectorMetric] = []
        self.retention_period = retention_period
        self._lock = asyncio.Lock()
        self._cleanup_task = None
        
    async def start(self):
        """Démarre le gestionnaire et lance le nettoyage périodique."""
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
        logger.info("Gestionnaire de métriques démarré")
    
    async def stop(self):
        """Arrête le gestionnaire."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Gestionnaire de métriques arrêté")
    
    async def _periodic_cleanup(self):
        """Nettoie périodiquement les métriques trop anciennes."""
        while True:
            try:
                await asyncio.sleep(3600)  # Nettoyage toutes les heures
                await self.cleanup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur lors du nettoyage des métriques: {e}")
                await asyncio.sleep(60)  # Pause en cas d'erreur
    
    async def cleanup(self):
        """Supprime les métriques plus anciennes que la période de rétention."""
        cutoff = datetime.utcnow() - self.retention_period
        
        async with self._lock:
            original_count = len(self.metrics)
            self.metrics = [m for m in self.metrics if m.timestamp >= cutoff]
            removed = original_count - len(self.metrics)
            
        if removed > 0:
            logger.info(f"Nettoyage des métriques: {removed} métriques supprimées")
    
    async def add_metric(self, metric: CollectorMetric):
        """Ajoute une métrique à la collection."""
        async with self._lock:
            self.metrics.append(metric)
    
    async def get_metrics(
        self,
        collector_name: Optional[str] = None,
        exchange: Optional[str] = None,
        metric_type: Optional[str] = None,
        symbol: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[CollectorMetric]:
        """Récupère les métriques selon les critères spécifiés."""
        async with self._lock:
            filtered = self.metrics.copy()
        
        # Filtrage par critères
        if collector_name:
            filtered = [m for m in filtered if m.name == collector_name]
        
        if exchange:
            filtered = [m for m in filtered if m.exchange == exchange]
        
        if metric_type:
            filtered = [m for m in filtered if m.metric_type == metric_type]
        
        if symbol:
            filtered = [m for m in filtered if symbol in m.symbols]
        
        if start_time:
            filtered = [m for m in filtered if m.timestamp >= start_time]
        
        if end_time:
            filtered = [m for m in filtered if m.timestamp <= end_time]
        
        return filtered
    
    async def get_aggregated_metrics(
        self,
        collector_name: Optional[str] = None,
        exchange: Optional[str] = None,
        metric_type: Optional[str] = None,
        symbol: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        aggregation: str = "avg"  # 'avg', 'min', 'max', 'sum', 'count'
    ) -> Dict[str, Dict[str, float]]:
        """Récupère des métriques agrégées selon les critères spécifiés."""
        # Récupération des métriques brutes
        metrics = await self.get_metrics(
            collector_name, exchange, metric_type, symbol, start_time, end_time
        )
        
        if not metrics:
            return {}
        
        # Organisation par type de métrique
        metrics_by_type = {}
        for metric in metrics:
            if metric.metric_type not in metrics_by_type:
                metrics_by_type[metric.metric_type] = []
            metrics_by_type[metric.metric_type].append(metric.value)
        
        # Agrégation
        result = {}
        for m_type, values in metrics_by_type.items():
            if aggregation == "avg":
                result[m_type] = {"value": statistics.mean(values) if values else 0}
            elif aggregation == "min":
                result[m_type] = {"value": min(values) if values else 0}
            elif aggregation == "max":
                result[m_type] = {"value": max(values) if values else 0}
            elif aggregation == "sum":
                result[m_type] = {"value": sum(values)}
            elif aggregation == "count":
                result[m_type] = {"value": len(values)}
            
            # Ajout de statistiques supplémentaires
            if len(values) > 1:
                result[m_type]["count"] = len(values)
                result[m_type]["std_dev"] = statistics.stdev(values) if len(values) > 1 else 0
                result[m_type]["min"] = min(values)
                result[m_type]["max"] = max(values)
                result[m_type]["median"] = statistics.median(values)
            
        return result

class CollectorPerformanceMonitor:
    """Moniteur de performance pour un collecteur spécifique."""
    
    def __init__(
        self,
        collector_name: str,
        exchange: str,
        symbols: List[str],
        metrics_manager: CollectorMetricsManager
    ):
        """Initialise le moniteur de performance.
        
        Args:
            collector_name: Nom du collecteur
            exchange: Exchange associé
            symbols: Symboles suivis
            metrics_manager: Gestionnaire de métriques
        """
        self.collector_name = collector_name
        self.exchange = exchange
        self.symbols = symbols
        self.metrics_manager = metrics_manager
        self.start_time = datetime.utcnow()
        
        # Compteurs et statistiques
        self.trades_processed = 0
        self.trades_per_symbol = {symbol: 0 for symbol in symbols}
        self.messages_received = 0
        self.errors_count = 0
        self.connection_attempts = 0
        self.reconnections = 0
        
        # Performance
        self.processing_times = []  # Liste des temps de traitement (ms)
        self.last_trades = {}  # Dernier trade par symbole
        self.health_status = "initializing"  # 'healthy', 'degraded', 'unhealthy'
        
        # Timers pour les métriques périodiques
        self.last_metric_time = time.time()
    
    def increment_trades(self, symbol: str, count: int = 1):
        """Incrémente le compteur de trades pour un symbole."""
        self.trades_processed += count
        self.trades_per_symbol[symbol] = self.trades_per_symbol.get(symbol, 0) + count
        self.last_trades[symbol] = datetime.utcnow()
    
    def record_processing_time(self, duration_ms: float):
        """Enregistre un temps de traitement."""
        self.processing_times.append(duration_ms)
        # Limite la taille de la liste pour éviter des problèmes de mémoire
        if len(self.processing_times) > 1000:
            self.processing_times = self.processing_times[-1000:]
    
    def record_error(self, error_type: str = "general"):
        """Enregistre une erreur."""
        self.errors_count += 1
        
        # Mise à jour du statut de santé en fonction du nombre d'erreurs
        if self.errors_count > 10:
            self.health_status = "unhealthy"
        elif self.errors_count > 3:
            self.health_status = "degraded"
    
    def record_reconnection(self):
        """Enregistre une tentative de reconnexion."""
        self.connection_attempts += 1
        self.reconnections += 1
    
    async def record_metrics(self, force: bool = False):
        """Enregistre les métriques périodiques."""
        current_time = time.time()
        # Enregistrement toutes les 60 secondes ou si forcé
        if force or (current_time - self.last_metric_time >= 60):
            # Calcul des métriques
            duration = datetime.utcnow() - self.start_time
            duration_seconds = duration.total_seconds()
            
            # Throughput (trades par seconde)
            if duration_seconds > 0:
                throughput = self.trades_processed / duration_seconds
                await self.metrics_manager.add_metric(CollectorMetric(
                    name=self.collector_name,
                    exchange=self.exchange,
                    symbols=self.symbols,
                    metric_type="throughput",
                    value=throughput,
                    unit="tps"
                ))
            
            # Latence moyenne
            if self.processing_times:
                avg_latency = statistics.mean(self.processing_times)
                await self.metrics_manager.add_metric(CollectorMetric(
                    name=self.collector_name,
                    exchange=self.exchange,
                    symbols=self.symbols,
                    metric_type="latency",
                    value=avg_latency,
                    unit="ms"
                ))
            
            # Taux d'erreur
            if self.messages_received > 0:
                error_rate = (self.errors_count / self.messages_received) * 100
                await self.metrics_manager.add_metric(CollectorMetric(
                    name=self.collector_name,
                    exchange=self.exchange,
                    symbols=self.symbols,
                    metric_type="error_rate",
                    value=error_rate,
                    unit="%"
                ))
            
            # Santé du collecteur (100% = healthy, 50% = degraded, 0% = unhealthy)
            health_value = 100.0
            if self.health_status == "degraded":
                health_value = 50.0
            elif self.health_status == "unhealthy":
                health_value = 0.0
                
            await self.metrics_manager.add_metric(CollectorMetric(
                name=self.collector_name,
                exchange=self.exchange,
                symbols=self.symbols,
                metric_type="health",
                value=health_value,
                unit="%"
            ))
            
            # Réinitialisation
            self.last_metric_time = current_time
            
            # Logging
            logger.debug(
                f"Métriques enregistrées pour {self.collector_name}: "
                f"throughput={throughput:.2f}tps, "
                f"latence={avg_latency:.2f}ms, "
                f"santé={health_value:.0f}%"
            )
            
            # Réinitialisation des compteurs temporaires
            self.processing_times = []
            
    async def get_performance_report(self) -> Dict[str, Any]:
        """Génère un rapport complet des performances du collecteur."""
        now = datetime.utcnow()
        duration = now - self.start_time
        duration_seconds = duration.total_seconds()
        
        # Calcul des statistiques
        avg_latency = statistics.mean(self.processing_times) if self.processing_times else 0
        max_latency = max(self.processing_times) if self.processing_times else 0
        
        # Throughput global et par symbole
        throughput = self.trades_processed / duration_seconds if duration_seconds > 0 else 0
        symbol_throughput = {
            symbol: (count / duration_seconds if duration_seconds > 0 else 0)
            for symbol, count in self.trades_per_symbol.items()
        }
        
        # Fraîcheur des données (secondes depuis le dernier trade)
        data_freshness = {
            symbol: (now - last_time).total_seconds()
            for symbol, last_time in self.last_trades.items()
        }
        
        # Construction du rapport
        report = {
            "collector": {
                "name": self.collector_name,
                "exchange": self.exchange,
                "symbols": self.symbols,
                "uptime": str(duration),
                "uptime_seconds": duration_seconds,
                "health_status": self.health_status
            },
            "performance": {
                "throughput": throughput,
                "throughput_by_symbol": symbol_throughput,
                "avg_latency_ms": avg_latency,
                "max_latency_ms": max_latency,
                "data_freshness_seconds": data_freshness
            },
            "reliability": {
                "total_trades": self.trades_processed,
                "trades_by_symbol": self.trades_per_symbol,
                "messages_received": self.messages_received,
                "errors": self.errors_count,
                "error_rate": (self.errors_count / self.messages_received * 100) if self.messages_received > 0 else 0,
                "connection_attempts": self.connection_attempts,
                "reconnections": self.reconnections
            },
            "timestamp": now.isoformat()
        }
        
        return report

# Fonction utilitaire pour mesurer le temps d'exécution
async def measure_execution_time(func, *args, **kwargs):
    """Mesure le temps d'exécution d'une fonction asynchrone."""
    start_time = time.time()
    result = await func(*args, **kwargs)
    execution_time = (time.time() - start_time) * 1000  # ms
    return result, execution_time 