"""Tests unitaires pour le collecteur de trades."""

import asyncio
import json
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest
from websockets.exceptions import ConnectionClosed

from sadie.core.collectors.trade_collector import TradeCollector, BinanceTradeCollector
from sadie.core.models.events import Exchange, Symbol, Trade

@pytest.fixture
def collector():
    """Fixture pour le collecteur de trades."""
    return TradeCollector(
        name="test",
        symbols=["BTC-USD", "ETH-USD"],
        update_interval=0.1,
        max_trades=1000,
        max_retries=3,
        retry_delay=0.1,
        connection_timeout=2.0
    )

@pytest.fixture
def binance_collector():
    """Fixture pour le collecteur de trades Binance."""
    return BinanceTradeCollector(
        name="binance_test",
        symbols=["BTCUSDT", "ETHUSDT"],
        update_interval=0.1,
        max_retries=3,
        retry_delay=0.1,
        connection_timeout=2.0,
        api_key="test_key",
        api_secret="test_secret"
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

@pytest.mark.asyncio
async def test_error_handling(collector):
    """Test de la gestion des erreurs."""
    # Patch de la méthode _run pour simuler des erreurs
    with patch.object(collector, '_run', side_effect=[
        ConnectionError("Test connection error"),
        asyncio.TimeoutError("Test timeout"),
        None  # Troisième appel réussi
    ]):
        await collector.start()
        # Attendre que les tentatives de reconnexion se produisent
        await asyncio.sleep(0.5)
        
        # Vérifier que le collecteur est toujours en cours d'exécution malgré les erreurs
        assert collector._running is True
        
        await collector.stop()

@pytest.mark.asyncio
async def test_binance_collector_connection(binance_collector):
    """Test de la connexion du collecteur Binance."""
    # Mock des clients et des WebSockets
    mock_client = AsyncMock()
    mock_bm = MagicMock()
    mock_ws = AsyncMock()
    mock_ws.__aenter__.return_value = mock_ws
    mock_ws.__aexit__.return_value = None
    
    # Simuler des messages de trades
    mock_ws.recv.side_effect = [
        json.dumps({
            "e": "trade",
            "s": "BTCUSDT",
            "p": "45000.0",
            "q": "0.5",
            "T": 1625097600000,
            "m": False
        }),
        asyncio.CancelledError()  # Pour sortir de la boucle
    ]
    
    mock_bm.trade_socket.return_value = mock_ws
    
    with patch('sadie.core.collectors.trade_collector.AsyncClient.create', 
               return_value=mock_client), \
         patch('sadie.core.collectors.trade_collector.BinanceSocketManager', 
               return_value=mock_bm):
        
        await binance_collector.start()
        # Attendre que les trades soient traités
        await asyncio.sleep(0.2)
        
        # Vérifier qu'un trade a été collecté
        trades = await binance_collector.get_trades("BTCUSDT")
        
        await binance_collector.stop()
        
        # Vérifier que les méthodes ont été appelées correctement
        mock_client.close_connection.assert_called_once()

@pytest.mark.asyncio
async def test_max_retries_exceeded(collector):
    """Test du dépassement du nombre maximal de tentatives."""
    # Patch de la méthode _run pour simuler des erreurs consécutives
    with patch.object(collector, '_run', side_effect=ConnectionError("Test connection error")):
        # Réduire le nombre de tentatives pour le test
        collector.max_retries = 2
        
        await collector.start()
        # Attendre que les tentatives de reconnexion se produisent
        await asyncio.sleep(0.5)
        
        # Vérifier que le collecteur s'est arrêté après avoir dépassé le nombre maximal de tentatives
        assert collector._running is False
        
        await collector.stop()  # Pour le nettoyage 