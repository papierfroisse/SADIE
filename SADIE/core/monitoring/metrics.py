"""Module de métriques Prometheus."""

import time
from typing import Dict, Optional

from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry, push_to_gateway

class MetricsHandler:
    """Gestionnaire de métriques Prometheus."""
    
    def __init__(
        self,
        registry: Optional[CollectorRegistry] = None,
        push_gateway: Optional[str] = None,
        job_name: str = "sadie"
    ):
        """Initialise le gestionnaire de métriques.
        
        Args:
            registry: Registry Prometheus personnalisé
            push_gateway: URL du Pushgateway Prometheus
            job_name: Nom du job pour le Pushgateway
        """
        self.registry = registry or CollectorRegistry()
        self.push_gateway = push_gateway
        self.job_name = job_name
        
        # Métriques des événements
        self.events_total = Counter(
            "sadie_events_total",
            "Nombre total d'événements traités",
            ["topic", "status"],
            registry=self.registry
        )
        
        self.event_processing_time = Histogram(
            "sadie_event_processing_seconds",
            "Temps de traitement des événements",
            ["topic"],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0),
            registry=self.registry
        )
        
        # Métriques de la base de données
        self.db_operations = Counter(
            "sadie_db_operations_total",
            "Nombre d'opérations en base de données",
            ["operation", "status"],
            registry=self.registry
        )
        
        self.db_batch_size = Histogram(
            "sadie_db_batch_size",
            "Taille des lots d'insertion",
            buckets=(10, 50, 100, 200, 500),
            registry=self.registry
        )
        
        self.db_connection_pool = Gauge(
            "sadie_db_connections",
            "État du pool de connexions",
            ["state"],
            registry=self.registry
        )
        
        # Métriques du cache
        self.cache_operations = Counter(
            "sadie_cache_operations_total",
            "Nombre d'opérations de cache",
            ["operation", "status"],
            registry=self.registry
        )
        
        self.cache_hit_ratio = Gauge(
            "sadie_cache_hit_ratio",
            "Ratio de hits du cache",
            registry=self.registry
        )
        
        # Métriques système
        self.memory_usage = Gauge(
            "sadie_memory_bytes",
            "Utilisation mémoire",
            ["type"],
            registry=self.registry
        )
        
        self.storage_usage = Gauge(
            "sadie_storage_bytes",
            "Utilisation du stockage",
            ["table", "type"],
            registry=self.registry
        )
        
    def track_event(self, topic: str, duration: float, status: str = "success"):
        """Enregistre les métriques d'un événement.
        
        Args:
            topic: Topic de l'événement
            duration: Durée de traitement en secondes
            status: Statut du traitement
        """
        self.events_total.labels(topic=topic, status=status).inc()
        self.event_processing_time.labels(topic=topic).observe(duration)
        
    def track_db_operation(
        self,
        operation: str,
        status: str = "success",
        batch_size: Optional[int] = None
    ):
        """Enregistre les métriques d'une opération DB.
        
        Args:
            operation: Type d'opération
            status: Statut de l'opération
            batch_size: Taille du lot pour les insertions
        """
        self.db_operations.labels(
            operation=operation,
            status=status
        ).inc()
        
        if batch_size is not None:
            self.db_batch_size.observe(batch_size)
            
    def update_db_pool_stats(
        self,
        active: int,
        available: int,
        max_size: int
    ):
        """Met à jour les métriques du pool de connexions.
        
        Args:
            active: Connexions actives
            available: Connexions disponibles
            max_size: Taille maximale du pool
        """
        self.db_connection_pool.labels(state="active").set(active)
        self.db_connection_pool.labels(state="available").set(available)
        self.db_connection_pool.labels(state="max").set(max_size)
        
    def track_cache_operation(
        self,
        operation: str,
        status: str = "success",
        is_hit: Optional[bool] = None
    ):
        """Enregistre les métriques d'une opération cache.
        
        Args:
            operation: Type d'opération
            status: Statut de l'opération
            is_hit: Si l'opération est un hit (pour les gets)
        """
        self.cache_operations.labels(
            operation=operation,
            status=status
        ).inc()
        
        if is_hit is not None:
            current_ratio = float(self.cache_hit_ratio._value.get())
            total_gets = float(
                self.cache_operations.labels(
                    operation="get",
                    status="success"
                )._value.get()
            )
            new_ratio = (current_ratio * (total_gets - 1) + int(is_hit)) / total_gets
            self.cache_hit_ratio.set(new_ratio)
            
    def update_storage_metrics(self, metrics: Dict):
        """Met à jour les métriques de stockage.
        
        Args:
            metrics: Métriques de stockage TimescaleDB
        """
        for table_metrics in metrics:
            table = table_metrics["hypertable_name"]
            self.storage_usage.labels(
                table=table,
                type="total"
            ).set(table_metrics["total_bytes"])
            self.storage_usage.labels(
                table=table,
                type="compressed"
            ).set(table_metrics["compressed_total_bytes"])
            self.storage_usage.labels(
                table=table,
                type="uncompressed"
            ).set(table_metrics["uncompressed_bytes"])
            
    def push_metrics(self):
        """Pousse les métriques vers le Pushgateway."""
        if self.push_gateway:
            try:
                push_to_gateway(
                    self.push_gateway,
                    job=self.job_name,
                    registry=self.registry
                )
            except Exception as e:
                print(f"Erreur lors du push des métriques: {e}")
                
    def __enter__(self):
        """Support du context manager."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Pousse les métriques à la sortie du context."""
        self.push_metrics() 