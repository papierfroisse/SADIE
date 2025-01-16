"""Exemple d'utilisation du système de streaming."""

import asyncio
import logging
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from prometheus_client import start_http_server

from SADIE.core.streaming import StreamEvent, StreamManager
from SADIE.core.streaming.processors import (
    FilterProcessor,
    TransformProcessor,
    ValidationProcessor,
    ThrottleProcessor
)
from SADIE.core.streaming.handlers import (
    LoggingHandler,
    CacheHandler,
    DatabaseHandler,
    AlertHandler
)
from SADIE.core.cache import Cache, RedisCache
from SADIE.core.models.events import MarketEvent
from SADIE.core.monitoring.metrics import MetricsHandler
from SADIE.core.analytics.queries import TimeScaleQueries

# Chargement des variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Schéma de validation pour les données de marché
MARKET_DATA_SCHEMA = {
    "type": "object",
    "properties": {
        "symbol": {"type": "string"},
        "price": {"type": "number"},
        "volume": {"type": "number"},
        "side": {"type": "string"},
        "exchange": {"type": "string"}
    },
    "required": ["symbol", "price", "volume", "side", "exchange"]
}

async def print_market_stats(queries: TimeScaleQueries, symbol: str):
    """Affiche les statistiques de marché en temps réel."""
    while True:
        stats = await queries.get_market_stats(symbol)
        logger.info(f"Stats pour {symbol}:")
        logger.info(f"  Prix: {stats.get('open_price')} -> {stats.get('close_price')}")
        logger.info(f"  Volume: Buy={stats.get('buy_volume')}, Sell={stats.get('sell_volume')}")
        await asyncio.sleep(5)

async def main():
    """Exemple principal."""
    # Démarrage du serveur de métriques Prometheus
    start_http_server(8000)
    
    # Initialisation des métriques
    metrics = MetricsHandler(
        push_gateway=os.getenv("PROMETHEUS_PUSHGATEWAY"),
        job_name="sadie_example"
    )
    
    # Initialisation du cache Redis
    cache = Cache(RedisCache(
        url=os.getenv("REDIS_URL", "redis://localhost"),
        prefix="stream:"
    ))
    
    # Création du gestionnaire de flux
    stream_manager = StreamManager()
    
    # Configuration des processeurs
    # 1. Filtre les prix > 1000
    price_filter = FilterProcessor(
        lambda e: e.data["price"] > 1000
    )
    
    # 2. Transforme les données (ajoute le timestamp unix)
    def add_timestamp(data):
        return {**data, "timestamp_unix": datetime.utcnow().timestamp()}
    
    transformer = TransformProcessor(add_timestamp)
    
    # 3. Valide le format des données
    validator = ValidationProcessor(MARKET_DATA_SCHEMA)
    
    # 4. Limite le débit (max 100 événements par seconde)
    throttler = ThrottleProcessor(max_events=100, window_seconds=1.0)
    
    # Ajout des processeurs au stream
    for processor in [validator, price_filter, transformer, throttler]:
        stream_manager.add_processor("market_data", processor)
    
    # Configuration des handlers
    # 1. Logging des événements
    stream_manager.subscribe(
        "market_data",
        LoggingHandler(level=logging.INFO)
    )
    
    # 2. Mise en cache des événements
    stream_manager.subscribe(
        "market_data",
        CacheHandler(
            cache=cache,
            ttl=timedelta(minutes=5)
        )
    )
    
    # 3. Persistence en base de données
    db_handler = DatabaseHandler(
        database_url=os.getenv("DATABASE_URL"),
        event_model=MarketEvent,
        batch_size=50,
        metrics_handler=metrics
    )
    
    stream_manager.subscribe("market_data", db_handler)
    
    # 4. Alertes sur les gros volumes
    def volume_alert(event):
        logger.warning(f"ALERTE: Gros volume détecté! {event.data}")
    
    stream_manager.subscribe(
        "market_data",
        AlertHandler(
            condition=lambda e: e.data["volume"] > 100,
            alert_func=volume_alert
        )
    )
    
    # Création de la session pour les requêtes
    engine = create_async_engine(os.getenv("DATABASE_URL"))
    async_session = sessionmaker(engine, class_=AsyncSession)()
    queries = TimeScaleQueries(async_session)
    
    # Démarrage du stream manager et des statistiques
    async with stream_manager, db_handler:
        # Tâche d'affichage des stats
        stats_task = asyncio.create_task(
            print_market_stats(queries, "BTC/USD")
        )
        
        try:
            # Simulation de données de marché
            exchanges = ["binance", "kraken", "coinbase"]
            symbols = ["BTC/USD", "ETH/USD", "SOL/USD"]
            
            for i in range(100):
                exchange = exchanges[i % len(exchanges)]
                symbol = symbols[i % len(symbols)]
                side = "buy" if i % 2 == 0 else "sell"
                
                event = StreamEvent(
                    topic="market_data",
                    data={
                        "symbol": symbol,
                        "price": 1000 + i * 100,
                        "volume": 50 + i * 10,
                        "side": side,
                        "exchange": exchange
                    }
                )
                await stream_manager.publish(event)
                await asyncio.sleep(0.1)
                
            # Attente pour voir les statistiques
            await asyncio.sleep(10)
            
        finally:
            # Nettoyage
            stats_task.cancel()
            await async_session.close()
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main()) 