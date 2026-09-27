"""Module pour la gestion des alertes basées sur les métriques de performance."""

import asyncio
import logging
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field, asdict

from sadie.core.monitoring.metrics import CollectorMetricsManager, CollectorMetric

logger = logging.getLogger(__name__)

@dataclass
class PerformanceThreshold:
    """Définition d'un seuil d'alerte pour les métriques de performance."""
    
    metric_type: str  # Type de métrique (throughput, latency, error_rate, health)
    operator: str  # Opérateur (>, <, >=, <=, ==, !=)
    value: float  # Valeur seuil
    duration: int = 60  # Durée en secondes pendant laquelle le seuil doit être dépassé
    cooldown: int = 300  # Période de silence après le déclenchement (en secondes)
    enabled: bool = True  # Si le seuil est activé
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le seuil en dictionnaire."""
        return asdict(self)
    
    def apply(self, metric_value: float) -> bool:
        """Applique l'opérateur pour vérifier si la valeur dépasse le seuil."""
        if self.operator == '>':
            return metric_value > self.value
        elif self.operator == '<':
            return metric_value < self.value
        elif self.operator == '>=':
            return metric_value >= self.value
        elif self.operator == '<=':
            return metric_value <= self.value
        elif self.operator == '==':
            return metric_value == self.value
        elif self.operator == '!=':
            return metric_value != self.value
        else:
            logger.warning(f"Opérateur inconnu: {self.operator}")
            return False

@dataclass
class PerformanceAlert:
    """Alerte basée sur les métriques de performance."""
    
    id: str  # Identifiant unique
    name: str  # Nom de l'alerte
    collector_name: Optional[str]  # Nom du collecteur (None = tous)
    exchange: Optional[str]  # Exchange (None = tous)
    symbols: List[str] = field(default_factory=list)  # Symboles concernés (vide = tous)
    thresholds: List[PerformanceThreshold] = field(default_factory=list)  # Seuils d'alerte
    notification_channels: List[str] = field(default_factory=list)  # Canaux de notification
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'alerte en dictionnaire."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        if self.last_triggered:
            data['last_triggered'] = self.last_triggered.isoformat()
        return data
    
    def is_applicable(self, metric: CollectorMetric) -> bool:
        """Vérifie si cette alerte s'applique à une métrique donnée."""
        # Vérifie le collecteur
        if self.collector_name and self.collector_name != metric.name:
            return False
            
        # Vérifie l'exchange
        if self.exchange and self.exchange != metric.exchange:
            return False
            
        # Vérifie les symboles
        if self.symbols and not any(s in metric.symbols for s in self.symbols):
            return False
            
        # Vérifie s'il y a un seuil pour ce type de métrique
        return any(t.metric_type == metric.metric_type and t.enabled for t in self.thresholds)
    
    def should_trigger(self, metric_value: float, metric_type: str) -> bool:
        """Vérifie si l'alerte doit être déclenchée pour une valeur de métrique."""
        # Vérifie chaque seuil applicable
        for threshold in self.thresholds:
            if threshold.metric_type == metric_type and threshold.enabled:
                if threshold.apply(metric_value):
                    # Vérifie le cooldown
                    if (self.last_triggered and 
                        (datetime.now(timezone.utc) - self.last_triggered).total_seconds() < threshold.cooldown):
                        # En période de cooldown
                        return False
                    return True
        return False
    
    def trigger(self) -> Dict[str, Any]:
        """Déclenche l'alerte et renvoie les données d'alerte."""
        self.last_triggered = datetime.now(timezone.utc)
        self.trigger_count += 1
        
        return {
            "alert_id": self.id,
            "alert_name": self.name,
            "triggered_at": self.last_triggered.isoformat(),
            "trigger_count": self.trigger_count,
            "notification_channels": self.notification_channels,
            "collector_name": self.collector_name,
            "exchange": self.exchange,
            "symbols": self.symbols
        }

class NotificationManager:
    """Gestionnaire des notifications pour les alertes."""
    
    def __init__(self):
        """Initialise le gestionnaire de notifications."""
        self.channels = {}
        self.setup_default_channels()
    
    def setup_default_channels(self):
        """Configure les canaux de notification par défaut."""
        self.register_channel("console", self._notify_console)
        self.register_channel("log", self._notify_log)
    
    def register_channel(self, channel_name: str, handler: Callable[[Dict[str, Any]], None]):
        """Enregistre un nouveau canal de notification."""
        self.channels[channel_name] = handler
        logger.info(f"Canal de notification enregistré: {channel_name}")
    
    async def send_notification(self, channel: str, alert_data: Dict[str, Any]):
        """Envoie une notification sur un canal spécifique."""
        if channel in self.channels:
            try:
                await asyncio.to_thread(self.channels[channel], alert_data)
                logger.info(f"Notification envoyée sur le canal {channel}")
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de la notification sur {channel}: {str(e)}")
        else:
            logger.warning(f"Canal de notification inconnu: {channel}")
    
    def _notify_console(self, alert_data: Dict[str, Any]):
        """Notifie via la console (pour le développement)."""
        print(f"\n🚨 ALERTE DE PERFORMANCE 🚨\n{json.dumps(alert_data, indent=2)}\n")
    
    def _notify_log(self, alert_data: Dict[str, Any]):
        """Notifie via les logs."""
        logger.warning(f"ALERTE DE PERFORMANCE: {json.dumps(alert_data)}")

