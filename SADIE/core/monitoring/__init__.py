"""Module de monitoring pour SADIE."""

import logging
import os
from datetime import datetime
from typing import Optional

# Configuration du logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Configuration du logger principal
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)

def get_logger(name: str) -> logging.Logger:
    """Retourne un logger configuré pour le module spécifié."""
    logger = logging.getLogger(name)
    return logger

class Metric:
    """Représente une métrique de monitoring."""
    
    def __init__(
        self,
        name: str,
        value: float,
        timestamp: Optional[datetime] = None,
        labels: Optional[dict] = None
    ):
        self.name = name
        self.value = value
        self.timestamp = timestamp or datetime.utcnow()
        self.labels = labels or {}
    
    def __repr__(self) -> str:
        return f"Metric(name='{self.name}', value={self.value}, timestamp='{self.timestamp}')"

class Monitor:
    """Gestionnaire de monitoring."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(f"monitor.{name}")
        self._metrics: dict = {}
    
    def record(
        self,
        metric_name: str,
        value: float,
        labels: Optional[dict] = None
    ) -> None:
        """Enregistre une métrique."""
        metric = Metric(
            name=metric_name,
            value=value,
            labels=labels
        )
        self._metrics[metric_name] = metric
        self.logger.debug(f"Métrique enregistrée: {metric}")
    
    def get_metric(self, metric_name: str) -> Optional[Metric]:
        """Récupère une métrique par son nom."""
        return self._metrics.get(metric_name)
    
    def get_all_metrics(self) -> dict:
        """Récupère toutes les métriques."""
        return self._metrics.copy()
    
    def clear_metrics(self) -> None:
        """Efface toutes les métriques."""
        self._metrics.clear()
        self.logger.debug("Métriques effacées") 