"""Tests unitaires pour le collecteur de trades."""

import asyncio
import json
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from websockets.exceptions import ConnectionClosed

from sadie.core.collectors.trade_collector import TradeCollector
from sadie.core.models.events import Exchange, Symbol, Trade

@pytest.fixture
def collector():
    """Fixture pour le collecteur de trades."""
    return TradeCollector(
        name="test",
        symbols=["BTC-USD", "ETH-USD"],
        update_interval=0.1,
        max_trades=1000
    )

@pytest.mark.asyncio
async def test_start_stop(collector):
    """Test du démarrage et de l'arrêt du collecteur."""
    await collector.start()
    assert collector._running is True
    assert collector._task is not None
    
    await collector.stop()
    assert collector._running is False
    assert collector._task is None

@pytest.mark.asyncio
async def test_collect(collector):
    """Test de la collecte des trades."""
    await collector.start()
    
    # Attente de quelques mises à jour
    await asyncio.sleep(0.3)
    
    # Collecte des données
    data = await collector.collect()
    
    # Vérification des données
    assert isinstance(data, dict)
    assert "BTC-USD" in data
    assert "ETH-USD" in data
    
    for symbol in ["BTC-USD", "ETH-USD"]:
        assert "trades" in data[symbol]
        assert "statistics" in data[symbol]
        assert isinstance(data[symbol]["trades"], list)
        assert isinstance(data[symbol]["statistics"], dict)
        
        stats = data[symbol]["statistics"]
        assert "count" in stats
        assert "volume" in stats
        assert "value" in stats
        assert "price" in stats
    
    await collector.stop() 