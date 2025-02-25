"""Routes API pour les alertes de performance."""

import logging
import uuid
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel, Field

from sadie.core.monitoring.alerts import (
    global_alert_manager, 
    PerformanceAlert, 
    PerformanceThreshold,
    initialize_alert_manager
)
from sadie.core.monitoring.metrics import global_metrics_manager
from sadie.web.auth import get_current_active_user, get_admin_user, User

logger = logging.getLogger(__name__)

# Initialisation du gestionnaire d'alertes
initialize_alert_manager(global_metrics_manager)

router = APIRouter(prefix="/alerts", tags=["alerts"])

# Modèles Pydantic pour l'API
class ThresholdCreate(BaseModel):
    """Modèle pour la création d'un seuil d'alerte."""
    metric_type: str
    operator: str
    value: float
    duration: int = 60
    cooldown: int = 300
    enabled: bool = True

class AlertCreate(BaseModel):
    """Modèle pour la création d'une alerte."""
    name: str
    collector_name: Optional[str] = None
    exchange: Optional[str] = None
    symbols: List[str] = Field(default_factory=list)
    thresholds: List[ThresholdCreate] = Field(default_factory=list)
    notification_channels: List[str] = Field(default_factory=list, description="Canaux de notification (log, console, slack, email, etc.)")

class AlertResponse(BaseModel):
    """Modèle pour la réponse d'une opération sur une alerte."""
    success: bool
    alert_id: Optional[str] = None
    message: Optional[str] = None

class AlertUpdate(BaseModel):
    """Modèle pour la mise à jour d'une alerte."""
    name: Optional[str] = None
    collector_name: Optional[str] = None
    exchange: Optional[str] = None
    symbols: Optional[List[str]] = None
    thresholds: Optional[List[ThresholdCreate]] = None
    notification_channels: Optional[List[str]] = None
    enabled: Optional[bool] = None

# Routes API
@router.post("", response_model=AlertResponse)
async def create_alert(
    alert: AlertCreate,
    current_user: User = Depends(get_admin_user)
):
    """Crée une nouvelle alerte de performance."""
    if not global_alert_manager:
        raise HTTPException(status_code=503, detail="Le gestionnaire d'alertes n'est pas disponible")
    
    # Génère un ID unique
    alert_id = str(uuid.uuid4())
    
    # Convertit les seuils
    thresholds = [
        PerformanceThreshold(
            metric_type=t.metric_type,
            operator=t.operator,
            value=t.value,
            duration=t.duration,
            cooldown=t.cooldown,
            enabled=t.enabled
        )
        for t in alert.thresholds
    ]
    
    # Crée l'alerte
    perf_alert = PerformanceAlert(
        id=alert_id,
        name=alert.name,
        collector_name=alert.collector_name,
        exchange=alert.exchange,
        symbols=alert.symbols,
        thresholds=thresholds,
        notification_channels=alert.notification_channels
    )
    
    # Ajoute l'alerte
    alert_id = global_alert_manager.add_alert(perf_alert)
    
    return {
        "success": True,
        "alert_id": alert_id,
        "message": f"Alerte '{alert.name}' créée avec succès"
    }

@router.get("", response_model=Dict)
async def get_alerts(
    current_user: User = Depends(get_current_active_user)
):
    """Récupère toutes les alertes de performance."""
    if not global_alert_manager:
        raise HTTPException(status_code=503, detail="Le gestionnaire d'alertes n'est pas disponible")
    
    alerts = global_alert_manager.get_alerts()
    return {
        "success": True,
        "count": len(alerts),
        "alerts": [alert.to_dict() for alert in alerts]
    }

@router.get("/{alert_id}", response_model=Dict)
async def get_alert(
    alert_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Récupère une alerte spécifique par son ID."""
    if not global_alert_manager:
        raise HTTPException(status_code=503, detail="Le gestionnaire d'alertes n'est pas disponible")
    
    alert = global_alert_manager.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alerte {alert_id} non trouvée")
    
    return {
        "success": True,
        "alert": alert.to_dict()
    }

@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: str,
    alert_update: AlertUpdate,
    current_user: User = Depends(get_admin_user)
):
    """Met à jour une alerte existante."""
    if not global_alert_manager:
        raise HTTPException(status_code=503, detail="Le gestionnaire d'alertes n'est pas disponible")
    
    # Vérifie que l'alerte existe
    existing_alert = global_alert_manager.get_alert(alert_id)
    if not existing_alert:
        raise HTTPException(status_code=404, detail=f"Alerte {alert_id} non trouvée")
    
    # Prépare les données pour la mise à jour
    update_data = {}
    
    if alert_update.name is not None:
        update_data["name"] = alert_update.name
    
    if alert_update.collector_name is not None:
        update_data["collector_name"] = alert_update.collector_name
    
    if alert_update.exchange is not None:
        update_data["exchange"] = alert_update.exchange
    
    if alert_update.symbols is not None:
        update_data["symbols"] = alert_update.symbols
    
    if alert_update.notification_channels is not None:
        update_data["notification_channels"] = alert_update.notification_channels
    
    if alert_update.thresholds is not None:
        update_data["thresholds"] = [
            PerformanceThreshold(
                metric_type=t.metric_type,
                operator=t.operator,
                value=t.value,
                duration=t.duration,
                cooldown=t.cooldown,
                enabled=t.enabled
            )
            for t in alert_update.thresholds
        ]
    
    # Effectue la mise à jour
    success = global_alert_manager.update_alert(alert_id, update_data)
    
    return {
        "success": success,
        "alert_id": alert_id,
        "message": "Alerte mise à jour avec succès" if success else "Échec de la mise à jour de l'alerte"
    }

@router.delete("/{alert_id}", response_model=AlertResponse)
async def delete_alert(
    alert_id: str,
    current_user: User = Depends(get_admin_user)
):
    """Supprime une alerte."""
    if not global_alert_manager:
        raise HTTPException(status_code=503, detail="Le gestionnaire d'alertes n'est pas disponible")
    
    success = global_alert_manager.delete_alert(alert_id)
    
    return {
        "success": success,
        "alert_id": alert_id,
        "message": "Alerte supprimée avec succès" if success else "Échec de la suppression de l'alerte"
    }

@router.get("/history", response_model=Dict)
async def get_alert_history(
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
):
    """Récupère l'historique des alertes déclenchées."""
    if not global_alert_manager:
        raise HTTPException(status_code=503, detail="Le gestionnaire d'alertes n'est pas disponible")
    
    history = global_alert_manager.get_alert_history(limit=limit)
    
    return {
        "success": True,
        "count": len(history),
        "history": history
    }

# Fonction pour démarrer le gestionnaire d'alertes au démarrage de l'application
async def startup_alert_manager():
    """Démarre le gestionnaire d'alertes au démarrage de l'application."""
    from sadie.core.monitoring.alerts import start_alert_manager
    await start_alert_manager()
    logger.info("Gestionnaire d'alertes démarré")

# Fonction pour arrêter le gestionnaire d'alertes à l'arrêt de l'application
async def shutdown_alert_manager():
    """Arrête le gestionnaire d'alertes à l'arrêt de l'application."""
    from sadie.core.monitoring.alerts import stop_alert_manager
    await stop_alert_manager()
    logger.info("Gestionnaire d'alertes arrêté") 