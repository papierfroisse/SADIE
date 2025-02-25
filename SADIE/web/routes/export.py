"""Routes pour l'exportation des données de métriques."""

import io
import csv
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse

from sadie.core.monitoring.metrics import global_metrics_manager
from sadie.web.auth import get_current_active_user, User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/export", tags=["export"])

@router.get("/metrics/json")
async def export_metrics_json(
    collector_name: Optional[str] = Query(None, description="Nom du collecteur"),
    exchange: Optional[str] = Query(None, description="Exchange (binance, kraken, etc.)"),
    metric_type: Optional[str] = Query(None, description="Type de métrique (throughput, latency, health, error_rate)"),
    symbol: Optional[str] = Query(None, description="Symbole spécifique"),
    timeframe: Optional[str] = Query("24h", description="Fenêtre temporelle (5m, 15m, 1h, 6h, 24h, 7d)"),
    current_user: User = Depends(get_current_active_user)
):
    """Exporte les métriques au format JSON."""
    # Calcul de la période
    end_time = datetime.utcnow()
    start_time = calculate_start_time(timeframe, end_time)
    
    # Récupération des métriques
    metrics = await global_metrics_manager.get_metrics(
        collector_name=collector_name,
        exchange=exchange,
        metric_type=metric_type,
        symbol=symbol,
        start_time=start_time,
        end_time=end_time
    )
    
    # Transformation des métriques en format exportable
    export_data = transform_metrics_for_export(metrics)
    
    # Génération du nom de fichier
    filename = generate_export_filename("json", collector_name, exchange, metric_type)
    
    # Préparation de la réponse
    response = Response(
        content=json.dumps(export_data, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
    
    return response

@router.get("/metrics/csv")
async def export_metrics_csv(
    collector_name: Optional[str] = Query(None, description="Nom du collecteur"),
    exchange: Optional[str] = Query(None, description="Exchange (binance, kraken, etc.)"),
    metric_type: Optional[str] = Query(None, description="Type de métrique (throughput, latency, health, error_rate)"),
    symbol: Optional[str] = Query(None, description="Symbole spécifique"),
    timeframe: Optional[str] = Query("24h", description="Fenêtre temporelle (5m, 15m, 1h, 6h, 24h, 7d)"),
    current_user: User = Depends(get_current_active_user)
):
    """Exporte les métriques au format CSV."""
    # Calcul de la période
    end_time = datetime.utcnow()
    start_time = calculate_start_time(timeframe, end_time)
    
    # Récupération des métriques
    metrics = await global_metrics_manager.get_metrics(
        collector_name=collector_name,
        exchange=exchange,
        metric_type=metric_type,
        symbol=symbol,
        start_time=start_time,
        end_time=end_time
    )
    
    # Transformation des métriques en format exportable
    export_data = transform_metrics_for_export(metrics)
    
    # Génération du nom de fichier
    filename = generate_export_filename("csv", collector_name, exchange, metric_type)
    
    # Conversion en CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # En-tête
    header = ["timestamp", "collector_name", "exchange", "metric_type", "value", "unit", "symbols"]
    writer.writerow(header)
    
    # Lignes de données
    for entry in export_data:
        symbols_str = ",".join(entry["symbols"]) if "symbols" in entry else ""
        row = [
            entry.get("timestamp", ""),
            entry.get("collector_name", ""),
            entry.get("exchange", ""),
            entry.get("metric_type", ""),
            entry.get("value", ""),
            entry.get("unit", ""),
            symbols_str
        ]
        writer.writerow(row)
    
    # Préparation de la réponse
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

def transform_metrics_for_export(metrics: List[Any]) -> List[Dict[str, Any]]:
    """Transforme les métriques en format exportable."""
    return [
        {
            "timestamp": metric.timestamp.isoformat(),
            "collector_name": metric.name,
            "exchange": metric.exchange,
            "metric_type": metric.metric_type,
            "value": metric.value,
            "unit": metric.unit,
            "symbols": metric.symbols
        }
        for metric in metrics
    ]

def calculate_start_time(timeframe: str, end_time: datetime) -> datetime:
    """Calcule la date de début en fonction de la fenêtre temporelle."""
    if timeframe == "5m":
        return end_time - timedelta(minutes=5)
    elif timeframe == "15m":
        return end_time - timedelta(minutes=15)
    elif timeframe == "1h":
        return end_time - timedelta(hours=1)
    elif timeframe == "6h":
        return end_time - timedelta(hours=6)
    elif timeframe == "24h":
        return end_time - timedelta(hours=24)
    elif timeframe == "7d":
        return end_time - timedelta(days=7)
    else:
        return end_time - timedelta(hours=24)  # Par défaut 24h

def generate_export_filename(
    extension: str,
    collector_name: Optional[str] = None,
    exchange: Optional[str] = None,
    metric_type: Optional[str] = None
) -> str:
    """Génère un nom de fichier pour l'exportation."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    parts = ["metrics"]
    
    if collector_name:
        parts.append(f"collector_{collector_name}")
    
    if exchange:
        parts.append(f"exchange_{exchange}")
    
    if metric_type:
        parts.append(f"type_{metric_type}")
    
    parts.append(timestamp)
    
    return f"{'-'.join(parts)}.{extension}" 