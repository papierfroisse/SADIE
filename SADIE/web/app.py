"""Module de l'application web."""

import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Optional, List, Any, Union, Literal
import os
from datetime import datetime, timedelta
import asyncio
import json
import time
import traceback
from dotenv import load_dotenv
from sadie.core.collectors.kraken_collector import KrakenTradeCollector
from sadie.core.collectors.trade_collector import BinanceTradeCollector
from pydantic import BaseModel, Field
from .stream_manager import StreamManager
from .auth import (
    authenticate_user, create_access_token, get_current_active_user,
    get_read_data_user, get_write_data_user, get_admin_user,
    Token, User, fake_users_db, ACCESS_TOKEN_EXPIRE_MINUTES
)
from sadie.data.collectors.base import start_metrics_manager, stop_metrics_manager
from .routes.metrics import router as metrics_router, startup_metrics_manager, shutdown_metrics_manager
from sadie.web.routes.alerts import router as alerts_router, startup_alert_manager, shutdown_alert_manager
from sadie.web.routes.export import router as export_router
from sadie.web.routes.prometheus import router as prometheus_router

# Chargement des variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Modèles de données
class Alert(BaseModel):
    id: Optional[str] = None
    symbol: str
    type: str
    condition: str
    value: float
    notification_type: str
    triggered: bool = False
    created_at: Optional[int] = None
    triggered_at: Optional[int] = None

class AlertResponse(BaseModel):
    success: bool
    data: Optional[Alert] = None
    error: Optional[str] = None

class AlertsResponse(BaseModel):
    success: bool
    data: Optional[List[Alert]] = None
    error: Optional[str] = None

class TradeData(BaseModel):
    symbol: str
    timestamp: int
    price: float
    quantity: float
    trade_id: str
    buyer_order_id: str = ""
    seller_order_id: str = ""
    buyer_is_maker: bool = False
    is_best_match: bool = True
    side: str = "unknown"

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    code: int
    timestamp: int = Field(default_factory=lambda: int(time.time() * 1000))

