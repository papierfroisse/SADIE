"""Routes API pour les métriques de performance des collecteurs."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ..auth import get_read_data_user, get_admin_user, User
from ...core.monitoring.metrics import CollectorMetricsManager, CollectorMetric

logger = logging.getLogger(__name__)

# Gestionnaire global des métriques
metrics_manager = CollectorMetricsManager()

# Création du router FastAPI
router = APIRouter(prefix="/api/metrics", tags=["metrics"])

@router.get("/collectors", response_model=Dict[str, Dict])
async def get_collectors_metrics(
    collector_name: Optional[str] = Query(None, description="Nom du collecteur"),
    exchange: Optional[str] = Query(None, description="Exchange (binance, kraken, etc.)"),
    metric_type: Optional[str] = Query(None, description="Type de métrique (throughput, latency, health, error_rate)"),
    symbol: Optional[str] = Query(None, description="Symbole spécifique"),
    timeframe: Optional[str] = Query("1h", description="Fenêtre temporelle (5m, 15m, 1h, 6h, 24h, 7d)"),
    aggregation: Optional[str] = Query("avg", description="Type d'agrégation (avg, min, max, sum, count)"),
    current_user: User = Depends(get_read_data_user)
):
    """Récupère les métriques agrégées des collecteurs selon les critères spécifiés."""
    # Conversion du timeframe en datetime
    now = datetime.utcnow()
    start_time = None
    
    if timeframe == "5m":
        start_time = now - timedelta(minutes=5)
    elif timeframe == "15m":
        start_time = now - timedelta(minutes=15)
    elif timeframe == "1h":
        start_time = now - timedelta(hours=1)
    elif timeframe == "6h":
        start_time = now - timedelta(hours=6)
    elif timeframe == "24h":
        start_time = now - timedelta(hours=24)
    elif timeframe == "7d":
        start_time = now - timedelta(days=7)
    else:
        raise HTTPException(status_code=400, detail=f"Timeframe invalide: {timeframe}")
    
    # Récupération des métriques agrégées
    metrics = await metrics_manager.get_aggregated_metrics(
        collector_name=collector_name,
        exchange=exchange,
        metric_type=metric_type,
        symbol=symbol,
        start_time=start_time,
        end_time=now,
        aggregation=aggregation
    )
    
    # Format de la réponse
    response = {
        "metrics": metrics,
        "metadata": {
            "timeframe": timeframe,
            "start_time": start_time.isoformat() if start_time else None,
            "end_time": now.isoformat(),
            "aggregation": aggregation,
            "filters": {
                "collector_name": collector_name,
                "exchange": exchange,
                "metric_type": metric_type,
                "symbol": symbol
            }
        }
    }
    
    return response

@router.get("/collectors/raw", response_model=Dict)
async def get_raw_metrics(
    collector_name: Optional[str] = Query(None, description="Nom du collecteur"),
    exchange: Optional[str] = Query(None, description="Exchange (binance, kraken, etc.)"),
    metric_type: Optional[str] = Query(None, description="Type de métrique (throughput, latency, health, error_rate)"),
    symbol: Optional[str] = Query(None, description="Symbole spécifique"),
    timeframe: Optional[str] = Query("1h", description="Fenêtre temporelle (5m, 15m, 1h, 6h, 24h, 7d)"),
    limit: Optional[int] = Query(100, description="Nombre maximum de métriques à retourner"),
    current_user: User = Depends(get_admin_user)  # Accès admin uniquement
):
    """Récupère les métriques brutes des collecteurs selon les critères spécifiés."""
    # Conversion du timeframe en datetime
    now = datetime.utcnow()
    start_time = None
    
    if timeframe == "5m":
        start_time = now - timedelta(minutes=5)
    elif timeframe == "15m":
        start_time = now - timedelta(minutes=15)
    elif timeframe == "1h":
        start_time = now - timedelta(hours=1)
    elif timeframe == "6h":
        start_time = now - timedelta(hours=6)
    elif timeframe == "24h":
        start_time = now - timedelta(hours=24)
    elif timeframe == "7d":
        start_time = now - timedelta(days=7)
    else:
        raise HTTPException(status_code=400, detail=f"Timeframe invalide: {timeframe}")
    
    # Récupération des métriques brutes
    metrics = await metrics_manager.get_metrics(
        collector_name=collector_name,
        exchange=exchange,
        metric_type=metric_type,
        symbol=symbol,
        start_time=start_time,
        end_time=now
    )
    
    # Limitation du nombre de métriques
    metrics = metrics[:limit]
    
    # Conversion en dictionnaires
    metrics_dicts = [metric.to_dict() for metric in metrics]
    
    # Format de la réponse
    response = {
        "metrics": metrics_dicts,
        "metadata": {
            "count": len(metrics_dicts),
            "timeframe": timeframe,
            "start_time": start_time.isoformat() if start_time else None,
            "end_time": now.isoformat(),
            "limit": limit,
            "filters": {
                "collector_name": collector_name,
                "exchange": exchange,
                "metric_type": metric_type,
                "symbol": symbol
            }
        }
    }
    
    return response

@router.get("/collectors/health", response_model=Dict)
async def get_collectors_health(
    collector_name: Optional[str] = Query(None, description="Nom du collecteur"),
    exchange: Optional[str] = Query(None, description="Exchange (binance, kraken, etc.)"),
    current_user: User = Depends(get_read_data_user)
):
    """Récupère l'état de santé des collecteurs."""
    # Récupération des métriques de santé
    health_metrics = await metrics_manager.get_metrics(
        collector_name=collector_name,
        exchange=exchange,
        metric_type="health",
        start_time=datetime.utcnow() - timedelta(minutes=10)  # 10 dernières minutes
    )
    
    # Organisation par collecteur
    collectors_health = {}
    for metric in health_metrics:
        if metric.name not in collectors_health or \
           metric.timestamp > collectors_health[metric.name]["timestamp"]:
            collectors_health[metric.name] = {
                "name": metric.name,
                "exchange": metric.exchange,
                "symbols": metric.symbols,
                "health": metric.value,
                "timestamp": metric.timestamp,
                "status": "healthy" if metric.value > 80 else ("degraded" if metric.value > 30 else "unhealthy")
            }
    
    # Format de la réponse
    response = {
        "collectors": list(collectors_health.values()),
        "metadata": {
            "count": len(collectors_health),
            "timestamp": datetime.utcnow().isoformat(),
            "filters": {
                "collector_name": collector_name,
                "exchange": exchange
            }
        }
    }
    
    return response

