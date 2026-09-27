"""Tests unitaires pour le stockage TimescaleDB."""

import json
from datetime import datetime
from typing import List

import pytest
import asyncpg
from asyncpg.pool import Pool

from sadie.core.models.events import Trade
from sadie.storage.timescale import TimescaleStorage

@pytest.fixture
async def timescale_storage():
    """Fixture pour le stockage TimescaleDB."""
    storage = TimescaleStorage(
        name="test",
        dsn="postgresql://postgres:postgres@localhost:5432/sadie_test"
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

async def test_connect_disconnect(timescale_storage: TimescaleStorage):
    """Teste la connexion et déconnexion."""
    assert isinstance(timescale_storage._pool, Pool)
    await timescale_storage.disconnect()
    assert timescale_storage._pool is None

async def test_store_trades(timescale_storage: TimescaleStorage, trades: List[Trade]):
    """Teste le stockage des trades."""
    symbol = "BTC/USDT"
    await timescale_storage.store_trades(symbol, trades)
    
    # Vérifie que les trades sont stockés
    async with timescale_storage._pool.acquire() as conn:
        rows = await conn.fetch('''
            SELECT * FROM trades 
            WHERE symbol = $1 
            ORDER BY timestamp DESC
        ''', symbol)
        
    assert len(rows) == len(trades)
    assert rows[0]["exchange"] == trades[0].exchange
    assert rows[0]["symbol"] == trades[0].symbol
    assert float(rows[0]["price"]) == trades[0].price
    assert float(rows[0]["amount"]) == trades[0].amount
    assert rows[0]["side"] == trades[0].side
    assert rows[0]["trade_id"] == trades[0].trade_id

async def test_get_trades(timescale_storage: TimescaleStorage, trades: List[Trade]):
    """Teste la récupération des trades."""
    symbol = "BTC/USDT"
    await timescale_storage.store_trades(symbol, trades)
    
    # Récupère tous les trades
    stored = await timescale_storage.get_trades(symbol)
    assert len(stored) == len(trades)
    assert isinstance(stored[0], Trade)
    assert stored[0].exchange == trades[0].exchange
    assert stored[0].symbol == trades[0].symbol
    assert stored[0].price == trades[0].price
    assert stored[0].amount == trades[0].amount
    assert stored[0].side == trades[0].side
    assert stored[0].trade_id == trades[0].trade_id
    
    # Teste la limitation
    limited = await timescale_storage.get_trades(symbol, limit=1)
    assert len(limited) == 1
    
    # Teste le filtrage par timestamp
    now = datetime.now().timestamp()
    filtered = await timescale_storage.get_trades(
        symbol,
        start_time=now - 3600,
        end_time=now + 3600
    )
    assert len(filtered) == len(trades)

async def test_store_statistics(timescale_storage: TimescaleStorage):
    """Teste le stockage des statistiques."""
    symbol = "BTC/USDT"
    stats = {
        "price": 50000.0,
        "volume": 100.0,
        "trades": 50
    }
    
    await timescale_storage.store_statistics(symbol, stats)
    
    # Vérifie que les stats sont stockées
    async with timescale_storage._pool.acquire() as conn:
        row = await conn.fetchrow('''
            SELECT * FROM statistics 
            WHERE symbol = $1 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', symbol)
        
    assert row is not None
    assert row["data"] == stats

async def test_get_statistics(timescale_storage: TimescaleStorage):
    """Teste la récupération des statistiques."""
    symbol = "BTC/USDT"
    stats = {
        "price": 50000.0,
        "volume": 100.0,
        "trades": 50
    }
    
    await timescale_storage.store_statistics(symbol, stats)
    
    # Récupère les stats
    stored = await timescale_storage.get_statistics(symbol)
    assert stored == stats
    
    # Teste avec un symbole inexistant
    empty = await timescale_storage.get_statistics("UNKNOWN")
    assert empty == {} 