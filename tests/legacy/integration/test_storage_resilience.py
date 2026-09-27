"""Tests d'intégration pour la résilience du stockage."""

import asyncio
from datetime import datetime
from typing import List

import pytest
import redis.asyncio as redis
from redis.exceptions import ConnectionError

from sadie.core.models.events import Trade
from sadie.data.collectors.binance import BinanceTradeCollector
from sadie.storage.redis import RedisStorage

@pytest.fixture
async def redis_storage():
    """Fixture pour le stockage Redis."""
    storage = RedisStorage(
        name="test_redis",
        host="localhost",
        port=6379,
        db=0,
        max_trades=100
    )
    await storage.connect()
    yield storage
    await storage.disconnect()

@pytest.fixture
async def binance_collector(redis_storage: RedisStorage):
    """Fixture pour le collecteur Binance."""
    collector = BinanceTradeCollector(
        name="test_binance",
        symbols=["BTC/USDT"],
        storage=redis_storage
    )
    await collector.start()
    yield collector
    await collector.stop()

async def test_storage_reconnection(binance_collector: BinanceTradeCollector, redis_storage: RedisStorage):
    """Teste la reconnexion au stockage."""
    # Attend quelques trades initiaux
    await asyncio.sleep(5)
    
    # Vérifie les données initiales
    trades_before = await redis_storage.get_trades("BTC/USDT")
    stats_before = await redis_storage.get_statistics("BTC/USDT")
    assert len(trades_before) > 0
    assert stats_before["price"] > 0
    
    # Simule une perte de connexion en fermant la connexion Redis
    await redis_storage.disconnect()
    
    # Attend un peu pour simuler la déconnexion
    await asyncio.sleep(2)
    
    # Tente de stocker des données pendant la déconnexion
    try:
        await redis_storage.store_trades("BTC/USDT", trades_before)
        assert False, "Devrait lever une exception"
    except RuntimeError:
        pass
    
    # Reconnecte le stockage
    await redis_storage.connect()
    
    # Attend de nouveaux trades
    await asyncio.sleep(5)
    
    # Vérifie que les nouvelles données sont stockées
    trades_after = await redis_storage.get_trades("BTC/USDT")
    stats_after = await redis_storage.get_statistics("BTC/USDT")
    assert len(trades_after) > 0
    assert stats_after["price"] > 0
    
    # Vérifie que les données sont cohérentes
    assert abs(stats_before["price"] - stats_after["price"]) < 1000  # Prix similaires
    assert stats_before["trades"] <= stats_after["trades"]  # Plus de trades après

async def test_collector_storage_resilience(binance_collector: BinanceTradeCollector, redis_storage: RedisStorage):
    """Teste la résilience du collecteur face aux problèmes de stockage."""
    # Attend quelques trades initiaux
    await asyncio.sleep(5)
    
    # Vérifie les données initiales
    trades_before = await redis_storage.get_trades("BTC/USDT")
    stats_before = await redis_storage.get_statistics("BTC/USDT")
    assert len(trades_before) > 0
    assert stats_before["price"] > 0
    
    # Simule une perte de connexion
    await redis_storage.disconnect()
    
    # Attend pendant la déconnexion
    await asyncio.sleep(5)
    
    # Le collecteur devrait continuer à fonctionner malgré l'erreur de stockage
    assert binance_collector._running
    
    # Reconnecte le stockage
    await redis_storage.connect()
    
    # Attend de nouveaux trades
    await asyncio.sleep(5)
    
    # Vérifie que les nouvelles données sont stockées
    trades_after = await redis_storage.get_trades("BTC/USDT")
    stats_after = await redis_storage.get_statistics("BTC/USDT")
    assert len(trades_after) > 0
    assert stats_after["price"] > 0
    
    # Les données en mémoire du collecteur devraient être à jour
    collector_data = binance_collector.collect("BTC/USDT")
    assert collector_data["price"] > 0
    assert collector_data["trades"] > 0
    
    # Vérifie que les statistiques sont cohérentes
    assert abs(stats_after["price"] - collector_data["price"]) < 100  # Prix similaires
    assert abs(stats_after["trades"] - collector_data["trades"]) < 10  # Nombre de trades similaire

async def test_storage_data_integrity(binance_collector: BinanceTradeCollector, redis_storage: RedisStorage):
    """Teste l'intégrité des données stockées."""
    symbol = "BTC/USDT"
    
    # Attend quelques trades
    await asyncio.sleep(5)
    
    # Récupère les trades et statistiques
    trades = await redis_storage.get_trades(symbol)
    stats = await redis_storage.get_statistics(symbol)
    
    # Vérifie l'intégrité des trades
    assert len(trades) > 0
    for trade in trades:
        # Vérifie le format des données
        assert isinstance(trade.price, float)
        assert isinstance(trade.amount, float)
        assert isinstance(trade.timestamp, float)
        assert isinstance(trade.side, str)
        assert isinstance(trade.trade_id, str)
        
        # Vérifie les contraintes métier
        assert trade.price > 0
        assert trade.amount > 0
        assert trade.timestamp > 0
        assert trade.side in ["buy", "sell"]
        
        # Vérifie l'unicité des IDs
        trade_ids = [t.trade_id for t in trades]
        assert len(trade_ids) == len(set(trade_ids))
    
    # Vérifie l'intégrité des statistiques
    assert isinstance(stats["price"], float)
    assert isinstance(stats["volume"], float)
    assert isinstance(stats["trades"], int)
    assert isinstance(stats["high"], float)
    assert isinstance(stats["low"], float)
    assert isinstance(stats["vwap"], float)
    assert isinstance(stats["total_volume"], float)
    
    # Vérifie les contraintes métier des statistiques
    assert stats["price"] > 0
    assert stats["volume"] >= 0
    assert stats["trades"] >= 0
    assert stats["high"] >= stats["price"]
    assert stats["low"] <= stats["price"]
    assert stats["vwap"] > 0
    assert stats["total_volume"] >= 0 