# Création de l'application FastAPI
app = FastAPI(
    title="SADIE API",
    description="API pour le Système d'Analyse et de Détection d'Indicateurs pour l'Échange",
    version="0.2.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion du router de métriques
app.include_router(metrics_router)

# Inclusion des routers
app.include_router(alerts_router, prefix="/api")
app.include_router(export_router, prefix="/api")
app.include_router(prometheus_router, prefix="/api")

# Endpoint pour l'authentification
@app.post("/api/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint pour obtenir un token JWT."""
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": user.scopes},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint public pour vérifier la santé de l'API
@app.get("/api/healthcheck")
async def healthcheck():
    """Vérifie l'état de santé de l'API."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# Endpoint protégé pour récupérer le profil utilisateur
@app.get("/api/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Récupère les informations de l'utilisateur connecté."""
    return current_user

# Configuration des collecteurs
EXCHANGE_COLLECTORS = {
    "binance": BinanceTradeCollector,
    "kraken": KrakenTradeCollector
}

# Gestionnaire de streams pour WebSocket
stream_manager = StreamManager()

@app.websocket("/ws/market")
async def websocket_endpoint(
    websocket: WebSocket,
    exchange: str = Query("binance"),
    symbols: str = Query(...),  # Symboles séparés par des virgules
):
    """Endpoint WebSocket pour les données de marché en temps réel."""
    try:
        symbols_list = symbols.split(",")
        
        # Connexion WebSocket
        await websocket.accept()
        
        # Initialisation du collecteur selon l'exchange
        if exchange.lower() == "binance":
            # Format des symboles Binance
            formatted_symbols = [s.upper().replace("/", "") for s in symbols_list]
            collector_name = f"binance_{'-'.join(formatted_symbols)}"
            collector = BinanceTradeCollector(
                name=collector_name,
                symbols=formatted_symbols,
                api_key=os.getenv("BINANCE_API_KEY"),
                api_secret=os.getenv("BINANCE_API_SECRET"),
                update_interval=1.0,
                exchange="binance",
                enable_metrics=True
            )
        elif exchange.lower() == "kraken":
            # Format des symboles Kraken
            formatted_symbols = [s.upper() for s in symbols_list]
            collector_name = f"kraken_{'-'.join(formatted_symbols)}"
            collector = KrakenTradeCollector(
                name=collector_name,
                symbols=formatted_symbols,
                api_key=os.getenv("KRAKEN_API_KEY"),
                api_secret=os.getenv("KRAKEN_API_SECRET"),
                update_interval=1.0,
                exchange="kraken",
                enable_metrics=True
            )
        else:
            await websocket.send_text(json.dumps({
                "error": f"Exchange non supporté: {exchange}"
            }))
            await websocket.close()
            return
        
        # Démarrage du collecteur
        await collector.start()
        
        # Ajout à la liste des connexions actives
        connection_id = stream_manager.add_connection(websocket)
        logger.info(f"Nouvelle connexion WebSocket établie: {connection_id}")
        
        try:
            # Boucle d'envoi des données
            while True:
                # Récupération des données du collecteur
                data = await collector.get_data()
                
                # Récupération des métriques de performance
                metrics = await collector.get_performance_metrics()
                
                # Formatage de la réponse
                response = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "exchange": exchange,
                    "symbols": formatted_symbols,
                    "data": data,
                    "metrics": {
                        "throughput": metrics.get("performance", {}).get("throughput", 0),
                        "latency": metrics.get("performance", {}).get("avg_latency_ms", 0),
                        "health": metrics.get("collector", {}).get("health_status", "unknown")
                    }
                }
                
                # Envoi des données via WebSocket
                await websocket.send_text(json.dumps(response))
                
                # Pause pour limiter le débit
                await asyncio.sleep(1)
                
        except WebSocketDisconnect:
            logger.info(f"Connexion WebSocket fermée: {connection_id}")
        finally:
            # Suppression de la connexion
            stream_manager.remove_connection(connection_id)
            
            # Arrêt du collecteur
            await collector.stop()
            
    except Exception as e:
        logger.error(f"Erreur dans le endpoint WebSocket: {e}")
        logger.debug(traceback.format_exc())
        try:
            await websocket.close(code=1011)
        except:
            pass

# Endpoint protégé pour récupérer la configuration des collecteurs
@app.get("/api/collectors/config", tags=["collectors"])
async def get_collectors_config(current_user: User = Depends(get_read_data_user)):
    """Récupère la configuration des collecteurs disponibles."""
    config = {
        "exchanges": list(EXCHANGE_COLLECTORS.keys()),
        "available_collectors": {
            "binance": ["BinanceTradeCollector"],
            "kraken": ["KrakenTradeCollector"]
        },
        "default_update_interval": 1.0,
        "metrics_enabled": True
    }
    return config

# Événements de démarrage et d'arrêt de l'application
@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage de l'application."""
    # Démarrage du gestionnaire de métriques
    await start_metrics_manager()
    await startup_metrics_manager()
    
    # Démarrage du gestionnaire d'alertes
    await startup_alert_manager()
    
    logger.info("Application démarrée")

@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage à l'arrêt de l'application."""
    # Arrêt du gestionnaire de métriques
    await stop_metrics_manager()
    await shutdown_metrics_manager()
    
    # Arrêt du gestionnaire d'alertes
    await shutdown_alert_manager()
    
    logger.info("Application arrêtée")

# Configuration du dossier static pour le frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

# Nouvelle route pour accéder aux données de trades directement
@app.get("/api/market/{exchange}/{symbol}/trades", response_model=Union[List[TradeData], ErrorResponse])
async def get_trades(
    exchange: str, 
    symbol: str, 
    limit: int = Query(20, ge=1, le=1000)
):
    """Récupère les derniers trades pour un symbole.
    
    Args:
        exchange: Nom de l'exchange (kraken, binance, etc.)
        symbol: Symbole/paire de trading
        limit: Nombre maximum de trades à récupérer
        
    Returns:
        Liste des derniers trades
    """
    try:
        collector = await get_or_create_collector(exchange, symbol)
        
        # Récupération des trades en fonction du type de collecteur
        if exchange == "binance" and hasattr(collector, "_trades"):
            trades = collector._trades[-limit:] if collector._trades else []
            return [TradeData(
                symbol=symbol,
                timestamp=trade.get("timestamp"),
                price=trade.get("price"),
                quantity=trade.get("quantity"),
                trade_id=trade.get("trade_id", ""),
                buyer_order_id=trade.get("buyer_order_id", ""),
                seller_order_id=trade.get("seller_order_id", ""),
                buyer_is_maker=trade.get("buyer_is_maker", False),
                is_best_match=trade.get("is_best_match", True),
                side=trade.get("side", "unknown")
            ) for trade in trades]
            
        elif exchange == "kraken" and hasattr(collector, "get_historical_trades"):
            kraken_trades = await collector.get_historical_trades(
                symbol=format_symbol_for_exchange(symbol, exchange),
                limit=limit
            )
            return [TradeData(
                symbol=symbol,
                timestamp=trade.get("timestamp"),
                price=trade.get("price"),
                quantity=trade.get("volume"),
                trade_id=trade.get("trade_id", ""),
                side=trade.get("side", "unknown")
            ) for trade in kraken_trades]
            
        # Collecteur non supporté
        return ErrorResponse(
            error=f"Récupération des trades non supportée pour {exchange}",
            code=400
        )
        
    except HTTPException as e:
        return ErrorResponse(error=e.detail, code=e.status_code)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des trades: {e}")
        logger.error(traceback.format_exc())
        return ErrorResponse(error=str(e), code=500)

# Nouvelle route pour accéder aux données de chandeliers
@app.get("/api/market/{exchange}/{symbol}/klines", response_model=Union[List[Dict[str, Any]], ErrorResponse])
async def get_klines(
    exchange: str, 
    symbol: str, 
    interval: str = Query("1h", description="Intervalle des chandeliers (1m, 5m, 15m, 30m, 1h, 4h, 1d)"),
    limit: int = Query(500, ge=1, le=1000),
    start_time: Optional[int] = Query(None, description="Timestamp de début en millisecondes")
):
    """Récupère les données de chandeliers (OHLCV) pour un symbole.
    
    Args:
        exchange: Nom de l'exchange (kraken, binance, etc.)
        symbol: Symbole/paire de trading (format: BTCUSDT sans '/')
        interval: Intervalle de temps pour les chandeliers
        limit: Nombre maximum de chandeliers à récupérer
        start_time: Timestamp de début en millisecondes (optionnel)
        
    Returns:
        Liste des chandeliers avec données OHLCV
    """
    try:
        # Pour cette démo, nous générons des données simulées
        # En production, connectez-vous à votre base de données TimescaleDB
        import random
        from datetime import datetime, timedelta
        
        # Conversion des intervalles en minutes
        interval_map = {
            "1m": 1, "5m": 5, "15m": 15, "30m": 30,
            "1h": 60, "4h": 240, "1d": 1440
        }
        minutes = interval_map.get(interval, 60)
        
        # Définir l'heure de fin (maintenant) et calculer l'heure de début
        end_time = datetime.now()
        if start_time:
            start_datetime = datetime.fromtimestamp(start_time / 1000)
        else:
            start_datetime = end_time - timedelta(minutes=minutes * limit)
        
        # Générer les chandeliers
        klines = []
        current_time = start_datetime
        last_close = 30000.0  # Prix de départ approximatif pour BTC
        
        while current_time <= end_time and len(klines) < limit:
            # Variation aléatoire du prix
            price_change = random.uniform(-0.005, 0.005)
            open_price = last_close
            close_price = open_price * (1 + price_change)
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.003))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.003))
            volume = random.uniform(0.5, 10.0)
            
            klines.append({
                "timestamp": int(current_time.timestamp() * 1000),
                "open": open_price,
                "high": high_price,
                "close": close_price,
                "low": low_price,
                "volume": volume
            })
            
            last_close = close_price
            current_time += timedelta(minutes=minutes)
        
        return klines
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des chandeliers: {str(e)}")
        return {"error": f"Erreur lors de la récupération des chandeliers: {str(e)}"}

# Route pour obtenir la liste des symboles disponibles
@app.get("/api/market/symbols", response_model=Union[Dict[str, List[str]], ErrorResponse])
async def get_available_symbols(exchange: str = Query("binance")):
    """Récupère la liste des symboles disponibles pour un exchange donné.
    
    Args:
        exchange: Nom de l'exchange (kraken, binance, etc.)
        
    Returns:
        Liste des symboles disponibles
    """
    try:
        # Pour cette démo, nous retournons une liste statique
        # En production, récupérez les symboles depuis votre base de données
        symbols = {
            "binance": ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT", 
                        "ADA/USDT", "AVAX/USDT", "DOGE/USDT", "MATIC/USDT", "DOT/USDT"],
            "kraken": ["BTC/USD", "ETH/USD", "XRP/USD", "ADA/USD", "SOL/USD", 
                       "DOT/USD", "DOGE/USD", "MATIC/USD", "LINK/USD", "UNI/USD"]
        }
        
        return {"success": True, "data": symbols.get(exchange, [])}
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des symboles: {str(e)}")
        return {"error": f"Erreur lors de la récupération des symboles: {str(e)}"}

# Route pour sauvegarder la configuration du graphique
@app.post("/api/user/chart-config", response_model=Dict[str, Any])
async def save_chart_configuration(
    config: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """Sauvegarde la configuration du graphique pour l'utilisateur.
    
    Args:
        config: Configuration du graphique (exchange, symbol, timeframe, indicateurs, etc.)
        current_user: Utilisateur authentifié
        
    Returns:
        Statut de la sauvegarde
    """
    try:
        # En production, sauvegardez dans votre base de données
        logger.info(f"Configuration sauvegardée pour {current_user.username}: {config}")
        
        return {
            "success": True,
            "message": "Configuration sauvegardée avec succès",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de la configuration: {str(e)}")
        return {
            "success": False,
            "error": f"Erreur lors de la sauvegarde: {str(e)}"
        }

# Routes pour les alertes
@app.get("/api/alerts", response_model=AlertsResponse)
async def get_alerts():
    """Récupère la liste des alertes."""
    try:
        # TODO: Implémenter la récupération depuis la base de données
        return AlertsResponse(success=True, data=[])
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des alertes: {e}")
        return AlertsResponse(success=False, error="Erreur lors de la récupération des alertes")

@app.post("/api/alerts", response_model=AlertResponse)
async def create_alert(alert: Alert):
    """Crée une nouvelle alerte."""
    try:
        # TODO: Implémenter la création dans la base de données
        alert.id = "temp_id"  # À remplacer par un vrai ID
        alert.created_at = int(datetime.now().timestamp() * 1000)
        return AlertResponse(success=True, data=alert)
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'alerte: {e}")
        return AlertResponse(success=False, error="Erreur lors de la création de l'alerte")

@app.delete("/api/alerts/{alert_id}", response_model=AlertResponse)
async def delete_alert(alert_id: str):
    """Supprime une alerte."""
    try:
        # TODO: Implémenter la suppression depuis la base de données
        return AlertResponse(success=True)
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de l'alerte: {e}")
        return AlertResponse(success=False, error="Erreur lors de la suppression de l'alerte")

def format_symbol_for_exchange(symbol: str, exchange: str) -> str:
    """Formate un symbole selon les conventions de l'exchange.
    
    Args:
        symbol: Symbole à formater
        exchange: Nom de l'exchange
        
    Returns:
        Symbole formaté
    """
    # Format standardisé: BTCUSD, ETHEUR, etc.
    if exchange == "kraken":
        # Kraken utilise XBT pour Bitcoin et des paires avec /
        if symbol.startswith("BTC"):
            formatted = "XBT" + symbol[3:]
        else:
            formatted = symbol
        return f"{formatted[:3]}/{formatted[3:]}"
    elif exchange == "binance":
        # Binance utilise des paires sans séparateur
        return symbol
    else:
        return symbol

async def get_or_create_collector(exchange: str, symbol: str) -> Union[KrakenTradeCollector, BinanceTradeCollector]:
    """Récupère ou crée un collecteur pour l'exchange et le symbole spécifiés.
    
    Args:
        exchange: Nom de l'exchange (kraken, binance, etc.)
        symbol: Symbole/paire de trading
        
    Returns:
        Collecteur initialisé
        
    Raises:
        HTTPException: Si l'exchange n'est pas supporté
    """
    # Validation de l'exchange
    exchange = exchange.lower()
    if exchange not in EXCHANGE_COLLECTORS:
        raise HTTPException(status_code=400, detail=f"Exchange non supporté: {exchange}")
        
    # Conversion du format du symbole selon l'exchange
    exchange_symbol = format_symbol_for_exchange(symbol, exchange)
    
    # Création ou récupération du collecteur
    collector_key = f"{exchange}:{exchange_symbol}"
    
    if collector_key in collectors and collectors[collector_key] is not None:
        # Mise à jour du timestamp de dernière utilisation
        collector_last_used[collector_key] = time.time()
        return collectors[collector_key]
    
    try:
        # Récupération des clés API depuis les variables d'environnement
        api_key = os.getenv(f"{exchange.upper()}_API_KEY")
        api_secret = os.getenv(f"{exchange.upper()}_API_SECRET")
        
        # Création du collecteur avec la configuration appropriée
        collector_class = EXCHANGE_COLLECTORS[exchange]
        
        if exchange == "kraken":
            collector = collector_class(
                name=f"collector_{exchange}_{exchange_symbol}",
                symbols=[exchange_symbol],
                api_key=api_key,
                api_secret=api_secret,
                max_retries=3,
                retry_delay=5,
                update_interval=1.0
            )
        elif exchange == "binance":
            collector = collector_class(
                symbol=exchange_symbol,
                api_key=api_key,
                api_secret=api_secret,
                max_retries=3,
                retry_delay=5
            )
        else:
            # Ne devrait jamais arriver grâce à la validation précédente
            raise HTTPException(status_code=400, detail=f"Exchange non supporté: {exchange}")
        
        collectors[collector_key] = collector
        collector_last_used[collector_key] = time.time()
        
        # Démarrage du collecteur
        await collector.start()
        logger.info(f"Collecteur créé et démarré pour {exchange}:{exchange_symbol}")
        
        return collector
        
    except Exception as e:
        error_message = f"Erreur lors de la création du collecteur pour {exchange}:{symbol}: {str(e)}"
        logger.error(error_message)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_message) 