"""Tests de performance du collecteur de transactions."""

import asyncio
import pytest
import time
import random
from datetime import datetime, timedelta
import logging
from unittest.mock import patch, MagicMock, AsyncMock

from SADIE.core.collectors.trade_collector import TradeCollector
from SADIE.core.models.events import Exchange, Symbol, Timeframe

logger = logging.getLogger(__name__)

@pytest.fixture
def collector():
    """Fixture du collecteur de transactions."""
    symbols = [Symbol.BTC_USDT.value, Symbol.ETH_USDT.value]
    collector = TradeCollector(
        name="perf_test",
        symbols=symbols,
        max_trades_per_symbol=10000,
        connection_pool_size=2,
        cache_enabled=False
    )
    return collector

def generate_trade(symbol: str, trade_id: int, timestamp=None):
    """Génère une transaction de test."""
    if timestamp is None:
        timestamp = datetime.now()
    return {
        "trade_id": str(trade_id),
        "symbol": symbol,
        "price": str(random.uniform(100, 100000)),
        "amount": str(random.uniform(0.001, 10.0)),
        "side": "buy" if random.random() > 0.5 else "sell",
        "timestamp": timestamp.isoformat()
    }

@pytest.mark.performance
@pytest.mark.asyncio
async def test_burst_processing():
    """Test de traitement en rafale."""
    logger.info("Démarrage du test de traitement en rafale")
    
    # Configuration
    burst_size = 1000
    symbol = Symbol.BTC_USDT.value
    collector = TradeCollector(
        name="burst_test",
        symbols=[symbol],
        max_trades_per_symbol=burst_size,
        connection_pool_size=1,
        cache_enabled=False
    )
    
    # Génération des trades
    trades = []
    base_time = datetime.now()
    
    for i in range(burst_size):
        timestamp = base_time + timedelta(milliseconds=i)
        trade = generate_trade(symbol, i, timestamp)
        trades.append(trade)
    
    logger.info(f"Génération de {burst_size} trades terminée")
    
    # Traitement par lots
    start_time = time.time()
    batch_size = 50
    
    for i in range(0, len(trades), batch_size):
        batch = trades[i:i + batch_size]
        tasks = [
            collector.process_trade(trade["symbol"], trade)
            for trade in batch
        ]
        await asyncio.gather(*tasks)
        
        if i % 200 == 0:
            logger.info(f"Progression : {i}/{burst_size} trades traités")
    
    total_time = time.time() - start_time
    trades_per_second = burst_size / total_time
    
    logger.info(
        f"Performance du traitement en rafale :\n"
        f"- {burst_size} trades traités\n"
        f"- Temps total : {total_time:.2f} secondes\n"
        f"- Débit : {trades_per_second:.2f} trades/seconde"
    )
    
    # Vérifications
    stored_trades = collector.get_trades(symbol)
    assert len(stored_trades) == burst_size, \
        f"Nombre incorrect de trades stockés : {len(stored_trades)} != {burst_size}"
    
    # Vérification de l'ordre chronologique
    timestamps = [
        datetime.fromisoformat(trade["timestamp"])
        for trade in stored_trades
    ]
    assert all(t1 <= t2 for t1, t2 in zip(timestamps, timestamps[1:])), \
        "Les trades ne sont pas dans l'ordre chronologique"
    
    logger.info("Test de performance terminé avec succès") 