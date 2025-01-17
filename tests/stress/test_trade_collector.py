"""Tests de base du collecteur de transactions."""

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
    symbols = [Symbol.BTC_USDT.value]  # Un seul symbole pour simplifier
    collector = TradeCollector(
        name="test",
        symbols=symbols,
        max_trades_per_symbol=1000,
        connection_pool_size=1,
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
        "price": "50000.0",
        "amount": "1.0",
        "side": "buy",
        "timestamp": timestamp.isoformat()
    }

@pytest.mark.asyncio
async def test_basic_trade_processing(collector):
    """Test simple du traitement d'un trade."""
    logger.info("Démarrage du test de traitement basique")
    
    # Génération d'un seul trade
    symbol = Symbol.BTC_USDT.value
    trade = generate_trade(symbol, 1)
    
    # Traitement du trade
    logger.info("Traitement du trade")
    await collector.process_trade(symbol, trade)
    
    # Vérification
    trades = collector.get_trades(symbol)
    assert len(trades) == 1
    assert trades[0]["trade_id"] == "1"
    logger.info("Test terminé avec succès") 