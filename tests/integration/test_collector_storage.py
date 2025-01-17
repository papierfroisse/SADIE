"""Tests d'intégration pour le stockage des données des collecteurs."""

import asyncio
from datetime import datetime
from typing import List

import pytest

from sadie.core.models.events import Trade
from sadie.data.collectors.binance import BinanceTradeCollector
from sadie.storage.redis import RedisStorage
from sadie.storage.timescale import TimescaleStorage

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
async def timescale_storage():
    """Fixture pour le stockage TimescaleDB."""
    storage = TimescaleStorage(
        name="test_timescale",
        dsn="postgresql://postgres:postgres@localhost:5432/sadie_test"
    )
    await storage.connect()
    yield storage
    await storage.disconnect()

@pytest.fixture
async def binance_collector(redis_storage: RedisStorage, timescale_storage: TimescaleStorage):
    """Fixture pour le collecteur Binance."""
    collector = BinanceTradeCollector(
        name="test_binance",
        symbols=["BTC/USDT", "ETH/USDT"],
        storage=redis_storage  # On utilise Redis pour les données en temps réel
    )
    await collector.start()
    yield collector
    await collector.stop()

async def test_collector_redis_storage(binance_collector: BinanceTradeCollector, redis_storage: RedisStorage):
    """Teste le stockage Redis avec le collecteur."""
    # Attend quelques trades
    await asyncio.sleep(5)
    
    # Vérifie les données en temps réel dans Redis
    for symbol in binance_collector.symbols:
        # Vérifie les trades
        trades = await redis_storage.get_trades(symbol)
        assert len(trades) > 0
        for trade in trades:
            assert isinstance(trade, Trade)
            assert trade.symbol == symbol
            assert trade.exchange == "binance"
            assert trade.price > 0
            assert trade.amount > 0
            assert trade.timestamp > 0
            assert trade.side in ["buy", "sell"]
            assert trade.trade_id is not None
        
        # Vérifie les statistiques
        stats = await redis_storage.get_statistics(symbol)
        assert stats["price"] > 0
        assert stats["volume"] >= 0
        assert stats["trades"] > 0
        assert stats["high"] >= stats["price"]
        assert stats["low"] <= stats["price"]
        assert stats["vwap"] > 0
        assert stats["total_volume"] >= 0

async def test_collector_timescale_storage(binance_collector: BinanceTradeCollector, timescale_storage: TimescaleStorage):
    """Teste le stockage TimescaleDB avec le collecteur."""
    # Change le stockage pour TimescaleDB
    binance_collector.storage = timescale_storage
    
    # Attend quelques trades
    await asyncio.sleep(5)
    
    # Vérifie les données historiques dans TimescaleDB
    for symbol in binance_collector.symbols:
        # Vérifie les trades
        trades = await timescale_storage.get_trades(symbol)
        assert len(trades) > 0
        for trade in trades:
            assert isinstance(trade, Trade)
            assert trade.symbol == symbol
            assert trade.exchange == "binance"
            assert trade.price > 0
            assert trade.amount > 0
            assert trade.timestamp > 0
            assert trade.side in ["buy", "sell"]
            assert trade.trade_id is not None
        
        # Vérifie les statistiques
        stats = await timescale_storage.get_statistics(symbol)
        assert stats["price"] > 0
        assert stats["volume"] >= 0
        assert stats["trades"] > 0
        assert stats["high"] >= stats["price"]
        assert stats["low"] <= stats["price"]
        assert stats["vwap"] > 0
        assert stats["total_volume"] >= 0

async def test_collector_dual_storage(
    binance_collector: BinanceTradeCollector,
    redis_storage: RedisStorage,
    timescale_storage: TimescaleStorage
):
    """Teste l'utilisation simultanée des deux stockages."""
    # Configure le collecteur pour utiliser les deux stockages
    binance_collector.storage = redis_storage
    
    # Attend quelques trades
    await asyncio.sleep(5)
    
    # Vérifie que les données sont présentes dans Redis
    for symbol in binance_collector.symbols:
        redis_trades = await redis_storage.get_trades(symbol)
        assert len(redis_trades) > 0
        
        redis_stats = await redis_storage.get_statistics(symbol)
        assert redis_stats["price"] > 0
    
    # Change pour TimescaleDB
    binance_collector.storage = timescale_storage
    
    # Attend quelques trades supplémentaires
    await asyncio.sleep(5)
    
    # Vérifie que les données sont présentes dans TimescaleDB
    for symbol in binance_collector.symbols:
        timescale_trades = await timescale_storage.get_trades(symbol)
        assert len(timescale_trades) > 0
        
        timescale_stats = await timescale_storage.get_statistics(symbol)
        assert timescale_stats["price"] > 0
        
        # Compare les données entre Redis et TimescaleDB
        assert abs(redis_stats["price"] - timescale_stats["price"]) < 1000  # Prix similaires
        assert redis_stats["trades"] <= timescale_stats["trades"]  # Plus de trades dans TimescaleDB 