@router.get("/collectors/summary", response_model=Dict)
async def get_collectors_summary(
    current_user: User = Depends(get_read_data_user)
):
    """Récupère un résumé global des métriques des collecteurs."""
    # Récupération des métriques des dernières 24 heures
    start_time = datetime.utcnow() - timedelta(hours=24)
    
    # Métriques par type
    throughput_metrics = await metrics_manager.get_metrics(
        metric_type="throughput",
        start_time=start_time
    )
    
    latency_metrics = await metrics_manager.get_metrics(
        metric_type="latency",
        start_time=start_time
    )
    
    error_rate_metrics = await metrics_manager.get_metrics(
        metric_type="error_rate",
        start_time=start_time
    )
    
    health_metrics = await metrics_manager.get_metrics(
        metric_type="health",
        start_time=start_time
    )
    
    # Calcul des moyennes
    avg_throughput = sum(m.value for m in throughput_metrics) / len(throughput_metrics) if throughput_metrics else 0
    avg_latency = sum(m.value for m in latency_metrics) / len(latency_metrics) if latency_metrics else 0
    avg_error_rate = sum(m.value for m in error_rate_metrics) / len(error_rate_metrics) if error_rate_metrics else 0
    avg_health = sum(m.value for m in health_metrics) / len(health_metrics) if health_metrics else 0
    
    # Liste des collecteurs uniques
    unique_collectors = set((m.name, m.exchange) for m in throughput_metrics + latency_metrics + health_metrics)
    collector_count = len(unique_collectors)
    
    # Format de la réponse
    response = {
        "summary": {
            "collector_count": collector_count,
            "avg_throughput": avg_throughput,
            "avg_throughput_unit": "tps",
            "avg_latency": avg_latency,
            "avg_latency_unit": "ms",
            "avg_error_rate": avg_error_rate,
            "avg_error_rate_unit": "%",
            "avg_health": avg_health,
            "avg_health_unit": "%",
            "overall_status": "healthy" if avg_health > 80 else ("degraded" if avg_health > 30 else "unhealthy")
        },
        "metadata": {
            "timeframe": "24h",
            "start_time": start_time.isoformat(),
            "end_time": datetime.utcnow().isoformat(),
            "metrics_count": {
                "throughput": len(throughput_metrics),
                "latency": len(latency_metrics),
                "error_rate": len(error_rate_metrics),
                "health": len(health_metrics)
            }
        }
    }
    
    return response

# Fonction pour initialiser le gestionnaire de métriques
async def startup_metrics_manager():
    """Démarre le gestionnaire de métriques au démarrage de l'application."""
    await metrics_manager.start()
    logger.info("Gestionnaire de métriques démarré")

# Fonction pour arrêter le gestionnaire de métriques
async def shutdown_metrics_manager():
    """Arrête le gestionnaire de métriques à l'arrêt de l'application."""
    await metrics_manager.stop()
    logger.info("Gestionnaire de métriques arrêté") 