class PerformanceAlertManager:
    """Gestionnaire des alertes de performance."""
    
    def __init__(self, metrics_manager: CollectorMetricsManager):
        """Initialise le gestionnaire d'alertes.
        
        Args:
            metrics_manager: Gestionnaire de métriques pour récupérer les données
        """
        self.metrics_manager = metrics_manager
        self.alerts: Dict[str, PerformanceAlert] = {}
        self.notification_manager = NotificationManager()
        self.running = False
        self._task = None
        self.check_interval = 60  # Intervalle de vérification en secondes
        
        # Historique des alertes
        self.alert_history = []  # Liste des alertes déclenchées
        self.max_history_size = 1000  # Taille maximale de l'historique
    
    async def start(self):
        """Démarre le gestionnaire d'alertes."""
        if self.running:
            return
            
        self.running = True
        self._task = asyncio.create_task(self._check_alerts_loop())
        logger.info("Gestionnaire d'alertes démarré")
    
    async def stop(self):
        """Arrête le gestionnaire d'alertes."""
        if not self.running:
            return
            
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
            
        logger.info("Gestionnaire d'alertes arrêté")
    
    def add_alert(self, alert: PerformanceAlert) -> str:
        """Ajoute une nouvelle alerte.
        
        Returns:
            L'identifiant de l'alerte
        """
        self.alerts[alert.id] = alert
        logger.info(f"Alerte ajoutée: {alert.name} (ID: {alert.id})")
        return alert.id
    
    def update_alert(self, alert_id: str, alert_data: Dict[str, Any]) -> bool:
        """Met à jour une alerte existante.
        
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        if alert_id not in self.alerts:
            logger.warning(f"Tentative de mise à jour d'une alerte inexistante: {alert_id}")
            return False
            
        current_alert = self.alerts[alert_id]
        
        # Mise à jour des champs
        for key, value in alert_data.items():
            if key == 'thresholds' and value:
                # Traitement spécial pour les seuils
                current_alert.thresholds = [
                    PerformanceThreshold(**t) if isinstance(t, dict) else t
                    for t in value
                ]
            elif key == 'notification_channels':
                current_alert.notification_channels = value
            elif key == 'collector_name':
                current_alert.collector_name = value
            elif key == 'exchange':
                current_alert.exchange = value
            elif key == 'symbols':
                current_alert.symbols = value
            elif key == 'name':
                current_alert.name = value
                
        logger.info(f"Alerte mise à jour: {current_alert.name} (ID: {alert_id})")
        return True
    
    def delete_alert(self, alert_id: str) -> bool:
        """Supprime une alerte.
        
        Returns:
            True si la suppression a réussi, False sinon
        """
        if alert_id not in self.alerts:
            logger.warning(f"Tentative de suppression d'une alerte inexistante: {alert_id}")
            return False
            
        del self.alerts[alert_id]
        logger.info(f"Alerte supprimée: {alert_id}")
        return True
    
    def get_alert(self, alert_id: str) -> Optional[PerformanceAlert]:
        """Récupère une alerte par son identifiant."""
        return self.alerts.get(alert_id)
    
    def get_alerts(self) -> List[PerformanceAlert]:
        """Récupère toutes les alertes."""
        return list(self.alerts.values())
    
    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Récupère l'historique des alertes déclenchées."""
        return self.alert_history[-limit:] if limit > 0 else self.alert_history
    
    async def _check_alerts_loop(self):
        """Boucle de vérification des alertes."""
        while self.running:
            try:
                await self._check_alerts()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur lors de la vérification des alertes: {str(e)}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_alerts(self):
        """Vérifie toutes les alertes par rapport aux métriques récentes."""
        # Récupère les métriques récentes
        start_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        metrics = await self.metrics_manager.get_metrics(start_time=start_time)
        
        if not metrics:
            return
            
        # Organise les métriques par type pour faciliter le traitement
        metrics_by_type = {}
        for metric in metrics:
            if metric.metric_type not in metrics_by_type:
                metrics_by_type[metric.metric_type] = []
            metrics_by_type[metric.metric_type].append(metric)
        
        # Vérifie chaque alerte
        for alert_id, alert in self.alerts.items():
            # Pour chaque type de métrique de l'alerte
            for threshold in alert.thresholds:
                if not threshold.enabled:
                    continue
                    
                metric_type = threshold.metric_type
                if metric_type not in metrics_by_type:
                    continue
                    
                # Vérifie chaque métrique de ce type
                for metric in metrics_by_type[metric_type]:
                    if alert.is_applicable(metric) and alert.should_trigger(metric.value, metric_type):
                        # Déclenche l'alerte
                        alert_data = alert.trigger()
                        
                        # Ajoute le contexte de la métrique
                        alert_data["metric"] = {
                            "type": metric.metric_type,
                            "value": metric.value,
                            "unit": metric.unit,
                            "timestamp": metric.timestamp.isoformat()
                        }
                        
                        # Enregistre dans l'historique
                        self.alert_history.append(alert_data)
                        if len(self.alert_history) > self.max_history_size:
                            self.alert_history = self.alert_history[-self.max_history_size:]
                        
                        # Envoie les notifications
                        for channel in alert.notification_channels:
                            await self.notification_manager.send_notification(channel, alert_data)
                            
                        # Une alerte a été déclenchée, passe à l'alerte suivante
                        break

# Gestionnaire global des alertes (sera initialisé avec le gestionnaire de métriques)
global_alert_manager = None

def initialize_alert_manager(metrics_manager: CollectorMetricsManager) -> PerformanceAlertManager:
    """Initialise le gestionnaire global des alertes."""
    global global_alert_manager
    if global_alert_manager is None:
        global_alert_manager = PerformanceAlertManager(metrics_manager)
    return global_alert_manager

async def start_alert_manager():
    """Démarre le gestionnaire global des alertes."""
    if global_alert_manager:
        await global_alert_manager.start()

async def stop_alert_manager():
    """Arrête le gestionnaire global des alertes."""
    if global_alert_manager:
        await global_alert_manager.stop() 