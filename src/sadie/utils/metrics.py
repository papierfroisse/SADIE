"""
Collecte et gestion des métriques.
"""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .logging import get_logger

logger = get_logger(__name__)

@dataclass
class Metric:
    """Métrique de base."""
    
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit la métrique en dictionnaire.

        Returns:
            Dictionnaire représentant la métrique
        """
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags
        }

class MetricsCollector:
    """Collecteur de métriques."""
    
    def __init__(self):
        """Initialise le collecteur de métriques."""
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.timers: Dict[str, float] = {}
    
    def record(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Enregistre une métrique.

        Args:
            name: Nom de la métrique
            value: Valeur de la métrique
            tags: Tags associés à la métrique
        """
        metric = Metric(name=name, value=value, tags=tags or {})
        self.metrics[name].append(metric)
        logger.debug(f"Métrique enregistrée: {metric.to_dict()}")
    
    def start_timer(self, name: str) -> None:
        """
        Démarre un timer.

        Args:
            name: Nom du timer
        """
        self.timers[name] = time.time()
        logger.debug(f"Timer démarré: {name}")
    
    def stop_timer(self, name: str, tags: Optional[Dict[str, str]] = None) -> float:
        """
        Arrête un timer et enregistre la durée.

        Args:
            name: Nom du timer
            tags: Tags associés à la métrique

        Returns:
            Durée en secondes
        """
        if name not in self.timers:
            logger.warning(f"Timer non trouvé: {name}")
            return 0.0
        
        duration = time.time() - self.timers.pop(name)
        self.record(f"{name}_duration", duration, tags)
        logger.debug(f"Timer arrêté: {name} ({duration:.2f}s)")
        
        return duration
    
    def get_metrics(
        self,
        name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[Metric]:
        """
        Récupère les métriques.

        Args:
            name: Nom des métriques à récupérer
            start_time: Début de la période
            end_time: Fin de la période
            tags: Tags à filtrer

        Returns:
            Liste des métriques
        """
        metrics = []
        
        for metric_name, metric_list in self.metrics.items():
            if name and metric_name != name:
                continue
            
            for metric in metric_list:
                if start_time and metric.timestamp < start_time:
                    continue
                if end_time and metric.timestamp > end_time:
                    continue
                
                if tags:
                    match = True
                    for key, value in tags.items():
                        if key not in metric.tags or metric.tags[key] != value:
                            match = False
                            break
                    if not match:
                        continue
                
                metrics.append(metric)
        
        return metrics
    
    def clear(self) -> None:
        """Efface toutes les métriques."""
        self.metrics.clear()
        self.timers.clear()
        logger.debug("Métriques effacées")

# Instance globale du collecteur de métriques
metrics = MetricsCollector() 