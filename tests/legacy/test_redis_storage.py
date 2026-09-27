"""Tests unitaires pour le stockage Redis."""

import json
from datetime import datetime
from typing import List

import pytest
import redis.asyncio as redis
from redis.asyncio.client import Redis

from sadie.core.models.events import Trade
from sadie.storage.redis import RedisStorage

@pytest.fixture
async def redis_storage():
    """Fixture pour le stockage Redis."""
    storage = RedisStorage(
        name="test",
        host="localhost",
        port=6379,
        db=0,
        max_trades=100
    )
    await storage.connect()
    yield storage
    await storage.disconnect()

@pytest.fixture
def trades() -> List[Trade]:
    """Fixture pour une liste de trades."""
    return [
        Trade(
            exchange="binance",
            symbol="BTC/USDT",
            price=50000.0,
            amount=1.0,
            timestamp=datetime.now().timestamp(),
            side="buy",
            trade_id="1"
        ),
        Trade(
            exchange="binance", 
            symbol="BTC/USDT",
            price=50100.0,
            amount=0.5,
            timestamp=datetime.now().timestamp(),
            side="sell",
            trade_id="2"
        )
    ]

async def test_connect_disconnect(redis_storage: RedisStorage):
    """Teste la connexion et déconnexion."""
    assert isinstance(redis_storage._redis, Redis)
    await redis_storage.disconnect()
    assert redis_storage._redis is None

async def test_store_trades(redis_storage: RedisStorage, trades: List[Trade]):
    """Teste le stockage des trades."""
    symbol = "BTC/USDT"
    await redis_storage.store_trades(symbol, trades)
    
    # Vérifie que les trades sont stockés
    key = f"trades:{symbol}"
    stored = await redis_storage._redis.lrange(key, 0, -1)
    assert len(stored) == len(trades)
    
    # Vérifie le contenu
    trade_data = json.loads(stored[0])
    assert trade_data["exchange"] == trades[0].exchange
    assert trade_data["symbol"] == trades[0].symbol
    assert trade_data["price"] == trades[0].price
    assert trade_data["amount"] == trades[0].amount
    assert trade_data["side"] == trades[0].side
    assert trade_data["trade_id"] == trades[0].trade_id

async def test_get_trades(redis_storage: RedisStorage, trades: List[Trade]):
    """Teste la récupération des trades."""
    symbol = "BTC/USDT"
    await redis_storage.store_trades(symbol, trades)
    
    # Récupère tous les trades
    stored = await redis_storage.get_trades(symbol)
    assert len(stored) == len(trades)
    assert isinstance(stored[0], Trade)
    assert stored[0].exchange == trades[0].exchange
    assert stored[0].symbol == trades[0].symbol
    assert stored[0].price == trades[0].price
    assert stored[0].amount == trades[0].amount
    assert stored[0].side == trades[0].side
    assert stored[0].trade_id == trades[0].trade_id
    
    # Teste la limitation
    limited = await redis_storage.get_trades(symbol, limit=1)
    assert len(limited) == 1
    
    # Teste le filtrage par timestamp
    now = datetime.now().timestamp()
    filtered = await redis_storage.get_trades(
        symbol,
        start_time=now - 3600,
        end_time=now + 3600
    )
    assert len(filtered) == len(trades)

async def test_store_statistics(redis_storage: RedisStorage):
    """Teste le stockage des statistiques."""
    symbol = "BTC/USDT"
    stats = {
        "price": 50000.0,
        "volume": 100.0,
        "trades": 50
    }
    
    await redis_storage.store_statistics(symbol, stats)
    
    # Vérifie que les stats sont stockées
    key = f"stats:{symbol}"
    stored = await redis_storage._redis.get(key)
    assert stored is not None
    
    # Vérifie le contenu
    stored_stats = json.loads(stored)
    assert stored_stats == stats

async def test_get_statistics(redis_storage: RedisStorage):
    """Teste la récupération des statistiques."""
    symbol = "BTC/USDT"
    stats = {
        "price": 50000.0,
        "volume": 100.0,
        "trades": 50
    }
    
    await redis_storage.store_statistics(symbol, stats)
    
    # Récupère les stats
    stored = await redis_storage.get_statistics(symbol)
    assert stored == stats
    
    # Teste avec un symbole inexistant
    empty = await redis_storage.get_statistics("UNKNOWN")
    assert empty == {} 