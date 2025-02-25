"""Routes pour la gestion de l'exportation Prometheus."""

import logging
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, Field

from sadie.web.auth import get_current_active_user, User
from sadie.core.monitoring.prometheus_exporter import (
    start_prometheus_exporter,
    stop_prometheus_exporter,
    global_prometheus_exporter
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prometheus", tags=["prometheus"])


class PrometheusConfig(BaseModel):
    """Configuration pour l'exportateur Prometheus."""
    
    enabled: bool = Field(True, description="Activer ou désactiver l'exportation Prometheus")
    port: int = Field(9090, description="Port sur lequel exposer les métriques Prometheus")


class PrometheusStatus(BaseModel):
    """Statut de l'exportateur Prometheus."""
    
    enabled: bool = Field(..., description="État de l'exportateur Prometheus")
    port: Optional[int] = Field(None, description="Port sur lequel les métriques sont exposées")


@router.post("/config", response_model=PrometheusStatus)
async def configure_prometheus(
    config: PrometheusConfig = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """Configure l'exportateur Prometheus."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Seuls les administrateurs peuvent configurer l'exportation Prometheus"
        )
    
    if config.enabled and not global_prometheus_exporter.running:
        try:
            start_prometheus_exporter(port=config.port)
            logger.info(f"Exportation Prometheus activée sur le port {config.port}")
        except Exception as e:
            logger.error(f"Erreur lors de l'activation de l'exportation Prometheus: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de l'activation de l'exportation Prometheus: {str(e)}"
            )
    elif not config.enabled and global_prometheus_exporter.running:
        try:
            stop_prometheus_exporter()
            logger.info("Exportation Prometheus désactivée")
        except Exception as e:
            logger.error(f"Erreur lors de la désactivation de l'exportation Prometheus: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de la désactivation de l'exportation Prometheus: {str(e)}"
            )
    
    return PrometheusStatus(
        enabled=global_prometheus_exporter.running,
        port=global_prometheus_exporter.port if global_prometheus_exporter.running else None
    )


@router.get("/status", response_model=PrometheusStatus)
async def get_prometheus_status(
    current_user: User = Depends(get_current_active_user)
):
    """Récupère le statut de l'exportateur Prometheus."""
    return PrometheusStatus(
        enabled=global_prometheus_exporter.running,
        port=global_prometheus_exporter.port if global_prometheus_exporter.running else None
    ) 